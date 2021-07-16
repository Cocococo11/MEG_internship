import os
import os.path as op
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

# def thecodes(file_to_ana, decod_scr_with_trigger):
#     if file_to_ana == 'Guided':
#         if decod_scr_with_trigger == 1:
#             cow_codes_scr = [40, 42]
#         else:
#             cow_codes_scr = [40, 50]
#         textleft_codes = [40, 45]
#         cow_codes = [1060, 1065, 1070, 1075,
#                      2060, 2065, 2070, 2075]
#         round_codes = [1060, 1065, 1070, 1075,
#                        1560, 1565, 1570, 1575]
#         left_codes = [1060, 1065, 1560, 1565,
#                       2060, 2065, 2560, 2565]
#         text_codes = [1060, 1070, 1560, 1570,
#                       2060, 2070, 2560, 2570]
#     if file_to_ana == 'JustCue':
#         cow_codes_scr = []
#         textleft_codes = []
#         cow_codes = []
#         round_codes = [10100, 10110, 10120]
#         left_codes = []
#         text_codes = []
#     if file_to_ana == 'Spontaneous':
#         cow_codes_scr = []
#         textleft_codes = [40]
#         cow_codes = []
#         round_codes = []
#         left_codes = [1060, 1065]
#         text_codes = [1060, 1070]
#     return cow_codes_scr, textleft_codes, cow_codes, round_codes, left_codes, text_codes  #noqa


#which channel we want to decode
def datatodec(which_channels, epochs):
    if which_channels == 'meg':
        epochs.pick_types(meg=True, ref_meg=False)
        data_to_dec = epochs._data
    elif which_channels == 'meg&ref':
        epochs.pick_types(meg=True)
        data_to_dec = epochs._data
    elif which_channels == 'meg&emg':
        epochs.pick_types(meg=True, eeg=True, ref_meg=False)
        data_to_dec = epochs._data        
    elif which_channels == 'eyes':
        data_to_dec = epochs._data[:, epochs.ch_names.index('UADC010-2800'):epochs.ch_names.index('UADC011-2800')+1, :]  # noqa
    elif which_channels == 'pupil':
        data_to_dec = epochs._data[:, None, epochs.ch_names.index('UADC012-2800'), :]  # noqa
    elif which_channels == 'emg':
        epochs.pick_types(eeg=True)
        data_to_dec = epochs._data
    elif which_channels == 'trigger':
        data_to_dec = epochs._data[:, None, epochs.ch_names.index('UPPT002'), :]  # noqa
    elif which_channels == 'mlc': #motor left channel
        picks = [chan for chan in epochs.ch_names if 'MLC' in chan]
        epochs.pick_channels(picks)  
        data_to_dec = epochs._data
    elif which_channels == 'mrc': #motor right channel
        picks = [chan for chan in epochs.ch_names if 'MRC' in chan] 
        epochs.pick_channels(picks)
        data_to_dec = epochs._data
    elif which_channels == 'mlc&emg&eyes': #motor left channel + emg + eyes (saccade) + pupil
        picks = [chan for chan in epochs.ch_names if 'MLC' in chan]
        picks.extend(['UADC010-2800', 'UADC011-2800', 'UADC012-2800', 'EEG064-2800'])  #add emg pupil eyes
        epochs.pick_channels(picks)
        data_to_dec = epochs._data
    elif which_channels == 'motor':
        picks = [chan for chan in epochs.ch_names if 'MLC' in chan or 'MRC' in chan or 'MZC' in chan] #every motor, right, left, and central
        epochs.pick_channels(picks)
        data_to_dec = epochs._data
    else: #if no precision decode on all channels
        data_to_dec = epochs._data
    return data_to_dec


def datatodec_conc(which_channels, epochs, epochs_times, package):
    #****  decode a package of data for example : package_size = 23  | epochs_times = 181   | time = time -1
    # package = 23
    # epochs_times = len(epochs.times)
    # time=1
    if which_channels == 'emg':
        data_to_dec = epochs._data[:, None, epochs.ch_names.index('EEG064-2800'), package:epochs_times]
        for time in range(1, 24):
            data_to_dec = np.concatenate((data_to_dec, epochs._data[:, None, epochs.ch_names.index('EEG064-2800'),  package-time:epochs_times-time]), axis = 1)
    elif which_channels == 'eyes':
        data_to_dec = epochs._data[:, epochs.ch_names.index('UADC010-2800'):epochs.ch__lenames.index('UADC011-2800')+1, package:epochs_times]
        for time in range(1, 24):
            data_to_dec = np.concatenate((data_to_dec, epochs._data[:, epochs.ch_names.index('UADC010-2800'):epochs.ch_names.index('UADC011-2800')+1,  package-time:epochs_times-time]), axis = 1)
    elif which_channels == 'pupil':
        data_to_dec = epochs._data[:, None, epochs.ch_names.index('UADC012-2800'), package:epochs_times]
        for time in range(1, 24):
            data_to_dec = np.concatenate((data_to_dec, epochs._data[:, None, epochs.ch_names.index('UADC012-2800'), package-time:epochs_times-time]), axis = 1)
    else:
        data_to_dec = epochs._data[:, :, package:epochs_times] 
        for time in range(1, 24):
            data_to_dec = np.concatenate((data_to_dec, epochs._data[:, :,  package-time:epochs_times-time]), axis = 1)
    return data_to_dec


