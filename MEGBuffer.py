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
        prediction = [2,2]
        
        with self.lock:
            self.running = True
            
        while True:
            with self.lock:
                if not self.running:
                    break
                globalIndex, useless = self.ftc.poll()
                
                toSend = np.zeros(1)
                
                if lastIndex is None :
                    lastIndex = globalIndex
                    
                if(globalIndex==lastIndex):
                    time.sleep(0.005)
                    continue
                
                data = self.ftc.getData([lastIndex,globalIndex-1])

                nsamples= lastIndex
                if(data[:,40].shape[0]>24):
                    data = data[data[:,40].shape[0]-24:data[:,40].shape[0],:]
                arrayIndexes = np.ones(24).reshape(24,1)
                arrayIndexes = arrayIndexes*nsamples
                extracted_data = self.extract_right_channels(data, self.ch_names)
                extracted_data_plus_indexes=np.append(extracted_data,arrayIndexes,axis=1)
                
                values = extracted_data_plus_indexes[:,:274]
                values_mean = np.mean(values,axis=0)
                values_mean_reshaped = values_mean.reshape(1,274)
        
                prediction[0]=prediction[1]
                prediction[1]= classifier.predict(values_mean_reshaped)
                
                predCurrent = prediction[1]
                predBefore = prediction[0]
                if((predCurrent + predBefore)==0):
                    print("Trigger from classifier at the sample no ", extracted_data_plus_indexes[13,274])
                    toSend=np.ones(1)
                
  
                self.outputs['signals'].send(toSend.astype('float32'))
                 
                
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
        self.ftc.connect(self.hostname, self.port)    # might throw IOError
        self.H = self.ftc.getHeader()
        print(self.H)
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

    
    # Configuring MEGBuffer node
    MEGB.configure()  
    MEGB.outputs['signals'].configure( transfermode='plaindata')
    MEGB.outputs['triggers'].configure( transfermode='plaindata')
    MEGB.initialize()
    inputStream.connect(MEGB.outputs['signals'])
    MEGB.start()    

    # Polling and receiving the data sent by the MEGBuffer node
    dataIsAvailable = inputStream.poll()
    data = inputStream.recv()
      
    i=0
    nbPaquetsToTest = 500 #  represents the number of packages of 24 we want to test
    nbPred = 0
    prediction =[2,2]
    while(dataIsAvailable and i<nbPaquetsToTest):        
        data = inputStream.recv() # Pulling the data from the stream
        if( data[1][0] == 1):
            print('DETEKKKKKKKKKKKKKKKKKKKKK')
            nbPred+=1
                        
        else:
            print('NO DETEK')
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
    

    
    
    
    