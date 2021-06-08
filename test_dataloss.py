# Testing data losses

import mne
import numpy as np
import os.path as op
import pandas as pd
import matplotlib.pyplot as plt

directory = 'C:/Users/Coco/Desktop/simple-megbuffer and script/saves/file/'
subject = 'fay'
session = ''
filename = 'saves/file/fa_agency_session0_run0_filter.fif'
fname = op.join(directory, '%s.fif' % (filename))

# epochs = mne.read_epochs(fname)
# raw = mne.io.read_raw_fif(filename)
# data_to_dec = datatodec('meg', epochs)
# events = mne.read_events(filename)
# print(events)

# for every run generated
best = 10000
for run in range(12,13):


    # TRIGGERS FROM MEG SAVING
    trigger_MEG = pd.read_csv('saves/trigger/fa_agency_session0_run'+str(run)+'_trigger.csv')
    events_meg = np.array(trigger_MEG) #array of original trigger file
    startingIndexMEG = events_meg[1,0]
    endIndexMEG = events_meg[-1,0]
    # print(trigger_MEG)
    # print("indexes : ", startingIndexMEG,endIndexMEG)
    total_of_samplesMEG = endIndexMEG-startingIndexMEG

    # print(np.where(events_meg[:,2]==20))
    nb_human_MEG= np.where(events_meg[:,2]==20)[0].shape[0]
    nb_comp_MEG= np.where(events_meg[:,2]==40)[0].shape[0]
    print('La sauvegarde MEG a enregistré %d triggers humains et %d triggers du clf, sur %d samples'%(nb_human_MEG,nb_comp_MEG,total_of_samplesMEG))

    # TRIGGERS RETRIEVED FROM MEGBUFFER SAVINGS
    trigger_MEGBuffer = pd.read_csv('saves_fay/savedDataFAY_155208_5steps.csv')
    # events_tri = np.array(trigger_MEGBuffer[startingIndexMEG:endIndexMEG,:]) # only looking for the indexes that were saved on the MEG
    events_tri = np.array(trigger_MEGBuffer)
    indexStartCorresponding = np.where(events_tri[:,1]==startingIndexMEG)
    print(indexStartCorresponding)
    indexEndCorresponding = np.where(events_tri[:,1]==endIndexMEG)
    events_tri = events_tri[indexStartCorresponding:indexEndCorresponding,:] # only looking for the indexes that were saved on the MEG
    startingIndex = events_tri[1,1]
    endIndex = events_tri[-1,1]
    total_of_samples = endIndex-startingIndex
    # Making sure there is only one timestamp equal to 20 everytime for easier counting
    for a in range(2,events_tri[:,5].size):
        if( events_tri[a,5]==20 and (events_tri[a-1,5]==20 or events_tri[a-1,5]==0.5) and a<events_tri[:,5].size-1):
            events_tri[a,5]=0.5
    events_tri= events_tri[np.where( (events_tri[:,5]==20))]
    # print(events_tri)
    total_button_press = events_tri[:,5].shape[0]
    clf_tri = np.array(trigger_MEGBuffer)
    for a in range(1,clf_tri[:,5].size-2):
            if(a+2<clf_tri.size and (clf_tri[a,5]==40 or clf_tri[a,5]==0.5) and clf_tri[a+1,5]==40):
                clf_tri[a+1,5]=0.5
    clf_first_tri = clf_tri[np.where(clf_tri[:, 5] ==40)[0]]
    total_clf_trigger = clf_first_tri.shape[0]
    clf_tri = np.array(trigger_MEGBuffer)
    # True positives
    for a in range(1,clf_tri[:,5].size-2):
            if(a+2<clf_tri.size and (clf_tri[a,5]==10 or clf_tri[a,5]==0.5) and clf_tri[a+1,5]==10):
                clf_tri[a+1,5]=0.5
    clf_true_pos = clf_tri[np.where(clf_tri[:, 5] ==10)[0]]
    total_clf_trigger_early = clf_true_pos.shape[0]

    nb_human_MEGB= np.where(events_tri[:,5]==20)[0].shape[0]
    nb_comp_MEGB= np.where(events_tri[:,5]==40)[0].shape[0]
    # print("Nombre de trigger early : ",total_clf_trigger_early)
    diffTriggerClf = abs(nb_comp_MEGB-nb_comp_MEG)
    diffTriggerButton = abs(nb_human_MEGB-nb_human_MEG+total_clf_trigger_early)
    totalDiff = diffTriggerButton + diffTriggerClf
    if(totalDiff<best):
        best = totalDiff
        best_run = (run)
    print('La sauvegarde MEGBuffer a enregistré %d triggers humains et %d triggers du clf, sur un total de %d samples'%(nb_human_MEGB+total_clf_trigger_early,total_clf_trigger, total_of_samples))
    print('La différence en terme de nombre de button press est de : %d et de clf_trigger : %d'%(diffTriggerButton,diffTriggerClf))
    print('La meilleure run est la : %d avec %d de différences'%(best_run,best))
    plt.plot(clf_tri[startingIndexMEG:endIndexMEG,1], clf_tri[startingIndexMEG:endIndexMEG,5],'b',label='MEGBuffer save')
    # plt.plot(clf_true_pos[startingIndexMEG:endIndexMEG,1], clf_true_pos[startingIndexMEG:endIndexMEG,5],'b',label='MEGBuffer save')
    plt.plot(events_meg[:,0], events_meg[:,2],'r',label ='MEG saves')
    # plt.xlim([-0.6,0])
    plt.title('Figure of triggers saved from two different methods (run '+str(run)+')')
    plt.legend()
    plt.ylabel('Triggers (20 human or 40 computer)')
    plt.xlabel('Sample number')
    plt.show()