def whattodecod(somecode, y):
    yTD = y.copy()
    yTD[:] = 1
    yTD[np.where(np.in1d(y, somecode))] = 0
    return yTD


def smooth_to_plot(array_of_decod):
    array_of_decod2 = array_of_decod.copy()
    for i in range(len(array_of_decod)-4):
        array_of_decod2[i+2] = (array_of_decod2[i] +
                                array_of_decod2[i+1] +
                                array_of_decod2[i+2] +
                                array_of_decod2[i+3] +
                                array_of_decod2[i+4])/5
    return array_of_decod2


def thedirectory(path_analyzed_data, which_channels, RAW=False): 
    if RAW:
        directory = op.join(path_analyzed_data, 'results_agency/raw/epochs_allchannels') #if you want to epochs with raw data
    else:
        directory = op.join(path_analyzed_data, 'results_agency/epochs_allchannels')  # noqa
    if not op.exists(directory):
        # print "directory"
        os.mkdir(directory)
    return directory


def thedirectorydecod(path_analyzed_data, endofpath):
    directorydecod = op.join(path_analyzed_data, endofpath)
    if not op.exists(directorydecod):
        os.mkdir(directorydecod)
    return directorydecod


def plotchanceandlimit(horizontal_extent, horizontal_borders, vertical_extent, vertical_borders):  # noqa
    for hor_bor in horizontal_borders:
        plt.plot(horizontal_extent, [hor_bor, hor_bor], color='black', linestyle='dashed', alpha=0.5)  # noqa
    for ver_bor in vertical_borders:
        plt.plot([ver_bor, ver_bor], vertical_extent, color='black', linestyle='dashed', alpha=0.5)  # noqa


def transfo_sign_analog(signal, targetValueMin, targetValueMax, targetStep1, targetStep2, halfDist):  # noqa
    # targetValueMin = 0
    # targetValueMax = 37.75
    # targetStep1 = 0.25
    # targetStep2 = 7.5
    # halfDist = 30
    signal2 = np.copy(signal)
    signal_high = np.where([item > (targetValueMax-targetStep1) for item in signal])  # 37.5  # noqa
    signal_low = np.where([item < (targetValueMin+targetStep1) for item in signal]) # 0.25  # noqa
    signal2[signal_high] = targetValueMax  # 37.75
    signal2[signal_low] = targetValueMin  # 0
    signal3 = np.copy(signal2)
    # signal_high = np.where([(item < targetValueMax and item > (targetValueMax-targetStep2)) for item in signal2[:-halfDist]])  # noqa
    # signal_low = np.where([(item < (targetValueMin+targetStep2) and item > targetValueMin) for item in signal2[:-halfDist]])  # noqa
    signal_high = np.where([(item < targetValueMax and item > (targetValueMax-targetStep2)) for item in signal2])  # noqa
    signal_low = np.where([(item < (targetValueMin+targetStep2) and item > targetValueMin) for item in signal2])  # noqa
    for item in signal_high[0]:
        if signal2[item+halfDist] > (targetValueMax-targetStep2):
            signal3[item] = targetValueMax
    for item in signal_low[0]:
        if signal2[item+halfDist] < (targetValueMin+targetStep2):
            signal3[item] = targetValueMin
    signal4 = np.copy(signal3)
    signal_inter = np.where([(item < targetValueMax and item > targetValueMin) for item in signal3[:-halfDist]])  # noqa
    for item in signal_inter[0]:
        if signal3[item+halfDist] > (targetValueMax-targetValueMin)/2:
            signal4[item] = targetValueMax
        else:
            signal4[item] = targetValueMin
    signal5 = np.copy(signal4)
    signal5[np.where(signal5 == targetValueMin)] = 0
    # ** plot to check and remove the last glinch for signal **
    # plt.plot(signal)
    # plt.plot(signal4)
    # plt.show()
    return signal5

