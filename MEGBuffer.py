from pyacq.core import Node
from pyacq.core.stream import InputStream
# from pyacq.rec import RawRecorder
from pyqtgraph.Qt import QtCore

#import struct
import os
# import shutil
import time
from pyqtgraph.util.mutex import Mutex
from joblib import load
import mne
from mne.io import read_raw_ctf
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
import pandas as pd
from predicting_clf import predicting_clf 
from config import * 
from psychopy import data
#from fieldtrip2mne import pick_channels

try:
    import FieldTrip
    HAVE_FIELDTRIP = True
except ImportError:
    HAVE_FIELDTRIP = False
    
#import FieldTripfrom mne import pick_channels

_dtype_trigger = [('pos', 'int64'),
                ('points', 'int64'),
                ('channel', 'int64'),
                ('type', 'S16'),  # TODO check size
                ('description', 'S16'),  # TODO check size
                ]

    
class MEGBuffer_Thread(QtCore.QThread):

    def __init__(self, ftc, outputs, parent=None,ch_names=None,sample_rate=None,nb_steps=5,clf_name=None,run_nbr=0,subjectId='default'):
        assert HAVE_FIELDTRIP, "MEGBuffer node depends on the `FieldTrip` package, but it could not be imported. Please make sure to download FieldTrip.py and store it next to this file "
        print('Thread initialized')
        QtCore.QThread.__init__(self)
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
        # Initializing save matrixes
        self.matSaveNbSamples = np.zeros(1)
        self.matSaveData = np.zeros(1)
        self.matDetect=np.zeros(1)
        self.matProbas=np.zeros(1)
        self.matProbas2=np.zeros(1)
        self.matSaveDataTrigger=np.zeros(1)
           
    def extract_right_channels(self, data, ch_names):
        ch = ch_names
        picks = []
        for i in range(len(ch)):
            if (('ML' in ch[i]) or ('MR' in ch[i]) or ('MZ' in ch[i]) and ('EEG' not in ch[i]) and ('UPPT' not in ch[i])):
                #or 
                #B' in ch[i]) or ('R' in ch[i]) or ('P' in ch[i]) or
                #('Q' in ch[i]) or ('G' in ch[i]))
                picks.append(i)
            
        try : 
            data = data[:,picks]              
        except :
            print("Error with channels : unusually high number")
            data = data[:,:274] 
        return data     

    def run(self):
        print('Thread running')
        clfName = self.clf_name
        classifier = load('./classifiers/meg/'+clfName) # Cross clf / data
        lastIndex = None
        self.nbSteps = int(self.nb_steps_chosen)
        print('chosen classifier : ' + clfName + 'with nb of step : ' + str(self.nbSteps))
        prediction = list(2*(np.ones(self.nbSteps)))
        i = 0
        
        with self.lock:
            self.running = True
            
        while True:
            with self.lock:
                if not self.running:
                    break
                try:

                    globalIndex, useless = self.ftc.poll()
                except:
                    print("polling failed")
                    time.sleep(0.1)
                toSend = np.zeros(1)
                
                if lastIndex is None :
                    lastIndex = globalIndex
                    
                if(globalIndex==lastIndex):
                    time.sleep(0.005)
                    continue
                
                # Getting the data from the fieldtripclient
                try :
                    data = self.ftc.getData([lastIndex,globalIndex-1])
                except :
                    time.sleep(5)

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
                    
                dataFrom200chan= values[:,200] # We will save the data of the 200th channel
                try :
                    dataFromTrigger =  data[:,319]
                except : 
                    print("Problem with channels")
                    dataFromTrigger = np.zeros(24)
                # print('Data from trigger : ',dataFromTrigger) # For trigger debugging
                self.matSaveNbSamples = np.append(self.matSaveNbSamples,sampleIndex, axis=0)
                self.matSaveData = np.append(self.matSaveData,dataFrom200chan, axis=0)
                self.matSaveDataTrigger = np.append(self.matSaveDataTrigger,dataFromTrigger, axis=0)
                
                
                # print(values_mean_reshaped)

                prediction[i]=classifier.predict(values_mean_reshaped)[0]
                
                prediction_proba=classifier.predict_proba(values_mean_reshaped)[0]
                mat_prediction_proba = np.ones(24)*prediction_proba[0]
                mat_prediction_proba2 = np.ones(24)*prediction_proba[1]
                self.matProbas = np.append(self.matProbas,mat_prediction_proba, axis=0)
                self.matProbas2 = np.append(self.matProbas2,mat_prediction_proba2, axis=0)
                # print(prediction_proba)
                
                
                if((max(prediction))==0):
                    #print("Trigger from classifier at the sample no ", extracted_data_plus_indexes[13,274])
                    toSend=np.ones(1)
                    # print(prediction_proba)

                    if(self.matDetect[-1]==50 or self.matDetect[-1]==0.5):
                        toAdd=0.5
                    else:
                        toAdd=50
                else:
                    toAdd=0
                self.matDetect=np.append(self.matDetect,toAdd*np.ones(24),axis=0)
                
                self.outputs['signals'].send(toSend.astype('float32'))
                 
                
                lastIndex = globalIndex
                if((i+1)>=self.nbSteps):
                    i=0
                else : 
                    i=i+1
            
    def stop(self):
        print('Thread stopped')
        # Using the matDetect matrix to extract the number of triggers after the first one
        # The 50 information is going to be replaced by the number of subsequent triggers
        # After the first one, and the ones will stay
        print("Modifying the saveDataMat")
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
        datePsy = data.getDateStr()
    
        print("Saving data ...")
        savingFileName = 'saves/save' + self.subjectId +'_' + datePsy +'_'+ str(self.nbSteps) +'steps_run'+str(self.run_nbr)+'.csv'
        matSaveData = np.c_[self.matSaveData,self.matSaveNbSamples,self.matDetect,self.matProbas,self.matProbas2,self.matSaveDataTrigger]
        # Use fmt=%d if you don't need to use the values of the data and focus on the triggers
        # Else, remove it because it will make the first column equal to zero (10e-14=> 0)
        np.savetxt(savingFileName, matSaveData, delimiter=',',fmt='%5.4g')
        
        # # # Analyzing the triggers from a local file (to comment if not in local)
        # raw = read_raw_ctf('data/0989MY_agency_20210415_06.ds', preload=True)
        # # **** reading the triggering channel ****
        # trigger_ch_number = raw.ch_names.index('UPPT002')
        # trigger = raw.get_data()[trigger_ch_number]
        # events_tri = mne.find_events(raw, stim_channel="UPPT002", consecutive=True, shortest_event=1)
        # plt.plot(trigger) #
        # np.savetxt('saves/triggersFromDSFile'+timeStamp+'.csv', events_tri,  delimiter=',',fmt ='%d' )
        # try :
            # predicting_clf(timeStamp,self.subjectId,self.nbSteps)


        # predicting_clf(timeStamp,self.subjectId,self.nbSteps)


        # except :
            # print('predict_clf failed miserably')

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

    def _configure(self,nb_steps_chosen,clf_name,run_nbr,subjectId):

        self.hostname = 'localhost'
        # self.hostname ='100.1.1.5'
        self.port = 1972
        self.ftc = FieldTrip.Client()
        self.ftc.connect(self.hostname, self.port)    # might throw IOError
        self.H = self.ftc.getHeader()
        print(self.H)
        self.nb_steps_chosen = nb_steps_chosen
        self.clf_name = clf_name
        self.run_nbr = run_nbr
        self.subjectId = subjectId

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

    def _initialize(self):
        self._thread = MEGBuffer_Thread(self.ftc, outputs=self.outputs,
                                        parent=self, ch_names=self.chan_names,
                                        sample_rate=self.sample_rate,nb_steps=self.nb_steps_chosen,
                                        clf_name=self.clf_name,run_nbr = self.run_nbr, subjectId = self.subjectId)
        


    def _start(self):
        self._thread.start()

    def _stop(self):
        self._thread.stop()
        #self._thread.wait()

    def _close(self):
        pass

#register_node_type(MEGBuffer)

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
    

    
    
    
    