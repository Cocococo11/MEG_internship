import numpy as np
from basemy import * 
from config import *
import mne


#**** PLOT THE SCORES *****
file_to_ana = 'npy'
file_to_ana_session = 'session1'
which_channels = 'meg'
file = thedirectorydecod(path_saving, 'results/decoding/meg/') #noqa
fname = op.join(file)
files = os.listdir(fname)
runs = list()
runs.extend(f for f in files if file_to_ana in f and file_to_ana_session in f and which_channels in f and 'probas' not in f) #only for score

subj_nb = 0
all_scores_subjects = []
timeforplot = np.linspace(-1, 1, 241)
lb = np.where(timeforplot == -1)[0][0] # -1 sec
ub = np.where(timeforplot == -0.7)[0][0] # -0.7 sec
lb2 = np.where(timeforplot == -0.35)[0][0] 
ub2 = np.where(timeforplot == -0)[0][0]

for run_number, this_run in enumerate(runs):
	run_to_load = op.join(fname, this_run)
	scores_subjects = np.load(run_to_load)
	all_scores_subjects.append(scores_subjects)
	subj_nb += 1

all_scores_subjects = np.array(all_scores_subjects)
# print('number of subject %s, shape of scores %s' % (subj_nb, all_scores_subjects.shape))

all_scores_subjects_sem = np.std(all_scores_subjects, axis=0)/np.sqrt(len(all_scores_subjects))
all_scores_subjects_mean = all_scores_subjects.mean(0,)
all_scores_subjects_mean = smooth_to_plot(all_scores_subjects_mean)
mean1 = all_scores_subjects_mean + all_scores_subjects_sem
mean2 = all_scores_subjects_mean - all_scores_subjects_sem
minforplot = min(mean2)
maxforplot = max(mean1)
# plt.fill_between(timeforplot, mean1, mean2, color='green', alpha=0.5, label=which_channels) #-1 to 0 
# plotchanceandlimit([timeforplot[0], timeforplot[-1]], [0.5], [minforplot, maxforplot], [0])
# plt.axvline(-0.35, ymin=0.05, ymax=0.953, color='r', linestyle='--', linewidth = 0.8, alpha=0.5) #beginning of RP
# plt.xlabel('Temps en seconde')
# plt.ylabel('Score')
# plt.legend()
# # plt.title('Decoding tous les canaux MEG'
# #             + '\nChannels : ' + which_channels
# #             + '\n[Mean at [' + str(timeforplot[lb]) + ':' + str(timeforplot[ub]) +   '] = ' +  str(round(np.mean(all_scores_subjects_mean[lb:ub])*100,1))
# #             + '\n[Mean at [' + str(timeforplot[lb2]) + ':' + str(timeforplot[ub2]) + '] = ' +  str(round(np.mean(all_scores_subjects_mean[lb2:ub2])*100,1)))

# print('T350 ms score : ', round(np.mean(all_scores_subjects_mean[lb2])*100,1), '\nT0 ms score : ', round(np.mean(all_scores_subjects_mean[ub2])*100,1))
# plt.show()

# # 4. save figure and all subject score
# fname = op.join(directorydecod,
#                 'allsubject_%s_session%s_%s_average.jpg'  # noqa
#                 % (file_to_ana, session_nb, which_channels))
# plt.savefig(fname, dpi=300)
# plt.show()


#**** PLOT THE PROBAS *****
subj_nb = 0
runs = list()
runs.extend(f for f in files if file_to_ana in f and file_to_ana_session in f and which_channels in f and 'probas' in f) #only for probas

# for run_number, this_run in enumerate(runs):
for run_number, this_run in enumerate([runs[1]]):
	run_to_load = op.join(fname, this_run)
	all_probas_subjects = np.load(run_to_load)
	subj_nb += 1

all_probas_subjects_sem = np.std(all_probas_subjects, axis=0)/np.sqrt(len(all_probas_subjects))
all_probas_subjects_mean = all_probas_subjects.mean(0,)
all_probas_subjects_mean = smooth_to_plot(all_probas_subjects_mean)
mean1 = all_probas_subjects_mean + all_probas_subjects_sem
mean2 = all_probas_subjects_mean - all_probas_subjects_sem
minforplot = min(mean2)
maxforplot = max(mean1)


plt.plot(timeforplot, all_probas_subjects_mean)
plotchanceandlimit([timeforplot[0], timeforplot[-1]], [0.5], [minforplot, maxforplot], [0])
plt.xlabel('Temps en seconde')
plt.ylabel('Score')                          
plt.legend()
plt.show()


plt.fill_between(timeforplot, mean1, mean2, color='green', alpha=0.5, label=which_channels)
plotchanceandlimit([timeforplot[0], timeforplot[-1]], [0.5], [minforplot, maxforplot], [0])
plt.xlabel('Temps en seconde')
plt.ylabel('Score')                            
plt.legend()
plt.show()

print('T350 ms score : ', round(np.mean(all_probas_subjects_mean[lb2])*100,1), '\nT0 ms score : ', round(np.mean(all_probas_subjects_mean[ub2])*100,1))




#split human machine
#moyenne de prediction
#moyenne de proba