def detect_emg(signal, threshold1, threshold2, length1, length2):
    emg3 = np.abs(signal)
    emg4 = np.zeros(signal.shape)
    for item in np.where(emg3 > threshold1)[0]:
        liminf = np.max([0, item - length1])
        limsup = np.min([item + length1, emg3.shape[0]])
        if np.where(emg3[liminf:limsup]>threshold2)[0].shape[0]>1:
            emg4[liminf:limsup] = threshold1
    emg5 = emg4
    for item in np.where(emg4 == threshold1)[0]:
        if emg4[item+length2]==threshold1:
            emg5[item:item+length2] =threshold1
    # plt.plot(emg2)
    # plt.plot(emg4)
    # plt.plot(emg5)
    # plt.show()
    return emg5

def plot_photodiode(photodiode, photodiode2, trigger):
    plt.plot(photodiode)
    plt.plot(photodiode2)
    plt.plot(trigger)
    plt.title('Photodiode and Trigger')
    plt.legend(('Photodiode', 'Photodiode2', 'Trigger'), loc='upper left')            
    plt.show()
    # plt.clf()

def plot_eyetracker(raw_eyeA, raw_eyeB, raw_eyeC, subject, run_number, file):
    timems = np.arange(0, raw_eyeA.shape[0]/600, 1/600)      
    plt.plot(timems, raw_eyeB, alpha=0.7, label='X')
    plt.plot(timems, raw_eyeA, alpha=0.7, label='Y')
    plt.plot(timems, raw_eyeC, alpha=0.7, label='Pupil')
    plt.xlabel('Temps en seconde') #a changer
    plt.ylabel('Valeur arbitraire')
    plt.title(subject + ' run n°' + str(run_number) + ' Eye Tracker')
    plt.legend(loc='upper right')
    fname = op.join(file, '%s_run%s_eye.jpg' %(subject, run_number))
    plt.savefig(fname)
    # plt.show()
    plt.clf()

def plot_detect_emg(emg, emg2, trigger, subject):
    plt.plot(emg*30000)
    if subject == 'FAY' or subject == '0992' or subject == '0993' or subject == '0994' or subject == '0995':
        plt.plot(emg2*100000)
    elif subject == '0986' or subject == '0987' or subject == '0989' or subject == '0990' or subject =='0991' or subject == '0996' or subject == '1059' or subject == '1060' or subject == '1061':
        plt.plot(emg2*30000)
    plt.plot(trigger)
    plt.xlabel('Hz') #a changer
    plt.ylabel('Valeur arbitraire')
    plt.title(subject + ' Detection of EMG when button press')
    plt.legend(('EMG', 'Détection EMG', 'Evènement'), loc='upper left')
    plt.show()           
    # plt.clf()
    # from biosppy.signals import emg as bioemg #function that plot emg and onset
    # ts, emg3, onsets = bioemg.emg(emg, sampling_rate=600)

def plot_event_before(events_tri, events_ima, E, F, subject, run_number, file):
    plt.hist((events_tri[E, 0]-events_ima[E, 0])/600, bins=40, label='Button', alpha = 0.5) # distribution of reaction time  # noqa
    plt.hist((events_tri[F, 0]-events_ima[F, 0])/600, bins=40, label='Nothing', fc=(1, 0, 0, 0.5)) # distribution of random changes of image  # noqa
    plt.legend()
    plt.xlabel('Times in second')
    plt.ylabel('Trials')
    plt.title(subject + ' run n°' + str(run_number) + ' Distribution of events through time (before delete)')
    fname = op.join(file, '%s_run%s_eventbefore.jpg' %(subject, run_number))
    plt.savefig(fname)
    # plt.show()
    plt.clf()

def plot_event_after(events_tri, events_ima, E, F, subject, run_number, file):
    plt.hist((events_tri[E, 0]-events_ima[E, 0])/600, bins=40, label='Button', alpha = 0.5) # distribution of reaction time  # noqa
    plt.hist((events_tri[F, 0]-events_ima[F, 0])/600, bins=40, label='Nothing', fc=(1, 0, 0, 0.5)) # distribution of random changes of image  # noqa
    plt.legend()
    plt.xlabel('Times in second')
    plt.ylabel('Trials')
    # plt.xlim(right=0.7, left=0.4) #detect button press before 500 ms
    plt.title(subject + ' run n°' + str(run_number) + ' Distribution of events through time (after delete)')
    fname = op.join(file, '%s_run%s_eventafter.jpg' %(subject, run_number))
    plt.savefig(fname)
    # plt.show()
    plt.clf()


