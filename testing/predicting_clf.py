import pandas as pd
import matplotlib.pyplot as plt
import copy
import numpy as np
import mne
from mne.io import read_raw_ctf
import os.path as op
import os

from config import * #check ce fichier où tu vas mettre ta config, les path, les subject que tu choisis etc.
def predicting_clf(timeStamp,subjectId,nbSteps):
	# **** opti pour automatiser le read des triggers pour tout les runs et tout les sujets ***** a faire aussi pour les clf_trigger mais pas pressé
	# **** il faudrait name les save clf_trigger de la meme façon, pour qu'on sache quel run, quel sujet match avec quel clf etc ca sera plus simple ****
	# **** loading files ****
	# subj_nb = 0
	# total_run = 0
	#permet de lire tout les fichiers csv par sujet

	# for subject, sessions in zip(subjects_id, session_subject):
	#     subj_nb += 1
	#     for session_nb, session in enumerate(sessions):
	#         for file_to_ana in files_to_ana:
	#             fname1 = op.join(path_saving, 'trigger') #the path file name where you have your trigger
	#             files = os.listdir(fname1) #all file in your path
	#             runs = list()
	#             runs.extend(f for f in files if file_to_ana in f)
	#             # for run_number, this_run in enumerate(runs): #all the run 
	#             for run_number, this_run in enumerate([runs[0]]):   #if you want only one run       
	#                 run_to_load = op.join(fname1, this_run)
	#                 # **** load the original trigger file ****
	#                 trigger = pd.read_csv(run_to_load, header=None) 
	#                 events_tri = np.array(trigger) #array of original trigger file


	# load the original trigger file
	trigger = pd.read_csv('saves/trigger/'+subjectId+'_agency_session0_run0_trigger.csv')
	events_tri = np.array(trigger) #array of original trigger file
	events_tri= events_tri[np.where(events_tri[:,5]>19)]
	print(events_tri)
	# load the detected motor preparation file
	clf_trigger = pd.read_csv('saves/savedData'+subjectId+'_'+timeStamp+'_'+nbSteps+'steps.csv')
	clf_tri = np.array(clf_trigger.iloc[:, 1]) #only the trigger
	clf_first_tri = clf_tri[np.where(clf_trigger.iloc[:, 2] > 1)[0]]

	# build a matrice, named value, with 5 columns:
	# the timing of the detected motor preparation,
	# the timing of the trigger,
	# the difference between the two,
	# the index of the trigger,
	# and if it was human or machine (20 or 40)
	value = []
	for det, clf_trial in enumerate(clf_first_tri): # for all detected motor premaration
		index_tri = np.where((clf_trial-events_tri[:, 0]) < 0)[0][0] # find the index of the trigger immediately following the motor preparation
		if bool(value) == False or index_tri not in np.array(value)[:, 3]: # if value is empty, or if the index was not yet present in value, complete value
			value.append([clf_trial, events_tri[index_tri, 0], (clf_trial-events_tri[index_tri,0]) / 600,
						index_tri, events_tri[index_tri, 2]])

	# calculate the total number of human and machine triggers occuring between the first and the last detected motor preparation (I ADDED A +1 TO INCLUDE THE LAST TRIGGER THAT WE NEGLECTED LAST TIME)
	nb_human = np.where(events_tri[value[0][3]:(value[-1][3]+1), 2] == 20)[0].shape[0]
	nb_machine = np.where(events_tri[value[0][3]:(value[-1][3]+1), 2] == 40)[0].shape[0]

	# take third element for sort
	def takeThird(elem):
		return elem[2]
	# sort list with key
	value.sort(key=takeThird)

	# make a copy of the list so we don't change the original value
	value2 = copy.deepcopy(value)
	# create hit & fa
	hit = []
	fa = []
	for i in range (len(value2)):
		if value2[i][4] == 20:
			hit.append(value2[i])
		else:
			fa.append(value2[i])
	# change the 20 and 40, by the % (I ADDED THE +1 BECAUSE THE FIRST DETECTION IS 1/N AND NOT 0)
	for i in range(len(hit)):
		hit[i][4] = (i+1)/nb_human
	for i in range(len(fa)):
		fa[i][4] = (i+1)/nb_machine

	# make an array
	hit = np.array(hit, dtype='object')
	fa = np.array(fa, dtype='object')

	# see the data
	# print('hit', hit, '\n\nfa', fa)
	# plt.plot(hit[:, 2], hit[:, 4])
	# plt.plot(fa[:, 2], fa[:, 4])
	# plt.show()

	# try to reproduce our plot from predicting but not working very well some errors to fix
	#ne pas prendre -3.3 mais le min.
	steppredic = np.linspace(-3.3, 0, 331) #create interval -3.3 to 0 of 300 sample # I JUST ADDED A FEW SAMPLES TO MATCH THE WIDTH OF 0.01 YOU PUT FOR THE WIDTH OF YOU BAR PLOT BELOW
	cumul_mov = np.zeros(len(steppredic))
	cumul_not = np.zeros(len(steppredic))
	cumul_dif = np.zeros(len(steppredic))
	for lim_n, lim in enumerate(steppredic):
		cumul_mov[lim_n] = sum(hit[:, 2] < lim)/ nb_human
		cumul_not[lim_n] = sum(fa[:, 2] < lim)/ nb_machine
		cumul_dif[lim_n] = cumul_mov[lim_n] - cumul_not[lim_n]

	# plt.figure(1, figsize=(19.20, 10.80))
	plt.bar(steppredic, cumul_mov, align='edge', width=-0.01, alpha=0.5)
	plt.bar(steppredic, cumul_not, align='edge', width=-0.01, alpha=0.5)
	plt.show()
