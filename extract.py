import numpy as np
import mne
from mne.io import read_raw_ctf
import os.path as op
import os

from config import * #check ce fichier où tu vas mettre ta config, les path, les subject que tu choisis etc.

#THIS SCRIPT IS FOR EXTRACT FILE FOR MATLAB AND EXTRACT TRIGGER
# **** loading files ****
subj_nb = 0
total_run = 0
for subject, sessions in zip(subjects_id, session_subject):
    subj_nb += 1
    for _, session in enumerate(sessions):
        for file_to_ana in files_to_ana:
            fname7 = op.join(path_data, session, 'MEG') #the path file name
            files = os.listdir(fname7) #all file in your path
            runs = list() #all your run ds
            runs.extend(f for f in files if file_to_ana in f)
            # for run_number, this_run in enumerate(runs): #all the run 
            for run_number, this_run in enumerate([runs[0]]):   #if you want only one run       
                run_to_load = op.join(fname7, this_run)
                raw = read_raw_ctf(run_to_load, preload=True)

                # **** reading the triggering channel ****
                trigger_ch_number = raw.ch_names.index('UPPT002')
                trigger = raw.get_data()[trigger_ch_number]

                # **** detecting the events from the triggering  ****
                events_tri = mne.find_events(raw, stim_channel="UPPT002", consecutive=True, shortest_event=1)
                
                # **** delete trigger associated to start and end of file ****
                events_tri_to_del_id = list()
                for parcours_eve_tri_ix in range(events_tri.shape[0]):
                    if (events_tri[parcours_eve_tri_ix,2] == 252
                        or events_tri[parcours_eve_tri_ix,2] == 253
                        or events_tri[parcours_eve_tri_ix,2] == 4):
                        events_tri_to_del_id.append(parcours_eve_tri_ix)
                events_tri = events_tri[np.delete(range(0, events_tri.shape[0]), events_tri_to_del_id)] 

                # **** saving trigger ****   
                directory = op.join(path_saving, 'trigger') #create a folder for save your trigger             
                fname1 = op.join(directory,'%s_%s_session%s_run%s_trigger.csv' #noqa
                            % (subject, file_to_ana, session_nb, run_number))
                np.savetxt(fname1, events_tri, fmt = '%d', delimiter=',')

                # **** saving raw/filter file with no filtering **** #ce qu'on va lire sur matlab
                directory = op.join(path_saving, 'file/')
                fname2 = op.join(directory, '%s_%s_session%s_run%s_raw.fif' #raw name
                            % (subject, file_to_ana, session_nb, run_number))
                fname3 = op.join(directory,'%s_%s_session%s_run%s.fif' #filter name
                            % (subject, file_to_ana, session_nb, run_number))                
                
                # raw.save(fname2, overwrite=True)
                # raw.filter(0.6, 30)              
                # raw.save(fname3, overwrite=True)
                
