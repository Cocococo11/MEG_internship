#import numpy as np

from pyacq.core import Node
from pyacq.core.stream import InputStream
from pyacq.rec import RawRecorder
from pyqtgraph.Qt import QtCore, QtGui

#import struct
import os
import shutil
import time
from pyqtgraph.util.mutex import Mutex
from joblib import load
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
            events = self.ftc.getEvents([lastIndex,globalIndex-1])
            # if(events is not None):
            #     print('EVENEMENT : ', events)
            # nbEvents = 0
            # print('Nb evenements totaux : ', nbEvents)
            # if events is not None :
            #     nbEvents+=nbEvents
            
            
            #Saving the data in a file
            # dataNumpy = np.asarray(data)
            # #print('Data numpy saved : ',dataNumpy)
            # np.savetxt('npfile.csv', dataNumpy, delimiter=',')
            
            #We choose to extract only the data from the left motor hemisphere
            #print('ch_names we are gonna get the data of',self.ch_names)
            nsamples= self.ftc.getHeader().nSamples
            #print(nsamples)
            extracted_data = self.extract_right_channels(data, self.ch_names)
            #if (D.shape[0] != 24 ):
            # print("On recupere depuis %d canaux un bloc de %d  (verification bloc %d )" %(data.shape[1], data.shape[0], globalIndex-lastIndex))
            #print("On envoie sur la sortie uniquement %d channels de donnees " %(extracted_data.shape[1]))
            
            #self.outputs['signals'].send(data.astype('float32'))
            #print('We are sending interesting data composed by %d channels' %(extracted_data))
            self.outputs['signals'].send(extracted_data.astype('float32'))
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
    classifier = load('classifiers/0989_meg_CLF_pack [-0.3,-0.1]_raw.joblib')
    #classifier = load('classifiers/0989_meg_CLF_pack [-0.3,-0.1]_filter.joblib')
    
    
    MEGB.configure()
    
    MEGB.outputs['signals'].configure( transfermode='plaindata')
    MEGB.outputs['triggers'].configure( transfermode='plaindata')
    MEGB.initialize()
    
    # dateT = datetime.now()
    # timet = dateT.strftime("%H:%M:%S")
    # timett = timet.replace(':', '') 
    # dirname = timett
    # while os.path.exists(dirname):
    #     dirname+='1'
         #shutil.rmtree(dirname)
    
    # rec = RawRecorder()
    # rec.configure(streams=[MEGB.outputs['signals']], autoconnect=True, dirname=dirname)
    # rec.initialize()

    inputStream.connect(MEGB.outputs['signals'])

    MEGB.start()
    # rec.start()
    #time.sleep(40)
    dataIsAvailable = inputStream.poll()
    data = inputStream.recv()
    i=0
    nbPred = 0
    prediction =[2,2]
    matSaveNbSamples = np.zeros(1)
    matSaveData = np.zeros(1)
    while(dataIsAvailable and i<1000):
        #print("Data received from inputStream : ")
        oldIndex = data[0]
        #print(data[0])
        
        data = inputStream.recv()
        if(data[0] is not None and data[1][:,200] is not None):
            b = np.ones(24)*data[0]
            c= data[1][:,200]
            matSaveNbSamples = np.append(matSaveNbSamples,b, axis=0)
            matSaveData = np.append(matSaveData,c, axis=0)
            
            
        values = data[1]
        values_clean = values[:,:]
        values_mean0 = np.mean(values_clean,axis=0)
        values_mean1 = values_mean0.reshape(1,274)

        prediction[0]=prediction[1]
        prediction[1]= classifier.predict(values_mean1)
        # prediction[1]= classifier.predict_proba(random_val)
        #print("Proba : ", prediction[1])
        pred = prediction[1]
        if(prediction[0]+prediction[1]==0):
            print("Mouvement detecté au sample numero : ", data[0])
            nbPred=nbPred+1
        dataIsAvailable = inputStream.poll()
        #print("i: " ,i)
        i=i+1
        
    #dataNumpy = np.asarray(matSave)
    print("Saving data ...")
    np.savetxt('npfileSamples.csv', matSaveNbSamples,  delimiter='\n')
    np.savetxt('npfileData.csv', matSaveData,  delimiter='\n')
    print("We found %d detections of motor activity out of %d samples "%(nbPred,oldIndex))
    print("Which means one detection every %d samples" %(oldIndex/nbPred))
    
    MEGB.stop()
    # rec.stop()
    inputStream.close()
    MEGB.close()
    # rec.close()
    # osc.stop()
    

    
    
    
    