# Code written by Corentin Bel with the help of Marine Vernet, Samuel Garcia, Emmanuel Maby and Fayed Rassoulou

# -------------------- Imports -------------------------- #
# Pyacq imports
from pyacq.core import Node
from pyacq.core.stream import InputStream
from pyqtgraph.Qt import QtCore

# General imports
import os
import time
from pyqtgraph.util.mutex import Mutex
from joblib import load
import mne
from mne.io import read_raw_ctf
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
import pandas as pd
import psychopy as psy

# Make sure you have the fieldtrip.py file in your current folder ! 
try:
    import FieldTrip
    HAVE_FIELDTRIP = True
except ImportError:
    HAVE_FIELDTRIP = False

# Could be useful in a potential next version needing to output the events too
_dtype_trigger = [('pos', 'int64'),
                ('points', 'int64'),
                ('channel', 'int64'),
                ('type', 'S16'),  # TODO check size
                ('description', 'S16'),  # TODO check size
                ]

# This is the thread that will be launched whenever we call the start function of the MEGBuffer
# The order of execution is : init, run, etc  
class MEGBuffer_Thread(QtCore.QThread):
    # We need all these parameters from the psychopy script to make an easier and more intuitive save function
    def __init__(self, ftc, outputs, parent=None,ch_names=None,sample_rate=None,nb_steps=5,clf_name=None,run_nbr=0,
    subjectId='default',partType = 'part1',dateStart = '',MEGsave = ''):
        assert HAVE_FIELDTRIP, "MEGBuffer node depends on the `FieldTrip` package, but it could not be imported. Please make sure to download FieldTrip.py and store it next to this file "
        print('Thread initialized')
        QtCore.QThread.__init__(self)

        # The many attributes of the thread : necessary for exchanges with the psychopy script
        self.lock = Mutex()
        self.running = False
        self.ftc = ftc
        self.outputs=outputs
        self.ch_names = ch_names
        self.Fs = sample_rate
        self.nb_steps_chosen = nb_steps
        self.clf_name = clf_name
        self.run_nbr = run_nbr
        self.subjectId = subjectId
        self.dateStart = dateStart
        self.partType = partType
        self.MEGsave = MEGsave

        # Initializing save matrixes
        self.matSaveNbSamples = np.zeros(1)
        self.matSaveData = np.zeros(1)
        self.matDetect=np.zeros(1)
        self.matProbas=np.zeros(1)
        self.matProbas2=np.zeros(1)
        self.matSaveDataTrigger=np.zeros(1)

    # Function to extract the 274 channels used for the training of the classifier
    def extract_right_channels(self, data, ch_names):
        ch = ch_names
        picks = []
        for i in range(len(ch)):
            if (('ML' in ch[i]) or ('MR' in ch[i]) or ('MZ' in ch[i]) and ('EEG' not in ch[i]) and ('UPPT' not in ch[i])):
                #or 
                #B' in ch[i]) or ('R' in ch[i]) or ('P' in ch[i]) or
                #('Q' in ch[i]) or ('G' in ch[i]))
                picks.append(i)

        # Added a try catch only for a special part of the experiment : inbetween two saves files, the MEG sends more than 
        # the usual 303 channels : we need to make sure the thread doesn't crash there.
        try : 
            data = data[:,picks]              
        except :
            print("Error with channels : unusually high number")
            data = data[:,:274] 
        return data     
    # This is the main function of the script, where the while loop containing the poll, the getdata etc is
    # That's also where we call the classifier and choose the method we want to use to send the signal to change
    # the image or not to the psychopy script
    def run(self):
        print('Thread running')
        clfName = self.clf_name
        classifier = load('./classifiers/meg/'+clfName) # Loading the classifier
        lastIndex = None
        self.probaSample = 8 # The length of the vector for the second validation method
        self.probaThreshold = 4 # The numeric value of the threshold for the third validation method
        self.currentProbaSum = 0 # Value reset every positive classification
        self.nbSteps = int(self.nb_steps_chosen)
        # Quick confirmation to make sure we chose the right classifier
        print('chosen classifier : ' + clfName + 'with nb of step : ' + str(self.nbSteps))

        # Our homemade ringbuffers: 
        prediction = list(2*(np.ones(self.nbSteps)))
        predictionProbas = list(2*(np.zeros(self.probaSample)))
        i = 0
        
        with self.lock:
            self.running = True
            
        while True:
            # Simpe lock system : we leave the loop when we want to close the thread (by calling the stop function)
            with self.lock:
                if not self.running:
                    break

                # Added a try if the fieldtrip buffer stop being connected for a short period of time (change of MEG save)
                try:
                    globalIndex, useless = self.ftc.poll()
                except:
                    print("polling failed")
                    time.sleep(0.1)
                
                # Basic packet sent to the next node : zeros
                toSend = np.zeros(1)
                
                # For the first poll
                if lastIndex is None :
                    lastIndex = globalIndex
                    
                # This line makes sure that if there is no new package received, we go back to the beggining of the loop
                # We added the sleep not to overcharge the network
                if(globalIndex==lastIndex):
                    time.sleep(0.005)
                    continue
                
                # Getting the data from the fieldtripclient
                # print("Time before the getdata : ",time.time())
                try :
                    data = self.ftc.getData([lastIndex,globalIndex-1])
                except :
                    time.sleep(5)
                # print("Time after the getdata megbuffer : ",time.time())

                nsamples= lastIndex
                # We only want 24 sized packages
                # If we get one bigger than 24, we only take the end of the package
                if(data[:,40].shape[0]>24):
                    data = data[data[:,40].shape[0]-24:data[:,40].shape[0],:]
                    
                # We are adding the information at the end of the array which contains
                # Information about the sample number
                arrayIndexes = np.ones(24).reshape(24,1)
                arrayIndexes = arrayIndexes*nsamples
                extracted_data = self.extract_right_channels(data, self.ch_names)
                extracted_data_plus_indexes=np.append(extracted_data,arrayIndexes,axis=1)
                
                # The raw values we want to save
                values = extracted_data_plus_indexes[:,:274]
                values_mean = np.mean(values, axis=0)
                values_mean_reshaped = values_mean.reshape(1,274)
                
                sampleIndex = np.ones(24)*nsamples
                for p in range(0,24):
                    sampleIndex[p]=sampleIndex[p]+p
                    

                dataFrom200chan= values[:,200] # We will save the data of the 200th channel to compare with MEG saved files

                # We also extract the data from the UPPT002 channel (used mostly to compare the timing CLF trigger -> Image chance)
                try :
                    dataFromTrigger =  data[:,319]
                except : 
                    print("Problem with channels")
                    dataFromTrigger = np.zeros(24)

                # Appending all the data gotten from this particular 24 sample packet in the matrix that we will save later
                self.matSaveNbSamples = np.append(self.matSaveNbSamples,sampleIndex, axis=0)
                self.matSaveData = np.append(self.matSaveData,dataFrom200chan, axis=0)
                self.matSaveDataTrigger = np.append(self.matSaveDataTrigger,dataFromTrigger, axis=0)

                # Inputting the current packet in the classifier : we save the probability and the output
                prediction[i]=classifier.predict(values_mean_reshaped)[0]
                predictionProbas[i]=classifier.predict_proba(values_mean_reshaped)[0]
                prediction_proba=classifier.predict_proba(values_mean_reshaped)[0]

                # Adding the probability from the classifier : we save both probabilities (they sum up to 1)
                mat_prediction_proba = np.ones(24)*prediction_proba[0]
                mat_prediction_proba2 = np.ones(24)*prediction_proba[1]

                # Appending again
                self.matProbas = np.append(self.matProbas,mat_prediction_proba, axis=0)
                self.matProbas2 = np.append(self.matProbas2,mat_prediction_proba2, axis=0)
                

                # We will send a 50 to the output of the MEGBuffer if this is the first positive prediction in a row
                # Else, if the previous packet was also classified as a positive one, we will send 0.5 instead, so
                # It's easier for us to find the start of the suite of positive trigger in post-processing

                #*********************
                # 1st : Current : If all of the predictions are equal to detection of motor activity (number of steps method)
                #*********************
                # if((max(prediction))==0):
                #     #print("Trigger from classifier at the sample no ", extracted_data_plus_indexes[13,274])
                #     toSend=np.ones(1)
                #     # print(prediction_proba)

                #     if(self.matDetect[-1]==50 or self.matDetect[-1]==0.5):
                #         toAdd=0.5
                #     else:
                #         toAdd=50
                # else:
                #     toAdd=0


                #*********************
                # 2nd : Other option : probability density with fixed length: 
                #*********************

                # if(sum(predictionProbas > self.probaSample/1.4)):
                #     print('sum prediction proba : %d , probaSample/1.4 : %d'%(sum(predictionProbas),self.probaSample/1.4))
                #     toSend=np.ones(1)
                #     if(self.matDetect[-1]==50 or self.matDetect[-1]==0.5):
                #         toAdd=0.5
                #     else:
                #         toAdd=50
                # else:
                #     toAdd=0


                #*********************
                # 3rd : Other option : probability density with adjustable length and threshold: 
                #*********************
                self.currentProbaSum += prediction_proba[0]
                if(self.currentProbaSum > self.probaThreshold):
                    print("Sum of probability reached threshold")
                    # Resetting the currentProbaSum to zero : 
                    self.currentProbaSum = 0
                    toSend=np.ones(1)
                    if(self.matDetect[-1]==50 or self.matDetect[-1]==0.5):
                        toAdd=0.5
                    else:
                        toAdd=50
                else:
                    toAdd=0


                self.matDetect=np.append(self.matDetect,toAdd*np.ones(24),axis=0)
                # Send the data (a packet of 24 times 0.5 or 50) to the next node (an inputstream in the agency script)
                self.outputs['signals'].send(toSend.astype('float32'))        
                

                lastIndex = globalIndex
                if((i+1)>=self.nbSteps):
                    i=0
                else : 
                    i=i+1


    # This is the stop function of the thread that will be called when we are done with the MEGBuffer
    # It will save the data from all the different matrixes and apply some data remodeling to make
    # It easier for later post-processing
    def stop(self):
        print('Thread stopped')
        # Using the matDetect matrix to extract the number of triggers after the first one
        # The 50 information is going to be replaced by the number of subsequent triggers
        # After the first one, and the ones will stay
        print("Modifying the saveDataMat")
        # We modify the matDetect matrix to replace the 50 information by the number of 
        # subsequent positive packets in a row
        for a in range(1,self.matDetect.size,24):
            if(self.matDetect[a]==50):
                y = 24
                nbDetected=0
                if(a+y<self.matDetect.size):
                    while(self.matDetect[a+y]==0.5 and (a+y+24<self.matDetect.size)):
                        y+=24
                        nbDetected+=1
                    self.matDetect[a]=nbDetected+1 
                # Erasing all the 50 values that are not needed anymore
                for k in range(1,24):
                    self.matDetect[a+k]=0.5
                    
        current_directory = os.getcwd()
        final_directory = os.path.join(current_directory, r'saves')
        if not os.path.exists(final_directory):
           os.makedirs(final_directory)
        
        # Configuring the name of the saving file
        dateT = datetime.now()
        timet = dateT.strftime("%H:%M:%S")
        timeStamp = timet.replace(':', '') 
        datePsy = psy.data.getDateStr()
    
        # Saving is based on the parameters transmitted from the psychopy script
        print("Saving data in the MEGBuffer...")
        savingFileName = 'saves/Agentivity_BCI_' + self.subjectId +'_' +str(self.run_nbr)+'_'+ str(self.partType)+'_'+ str(self.dateStart) +'_'+ str(self.clf_name)+'_'+str(self.nbSteps) +'steps_megsave'+str(self.MEGsave)+'.csv'
        
        # Quick fix : in some cases, we stop the polling at the wrong time and miss a classification
        if(self.matDetect.shape[0]<self.matSaveData.shape[0]):
            self.matDetect=np.append(self.matDetect,np.zeros(24),axis=0)

        # Appending all the matrixes to the same array
        matSaveData = np.c_[self.matSaveData,self.matSaveNbSamples,self.matDetect,self.matProbas,self.matProbas2,self.matSaveDataTrigger]

        # Use fmt=%d if you don't need to use the values of the data and focus on the triggers
        # Else, remove it because it will make the first column equal to zero (10e-14=> 0)
        np.savetxt(savingFileName, matSaveData, delimiter=',',fmt='%5.5g')
        
        # Analyzing the triggers from a local file (to comment if not in local)
        # Used for comparing the results from the MEGBuffer (and the classifier)
        # With an existing trigger file extracted from session 1

        # raw = read_raw_ctf('data/0989MY_agency_20210415_06.ds', preload=True)
        # # **** reading the triggering channel ****
        # trigger_ch_number = raw.ch_names.index('UPPT002')
        # trigger = raw.get_data()[trigger_ch_number]
        # events_tri = mne.find_events(raw, stim_channel="UPPT002", consecutive=True, shortest_event=1)
        # plt.plot(trigger) #
        # np.savetxt('saves/triggersFromDSFile'+timeStamp+'.csv', events_tri,  delimiter=',',fmt ='%d' )
        # try :
            # predicting_clf(timeStamp,self.subjectId,self.nbSteps)
        # except :
            # print('predict_clf failed miserably')

        # Disconnection the socket etc
        with self.lock:
            self.running = False
            self.ftc.disconnect()
            print('Socket disconnected')
            
            