def plot_emg(G, subject, run_number, file):
    plt.hist(G/600, bins=40)
    plt.xlabel('Times in second')
    plt.ylabel('Trials')
    plt.title(subject + ' run n°' + str(run_number) + ' Distribution of EMG immediately preceding a button press')
    fname = op.join(file, '%s_run%s_emg.jpg' %(subject, run_number))
    plt.savefig(fname)
    # plt.show()
    plt.clf()


def plot_blank(events_bla, events_ima, events_tri, subject, run_number, file):
    #**** all trials ****
    plt.hist((events_ima[1:, 0]-events_bla[0:-1, 0])/600, bins=40)  # 22 or 23 ms of blank for all trials, one trial with 32 ms, except between the pause  # noqa
    plt.xlabel('Times in second')
    plt.ylabel('Trials')
    plt.title(subject + ' run n°' + str(run_number) + ' Distribution of blank for all trials' )
    fname = op.join(file, '%s_run%s_blanktrials.jpg' %(subject, run_number))
    plt.savefig(fname)    
    # plt.show()
    plt.clf()

    #**** triggers ****
    plt.hist((events_bla[:, 0]-events_tri[:, 0])/600, bins=40)      # 7 values between 18 ms and 28 ms  # noqa
    plt.xlabel('Times in second')
    plt.ylabel('Trials')
    plt.title(subject + ' run n°' + str(run_number) +' Distribution of blank for triggers') 
    fname = op.join(file, '%s_run%s_blanktriggers.jpg' %(subject, run_number))
    plt.savefig(fname) 
    # plt.show()
    plt.clf()



#save multiple fig in pdf
def multipage(filename, figs=None, dpi=300):
    pp = PdfPages(filename)
    if figs is None:
        figs = [plt.figure(n) for n in plt.get_fignums()]
    for fig in figs:
        fig.savefig(pp, format='pdf')
    pp.close()



# def plot_all_emg(all_G, runs, subject):
#     plt.figure(figsize=(19.20, 10.80))
#     emg_rt = []
#     emg_rt_percent = []
#     for i in range(len(runs)):    
#         plt.hist(all_G[i]/600, bins=40, color = 'seagreen')
#         emg_rt.append(all_G[i]/600) #add tout les temps de réactions dans une liste
#         emg_rt_percent.append(len(np.where(emg_rt[i] <=1)[0]) / len(emg_rt[i]) * 100) #récupère le % lorsque temps de reaction < 1
#     plt.xlabel('Times in second')
#     plt.ylabel('Trials')
#     plt.title(subject + 'Distribution of all EMG immediately preceding a button press'
#         +'\nPercentage under 1 sec : ' + str(round(sum(emg_rt_percent) / len(emg_rt_percent),3)) + '%')


# def plot_all_emg_subj(new_G, total_run):
#     plt.figure(figsize=(19.20, 10.80))
#     emg_rt = []
#     emg_rt_percent = []
#     for i in range(total_run):    
#         plt.hist(new_G[i]/600, bins=40, color = 'seagreen')
#         emg_rt.append(new_G[i]/600) #add tout les temps de réactions dans une liste
#         emg_rt_percent.append(len(np.where(emg_rt[i] <=1)[0]) / len(emg_rt[i]) * 100) #récupère le % lorsque temps de reaction < 1
#     plt.xlabel('Times in second')
#     plt.ylabel('Trials')
#     plt.title('all subjects Distribution of all EMG immediately preceding a button press'
#         +'\nPercentage under 1 sec : ' + str(round(sum(emg_rt_percent) / len(emg_rt_percent),3)) + '%')



