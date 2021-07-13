
'''
This is the config used for the scripts
session nb = the number of session  ()
subjects_id = the 
'''

# **** path ************************************************************
computer = 'fayed'  # 'home' 'work' 'biowulf' 'fayed'
if computer == 'ssd':
    path_data = '/Volumes/SSD_Marine/agency/Data_MEG'
    path_analyzed_data = '/Volumes/SSD_Marine/agency/MEG_analyzed_data'
elif computer == 'fayed':
    path_data = '/Users/Fayed/Desktop/StageM2/scripts/decoding/MEG/MEG_data'
    path_analyzed_data = '/Users/Fayed/Desktop/StageM2/scripts/decoding/MEG/MEG_analyzed_data'
    path_saving = '/Users/Fayed/Desktop/StageM2/scripts/decoding/MEG/MEG_save' #where you want to save some file, like clf, trigger etc.

# **** sessionType for scripts agency BCI *****
# sessionType = 'session2_part1','session2_part2'
sessionType = 'session2_part2'

# **** subjects ************************************************************
session_nb = 1
# subjects_id = ['MAR', 'SAL', 'FAY', '0986', '0987', '0989', '0990', '0991', '0992', '0993', '0994', '0995', '0996'] #all session 1
subjects_id = ['0986', '0987', '0989', '0990', '0991', '0992', '0993', '0994', '0995', '0996'] #subject without pilot
# subjects_id = ['0986', '0987', '0989', '0990', '0991', '0992', '0993', '0994'] #subject memoire

# session_nb = 2
subjects_id = ['MAR2', 'SAL2', 'FAY2', '1059', '1060', '1061', '1062'] #all session 2

#**** group of subject by session ****
# session_nb = 1 
# subjects_id = ['MAR', 'SAL', 'FAY'] #pilot
# subjects_id = ['0986', '0987'] #18 mars
# subjects_id = ['0989', '0990', '0991'] #15 avril
# subjects_id = ['0992', '0993', '0994', '0995' ] #29 avril
# subjects_id = ['0996'] #20 mai

# session_nb = 2
# subjects_id = ['FAY_test'] #20 mai
# subjects_id = ['MAR2', 'FAY2'] #03 juin
# subjects_id = ['1059', '1060', '1061'] #24 juin
# subjects_id = ['SAL2', '1062'] #08 juillet


#**** each subject ****
#12 décembre
# subjects_id = ['MAR'] 
# subjects_id = ['SAL']

#18 février
# subjects_id = ['FAY'] 

#18 mars
# subjects_id = ['0986'] #RJ weird event on file 04.ds #1059
# subjects_id = ['0987'] #AEG  #1060

#15 avril
# subjects_id = ['0989'] #MY #1062
# subjects_id = ['0990'] #TZ not very good decoding for this subject
# subjects_id = ['0991'] #MA #1061

#29 avril
# subjects_id = ['0992'] #ES 
# # subjects_id = ['0993'] #DAA
# subjects_id = ['0994'] #CC press too fast BP, many BP in a row.
# subjects_id = ['0995'] #DC bad eye tracker, last file only 50 trial, weird RP. 

#20 mai 
# subjects_id = ['0996'] #LB
# subjects_id = ['FAY_test'] #pilot : test bci for the 1st time.


#03 juin
# session_nb = 2
# subjects_id = ['MAR2'] #pilot
# subjects_id = ['FAY2'] #pilot

# 24 juin
# session_nb = 2
subjects_id = ['1059'] #RJ emg can't analyse yet
subjects_id = ['1060'] #AEG
# subjects_id = ['1061'] #MA

#08 juillet
# session_nb = 2
# subjects_id = ['SAL2'] #pilot
# subjects_id = ['1062'] #MY

# **** sessions ************************************************************
session_nb = 1
# session_subject = [['MAR20201210_session1'], ['SAL20201210_session1'], ['FA20210218_session1'],['RJ20210318_session1'], ['AEG20210318_session1'], ['MY20210415_session1'],
#                     ['TZ20210415_session1'], ['MA20210415_session1'], ['ES20210429_session1'], ['DAA20210429_session1'], ['CC20210429_session1'], ['DC20210429_session1'], ['LB20210520_session1']] #all session 1