class MEGBuffer(Node):
    
    _output_specs = {'signals': dict(streamtype='analogsignal', dtype='float32',
                                     shape=(-1, 1)),
                                'triggers': dict(streamtype = 'event', dtype = _dtype_trigger,
                                                shape = (-1,)),
                                }
   
    def __init__(self, **kargs):
        Node.__init__(self, **kargs)

    def _configure(self,nb_steps_chosen,clf_name,run_nbr,subjectId,partType,timeStart,MEGsave):

        # ******************** IMPORTANT PARAMETERS ************************
        self.hostname = 'localhost' # Localhost only works when working offline, on your own computer (with MATLAB)

        # ---------------- This is the current IP of the MEG (lastly been working 08/07/2021)
        # self.hostname ='100.1.1.5' 
        # ---------------- Please make sure you are correctly connected to the MEG with an RJ-45 cable and in manuel connection (not DHCP)
        # ---------------- The IP address you can allocate yourself for example :  100.1.1.10 (minimum 10 for the last 4 bits)
        # ---------------- The subnet mask : 4
        # ---------------- The gateway : 10.1.1.4

        self.port = 1972 # The port is fortunately always the same
        # For more informations regarding this procedure, don't hesitate to take a look at the doc or the readme 
        # ******************** IMPORTANT PARAMETERS ************************


        self.ftc = FieldTrip.Client()
        self.ftc.connect(self.hostname, self.port) # Connecting to the fieldtrip client   # might throw IOError
        # Get the header and print it to make sure everything is normal
        self.H = self.ftc.getHeader()
        print(self.H)
        self.nb_steps_chosen = nb_steps_chosen
        self.clf_name = clf_name
        self.run_nbr = run_nbr
        self.subjectId = subjectId
        self.partType = partType
        self.timeStart = timeStart
        self.MEGsave = MEGsave

        self.nb_channel = self.H.nChannels
        self.sample_rate = self.H.fSample
        self.nb_samples = self.H.nSamples
        self.nb_events = self.H.nEvents
        self.data_type = self.H.dataType
        
        #Setting up the name of the different channels
        self.chan_names = self.H.labels
          
        # Settings of the output for the next PyAcq node
        self.outputs['signals'].spec['shape'] = (-1, 1)
        
        self.outputs['signals'].spec['nb_channel'] = self.nb_channel
        self.outputs['signals'].spec['sample_rate'] = self.sample_rate
        #self.output.spec['buffer_size'] = 1000
        print(self.nb_channel)
    # This is where we initialize the thread with all the due parameters
    def _initialize(self):
        self._thread = MEGBuffer_Thread(self.ftc, outputs=self.outputs,
                                        parent=self, ch_names=self.chan_names,
                                        sample_rate=self.sample_rate,nb_steps=self.nb_steps_chosen,
                                        clf_name=self.clf_name,run_nbr = self.run_nbr, subjectId = self.subjectId, 
                                        partType = self.partType, dateStart = self.timeStart,MEGsave = self.MEGsave)
        


    def _start(self):
        self._thread.start()

    def _stop(self):
        self._thread.stop()
        #self._thread.wait()

    def _close(self):
        pass

