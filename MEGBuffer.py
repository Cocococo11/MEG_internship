#import numpy as np

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
# from datetime import datetime
import numpy as np
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

    def __init__(self, ftc, outputs, parent=None,ch_names=None):
        assert HAVE_FIELDTRIP, "MEGBuffer node depends on the `FieldTrip` package, but it could not be imported. Please make sure to download FieldTrip.py and store it next to this file "
        print('Thread initialized')
        QtCore.QThread.__init__(self)
        self.lock = Mutex()
        self.running = False
        self.ftc = ftc
        self.outputs=outputs
        self.ch_names = ch_names
        
    def extract_right_channels(self, data, ch_names):
        ch = ch_names
        picks = []
        for i in range(len(ch)):
            if (('ML' in ch[i]) or ('MR' in ch[i]) or ('MZ' in ch[i]) and ('EEG' not in ch[i]) and ('UPPT' not in ch[i])):
                #or 
                #B' in ch[i]) or ('R' in ch[i]) or ('P' in ch[i]) or
                #('Q' in ch[i]) or ('G' in ch[i]))
                picks.append(i)
            
        data = data[:,picks]              
        return data     

    def run(self):
        print('Thread running')
        lastIndex = None
        with self.lock:
            self.running = True
            
        while True:
            with self.lock:
                if not self.running:
                    break

            globalIndex, useless = self.ftc.poll()
            
            if lastIndex is None :
                lastIndex = globalIndex
                
            if(globalIndex==lastIndex):
                #print('last index : ' +lastIndex)
                #print('global index : ' +globalIndex)
                #print('Stuck because no new data fetched, we sleep for 0.005s')
                time.sleep(0.005)
                continue
            
            #TODO 
            # We should not fetch data when globalIndex = lastIndex
            # and so in the case we sleep, we should also skip these 2 next lines
            #print('On recupere les donnees et evenements')
            data = self.ftc.getData([lastIndex,globalIndex-1])
            #events = self.ftc.getEvents([lastIndex,globalIndex-1])
            # if(events is not None):
            #     print('EVENEMENT : ', events)
            # nbEvents = 0
            # print('Nb evenements totaux : ', nbEvents)
            # if events is not None :
            #     nbEvents+=nbEvents
            
            
            # Here, we try to add the index of sample into the data we're going
            # To send to the next node, adding a column at the end
            nsamples= self.ftc.getHeader().nSamples
            #print(nsamples)
            arrayIndexes = np.ones(24).reshape(24,1)
            arrayIndexes = arrayIndexes*nsamples
            extracted_data = self.extract_right_channels(data, self.ch_names)
            extracted_data_plus_indexes=np.append(extracted_data,arrayIndexes,axis=1)
            #print(extracted_data_plus_indexes.shape)
            #if (D.shape[0] != 24 ):
            # print("On recupere depuis %d canaux un bloc de %d  (verification bloc %d )" %(data.shape[1], data.shape[0], globalIndex-lastIndex))
            #print("On envoie sur la sortie uniquement %d channels de donnees " %(extracted_data.shape[1]))
            
            #self.outputs['signals'].send(data.astype('float32'))
            #print('We are sending interesting data composed by %d channels' %(extracted_data))
            self.outputs['signals'].send(extracted_data_plus_indexes.astype('float32'))
            #self.outputs['signals'].send(data.astype('float32'))
            #self.outputs['triggers'].send(events)
            
            lastIndex = globalIndex

    def stop(self):
        print('Thread stopped')
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

    def _configure(self):

        self.hostname = 'localhost'
        #self.hostname ='100.1.1.5'
        self.port = 1972
        
        self.ftc = FieldTrip.Client()
        
        # Testing connection to the Client
        print('Trying to connect to buffer on %s:%i ...' % (self.hostname, self.port))
        self.ftc.connect(self.hostname, self.port)    # might throw IOError
        
        #Debugging
        
        print('\nConnected - trying to read header...')
        self.H = self.ftc.getHeader()
        if self.H is None:
            print('Failed!')
        else:
            print('Header successfully obtained : ')
            print(self.H)
            print(self.H.labels)
        
        
        self.nb_channel = self.H.nChannels
        self.sample_rate = self.H.fSample
        self.nb_samples = self.H.nSamples
        self.nb_events = self.H.nEvents
        self.data_type = self.H.dataType
        
        #Setting up the name of the different channels
        self.chan_names = self.H.labels
          
        # Settings of the output for the next PyAcq node
        self.outputs['signals'].spec['shape'] = (-1, self.nb_channel)
        
        self.outputs['signals'].spec['nb_channel'] = self.nb_channel
        self.outputs['signals'].spec['sample_rate'] = self.sample_rate
        #self.output.spec['buffer_size'] = 1000
        print(self.nb_channel)

    def _initialize(self):
        self._thread = MEGBuffer_Thread(self.ftc, outputs=self.outputs,
                                        parent=self, ch_names=self.chan_names)
        


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
    
    # Choosing which classifier to use
    classifier = load('classifiers/0989_meg_CLF_pack [-0.3,-0.1]_filter.joblib')
    #classifier = load('classifiers/0989_meg_CLF_pack [-0.3,-0.1]_filter.joblib')
    
    # Analyzing the triggers from a local file (to comment if not in local)
    raw = read_raw_ctf('0989MY_agency_20210415_02.ds', preload=True)
    # **** reading the triggering channel ****
    trigger_ch_number = raw.ch_names.index('UPPT002')
    trigger = raw.get_data()[trigger_ch_number]
    events_tri = mne.find_events(raw, stim_channel="UPPT002", consecutive=True, shortest_event=1)
    plt.plot(trigger) #
    
    
    # Configuring MEGBuffer node
    MEGB.configure()  
    MEGB.outputs['signals'].configure( transfermode='plaindata')
    MEGB.outputs['triggers'].configure( transfermode='plaindata')
    MEGB.initialize()
    inputStream.connect(MEGB.outputs['signals'])
    MEGB.start()    
    
    # Configuring the name of the saving file
    # dateT = datetime.now()
    # timet = dateT.strftime("%H:%M:%S")
    # timett = timet.replace(':', '') 
    # dirname = timett
    # while os.path.exists(dirname):
    #     dirname+='1'
         #shutil.rmtree(dirname)


    # Polling and receiving the data sent by the MEGBuffer node
    dataIsAvailable = inputStream.poll()
    data = inputStream.recv()
    
    # We save the first index to compare it to the known triggers (only in local)
    firstSampleIndex = data[1][7,274]
    
    
    i=0
    nbPaquetsToTest = 100#  represents the number of packages of 24 we want to test
    nbPred = 0
    prediction =[2,2]
    matSaveNbSamples = np.zeros(1)
    matSaveData = np.zeros(1)
    matSaveTriggerHistory = np.zeros(1)
    while(dataIsAvailable and i<nbPaquetsToTest):
        #print("Data received from inputStream : ")
        oldIndex = data[0]
        #print(data[0])
        
        data = inputStream.recv() # Pulling the data from the stream
        
        print("Donnees de sample number : ",data[1][:,274])
        # This loop makes sure we don't save null values
        # Which exist since the .recv() can return null
        if(data[0] is not None and data[1][:,200] is not None):
            sampleIndex = np.ones(24)*data[1][:,274]
            dataFrom200chan= data[1][:,200] # We will save the data of the 200th channel
            matSaveNbSamples = np.append(matSaveNbSamples,sampleIndex, axis=0)
            matSaveData = np.append(matSaveData,dataFrom200chan, axis=0)
            
            
        values = data[1][:,:274]
        values_mean = np.mean(values,axis=0)
        values_mean_reshaped = values_mean.reshape(1,274)

        prediction[0]=prediction[1]
        prediction[1]= classifier.predict(values_mean_reshaped)
        
        probaPred = classifier.predict_proba(values_mean_reshaped)
        #print("Actual probability of detection  : ", probaPred)
        predCurrent = prediction[1]
        predBefore = prediction[0]
        if((predCurrent + predBefore)==0):
            print("Trigger from classifier at the sample no ", data[1][13,274])
            
            triggerSample= np.zeros(1)
            triggerSample[0]= data[1][7,274]
            matSaveTriggerHistory = np.append(matSaveTriggerHistory,triggerSample, axis=0)
            nbPred=nbPred+1
        dataIsAvailable = inputStream.poll()
        #print("i: " ,i)
        i=i+1
        
        
        
    # Saving the data under csv files
    current_directory = os.getcwd()
    final_directory = os.path.join(current_directory, r'saves')
    if not os.path.exists(final_directory):
       os.makedirs(final_directory)
    print("Saving data ...")
    # We make different csv files to make it easier to use under excel
    np.savetxt('saves/rawIndexSamples.csv', matSaveNbSamples,  delimiter='\n')
    np.savetxt('saves/rawData.csv', matSaveData,  delimiter='\n')
    np.savetxt('saves/indexClassifierTrigger.csv', matSaveTriggerHistory,  delimiter='\n')
    #TODO Comment the next line if you're not in local mode
    np.savetxt('saves/triggersFromDSFile.csv', events_tri,  delimiter=',',fmt ='%d' )
    print("We found %d detections of motor activity out of %d samples "%(nbPred,oldIndex))
    if(nbPred != 0):
        print("Which means one detection every %d samples" %(oldIndex/nbPred))
    else : 
        print("Not a single trigger")
    
    
    # Closing the sockets and threads 
    MEGB.stop()
    inputStream.close()
    MEGB.close()
    

    
    
    
    