session_subject = [['RJ20210318_session1'], ['AEG20210318_session1'], ['MY20210415_session1'], ['TZ20210415_session1'], ['MA20210415_session1'],
                    ['ES20210429_session1'], ['DAA20210429_session1'], ['CC20210429_session1'], ['DC20210429_session1'], ['LB20210520_session1']] #subject without pilot

# session_subject = [['RJ20210318_session1'], ['AEG20210318_session1'], ['MY20210415_session1'], ['TZ20210415_session1'], ['MA20210415_session1'],
#                     ['ES20210429_session1'], ['DAA20210429_session1'], ['CC20210429_session1']] #subject memoire 


session_nb = 2
session_subject = [['MAR20210603_session2'], ['SAL20210708_session2'], ['FA20210603_session2'],  ['RJ20210624_session2'], ['AEG20210624_session2'], ['MA20210624_session2'], ['MY20210708_session2']] #all session 2

#**** group of subject by session ****
# session_nb = 1
# session_subject = [['MAR20201210'], ['SAL20201210'], ['FA20210218']] #pilot
# session_subject = [['RJ20210318_session1'], ['AEG20210318_session1']] #18 mars
# session_subject = [['MY20210415_session1'], ['TZ20210415_session1'], ['MA20210415_session1']] #15 avril
# session_subject = [['ES20210429_session1'], ['DAA20210429_session1'], ['CC20210429_session1'], ['DC20210429_session1']] #29 avril
# session_subject = [['LB20210520_session1']] #20 mai

# session_nb = 2
# session_subject = [['FA20210520_session2_test']] #20 mai
# session_subject = [['MAR20210603_session2'], ['FA20210603_session2']] #03 juin
# session_subject = [['RJ20210624_session2'], ['AEG20210624_session2'], ['MA20210624_session2']] #24 juin
# session_subject = [['SAL20210708_session2'], ['MY20210708_session2']] #08 juillet

#**** each subject ****
#12 décembre
# session_subject = [['MAR20201210_session1']]
# session_subject = [['SAL20201210_session1']]

# #18 février
# session_subject = [['FA20210218_session1']]

#18 mars
# session_subject = [['RJ20210318_session1']]
# session_subject = [['AEG20210318_session1']]

#15 avril
# session_subject = [['MY20210415_session1']]
# # session_subject = [['TZ20210415_session1']]
# session_subject = [['MA20210415_session1']]

#29 avril
# session_subject = [['ES20210429_session1']]
# session_subject = [['DAA20210429_session1']]
# session_subject = [['CC20210429_session1']]
# session_subject = [['DC20210429_session1']] 

#20 mai
# session_subject = [['LB20210520_session1']]
# session_subject = [['FA20210520_session2_test']]

#03 juin
# session_subject = [['MAR20210603_session2']]
# session_subject = [['FA20210603_session2']]

#24 juin
session_subject = [['RJ20210624_session2']]
session_subject = [['AEG20210624_session2']]
# session_subject = [['MA20210624_session2']]

#08 juillet
# session_subject = [['SAL20210708_session2']]
# session_subject = [['MY20210708_session2']]


# **** file ************************************************************
files_to_ana = ['agency']

# **** which channels to decode *****************************************
which_channels = 'meg'
# which_channels = 'meg&ref'
# which_channels = 'meg&emg'
# which_channels = 'meg&pupil'
# which_channels = 'meg&eyes'

# which_channels = 'motor'
# which_channels = 'mlc'
# which_channels = 'mrc'

# which_channels = 'eyes'
# which_channels = 'pupil'
# which_channels = 'trigger'
# which_channels = 'emg'


# what = 'trigger'
def thedirectory(path_saving, what): #where we save and what we save
    if what == 'trigger':
        directory = op.join(path_saving, 'trigger')
    if not op.exists(directory):
        # print "directory"
        os.mkdir(directory)
    return directory