# This will hopefully be done soon with the help of Samuel Garcia to fully integrate the node to pyacq
#register_node_type(MEGBuffer)


# Just a quick testing main to make sure everything related to fieldtrip and pyacq works before starting to use the script! 
if __name__ == "__main__":

    #Nodes 
    MEGB =  MEGBuffer()
    inputStream = InputStream()
    
    # Configuring MEGBuffer node
    MEGB.configure(nb_steps_chosen=5,clf_name= 'classifiers/FAY_meg_CLF [-0.3,-0.1].joblib',run_nbr=4,subjectId='0991')  
    MEGB.outputs['signals'].configure( transfermode='plaindata')
    MEGB.outputs['triggers'].configure( transfermode='plaindata')
    MEGB.initialize()
    inputStream.connect(MEGB.outputs['signals'])
    MEGB.start()    

    # Polling and receiving the data sent by the MEGBuffer node
    dataIsAvailable = inputStream.poll()
    data = inputStream.recv()
      
    i=0
    nbPaquetsToTest = 200 #  represents the number of packages of 24 we want to test
    nbPred = 0
    while(dataIsAvailable and i<nbPaquetsToTest):    
    # while(dataIsAvailable):          
        data = inputStream.recv() # Pulling the data from the stream
        if( data[1][0] == 1):
            print('Detection')
            nbPred+=1
                        
        else:
            #print('NO DETEK')
            a = 2
        try :
            dataIsAvailable = inputStream.poll(1000)
        except : 
            print("Error with polling the input stream")
            break
        i=i+1
        
    print("Nb detek : ",nbPred)
        

  

    # Closing the sockets and threads 
    MEGB.stop()
    inputStream.close()
    MEGB.close()
    

    
    
    
    