#a refaire avec le new plot des BP 
# def plot_all_event(all_events_tri, all_events_ima, all_E, all_F, runs, subject, subj_nb):
#     from statistics import mean
#     from statistics import median
#     human_rt_mean = []
#     machine_rt_mean = []
#     human_rt_median = []
#     machine_rt_median = []
#     plt.figure(figsize=(19.20, 10.80))
#     for i in range(len(runs)):
#         plt.hist((all_events_tri[i][all_E[i], 0]-all_events_ima[i][all_E[i], 0])/600, bins=20, fc=(0.2, 0.2, 1, 1)) # distribution of reaction time  # noqa
#         plt.hist((all_events_tri[i][all_F[i], 0]-all_events_ima[i][all_F[i], 0])/600, bins=20, fc=(1, 0.2, 0.2, 0.5)) # distribution of random changes of image  # noqa
#         human_rt_mean.append(mean(((all_events_tri[i][all_E[i], 0]-all_events_ima[i][all_E[i], 0])/600)))
#         machine_rt_mean.append(mean(((all_events_tri[i][all_F[i], 0]-all_events_ima[i][all_F[i], 0])/600)))
#         human_rt_median.append(median(((all_events_tri[i][all_E[i], 0]-all_events_ima[i][all_E[i], 0])/600)))
#         machine_rt_median.append(median(((all_events_tri[i][all_F[i], 0]-all_events_ima[i][all_F[i], 0])/600)))
#     mean_diff = abs(mean(human_rt_mean) - mean(machine_rt_mean))
#     median_diff = abs(median(human_rt_median) - median(machine_rt_median))
#     plt.legend(('Button', 'Nothing'))
#     plt.xlabel('Times in second')
#     plt.ylabel('Trials')
#     plt.title(subject + ' Distribution of all events through time (after delete)'
#         + '\nMean difference between Human and Machine : ' + str(round(mean_diff,3))
#         + '\nMedian difference between Human and Machine : ' + str(round(median_diff,3)))

#     #**** save results for corr **** 
#     save_diff_RT = thedirectorydecod('/Users/Fayed/Desktop/PC_STAGE/analysis/scripts/decoding/MEG/MEG_analyzed_data', 'preprocessing/results/') #noqa
#     DiffRT_Mean = op.join(save_diff_RT, '%s_DiffRT_Mean.npy' %(subject))
#     DiffRT_Median = op.join(save_diff_RT, '%s_DiffRT_Median.npy' %(subject))
#     np.save(DiffRT_Mean, mean_diff) 
#     np.save(DiffRT_Median, median_diff)



#a refaire avec le new plot des BP ou laisser le script à part maintenant qu'on save
# def plot_all_event_subj(all_events_tri_subj, all_events_ima_subj, all_E_subj, all_F_subj, total_run):
#     from statistics import mean
#     from statistics import median
#     human_rt_mean = []
#     machine_rt_mean = []
#     human_rt_median = []
#     machine_rt_median = []
#     plt.figure(figsize=(19.20, 10.80))
#     for i in range(total_run):
#         #all_events_tri = tout les events tri de tt les sujets, all_e l'index
#         plt.hist((all_events_tri_subj[i][all_E_subj[i], 0]-all_events_ima_subj[i][all_E_subj[i], 0])/600, bins=5, fc=(0.2, 0.2, 1, 1)) # distribution of reaction time  # noqa
#         plt.hist((all_events_tri_subj[i][all_F_subj[i], 0]-all_events_ima_subj[i][all_F_subj[i], 0])/600, bins=5, fc=(1, 0.2, 0.2, 0.5)) # distribution of random changes of image  # noqa
#         human_rt_mean.append(mean(((all_events_tri_subj[i][all_E_subj[i], 0]-all_events_ima_subj[i][all_E_subj[i], 0])/600)))
#         machine_rt_mean.append(mean(((all_events_tri_subj[i][all_F_subj[i], 0]-all_events_ima_subj[i][all_F_subj[i], 0])/600)))
#         human_rt_median.append(median(((all_events_tri_subj[i][all_E_subj[i], 0]-all_events_ima_subj[i][all_E_subj[i], 0])/600)))
#         machine_rt_median.append(median(((all_events_tri_subj[i][all_F_subj[i], 0]-all_events_ima_subj[i][all_F_subj[i], 0])/600)))
#     mean_diff = abs(mean(human_rt_mean) - mean(machine_rt_mean))
#     median_diff = abs(median(human_rt_median) - median(machine_rt_median))
#     plt.legend(('Bouton', 'Gamma'))
#     plt.xlabel('Temps en millisecondes')
#     plt.ylabel('Essais')
#     # plt.title('all subjects Distribution of all events through time (after delete)'
#     #     + '\nMean difference between Human and Machine : ' + str(round(mean_diff,3))
#     #     + '\nMedian difference between Human and Machine : ' + str(round(median_diff,3)))

#     #**** save results for corr****
#     save_diff_RT = thedirectorydecod('/Users/Fayed/Desktop/PC_STAGE/analysis/scripts/decoding/MEG/MEG_analyzed_data', 'preprocessing/results/')
#     DiffRT_Mean = op.join(save_diff_RT, 'allsubject_DiffRT_Mean.npy')
#     DiffRT_Median = op.join(save_diff_RT, 'allsubject_DiffRT_Median.npy')
#     np.save(DiffRT_Mean, mean_diff) 
#     np.save(DiffRT_Median, median_diff)

