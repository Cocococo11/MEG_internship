import numpy as np

from pyacq.core import Node, register_node_type
from pyacq.core.stream import stream, InputStream
from pyqtgraph.Qt import QtCore, QtGui

import struct
import time
from pyqtgraph.util.mutex import Mutex

try:
    import FieldTrip
    HAVE_FIELDTRIP = True
except ImportError:
    HAVE_FIELDTRIP = False
    
import FieldTrip
from mne import pick_channels

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
        picks = list()
        for i in range(len(ch)):
            if 'MLC' in ch[i] :
                picks.append(ch[i])
        data.pick_channels(picks) #24 channel               
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
            #print('EVENEMENT : ', events)
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
            #extracted_data = self.extract_right_channels(data, self.ch_names)
            
            #if (D.shape[0] != 24 ):
            # print("On recupere depuis %d canaux un bloc de %d  (verification bloc %d )" %(data.shape[1], data.shape[0], globalIndex-lastIndex))
            #print("On envoie sur la sortie uniquement %d channels de donnees " %(extracted_data.shape[1]))
            
            #self.outputs['signals'].send(data.astype('float32'))
            #print('We are sending interesting data composed by %d channels' %(extracted_data))
            #self.outputs['signals'].send(extracted_data.astype('float32'))
            self.outputs['signals'].send(data.astype('float32'))
            self.outputs['triggers'].send(events)
            
            lastIndex = globalIndex

    def stop(self):
        print('Thread stopped')
        with self.lock:
            self.running = False

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
        self._thread.wait()

    def _close(self):
        pass

#register_node_type(MEGBuffer)

if __name__ == "__main__":
    from pyacq.viewers import QOscilloscope
    app = QtGui.QApplication([])
    
    MEGB =  MEGBuffer()
    inputStream = InputStream()
    MEGB.configure()
    
    MEGB.outputs['signals'].configure( transfermode='sharedmem')
    #MEGB.outputs['triggers'].configure( transfermode='plaindata')
    MEGB.initialize()
    
    # osc = QOscilloscope()
    # osc.configure(with_user_dialog=True)
    # osc.input.connect(MEGB.outputs['signals'])
    inputStream.connect(MEGB.outputs['signals'])

    # osc.initialize()
    # osc.show()

    # start both nodes
    # osc.start()
    MEGB.start()
    #time.sleep(40)
    dataIsAvailable = inputStream.poll()
    if(dataIsAvailable):
            print("Data received from inputStream : "+ inputStream.recv())
    
    
        
    
    app.exec_()
    time.sleep(40)
    
    MEGB.stop()
    inputStream.stop()
    # osc.stop()
    

    
    
    
    