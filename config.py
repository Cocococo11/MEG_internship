

# **** path ************************************************************


computer = 'corentin'  # 'home' 'work' 'biowulf' 'fayed'
if computer is 'ssd':
    path_data = '/Volumes/SSD_Marine/agency/Data_MEG'
    path_analyzed_data = '/Volumes/SSD_Marine/agency/MEG_analyzed_data'
elif computer is 'fayed':
    path_data = '/Users/Fayed/Desktop/PC_STAGE/analysis/scripts/decoding/MEG/MEG_data'
    path_analyzed_data = '/Users/Fayed/Desktop/PC_STAGE/analysis/scripts/decoding/MEG/MEG_analyzed_data'
    path_saving = '/Users/Fayed/Desktop/PC_STAGE/analysis/scripts/decoding/MEG/agency_scripts_meg_0507'
elif computer is 'corentin':
    path_data = '/Users/Coco/Desktop/simple-megbuffer and script/data'
    #path_analyzed_data =  #pas besoin ici
    path_saving = '/Users/Coco/Desktop/simple-megbuffer and script/saves'

# sessionType = 'session2_part1','session2_part2'
sessionType = 'session2_part2'
 
# **** subjects ************************************************************
# subjects_id = ['MAR', 'SAL', 'FAY',
# 			   '0986', '0987',
# 			   '0989', '0990', '0991',
# 			   '0992', '0993', '0994', '0995'] #all

#garde cette ligne si tu veux extraire tout nos sujets, si tu veux prendre un seul sujet decommente la ligne en dessous
# subjects_id = ['0986', '0987', '0989', '0990', '0991', '0992', '0993', '0994', '0995'] #our real subject
subjects_id = ['fa'] #only fayed
#**** regroupé par session ****
# subjects_id = ['MAR', 'SAL', 'FAY'] # old subject
# subjects_id = ['0986', '0987'] #18 mars
# subjects_id = ['0989', '0990', '0991'] #15 avril
# subjects_id = ['0992', '0993', '0994', '0995' ] #29 avril

#**** sujet par sujet ****
# #old
# # subjects_id = ['MAR']
# # subjects_id = ['SAL']
# subjects_id = ['FAY']

#15mars
# subjects_id = ['0986'] #RJ
# subjects_id = ['0987'] #AEG

# subjects_id = ['0989'] #MY
# # subjects_id = ['0990'] #TZ
# subjects_id = ['0991'] #MA

#29 avril
# subjects_id = ['0992'] #ES 
# subjects_id = ['0993'] #DAA
# subjects_id = ['0994'] #CC press too fast BP, many BP a la suite
# subjects_id = ['0995'] #DC bad eye tracker, last file only 50 trial

#20 mai
# subjects_id = ['0996'] #LB

# **** sessions ************************************************************
# session_subject = [['Marine20201210'], ['Salim20201210'], ['Fayed20210218'],
# 					['RJ20210318'], ['AEG20210318'],
# 					['MY20210415'], ['TZ20210415'], ['MA20210415'],
# 					['ES20210429'], ['DAA20210429'], ['CC20210429'], ['DC20210429']] #all

# session_subject = [['RJ20210318'], ['AEG20210318'], ['MY20210415'], ['TZ20210415'], ['MA20210415'], ['ES20210429'], ['DAA20210429'], ['CC20210429'], ['DC20210429']] #our real subject
session_subject = [['20210603']] #our real subject

# # session_subject = [['Marine20201210'], ['Salim20201210'], ['Fayed20210218']]
# session_subject = [['RJ20210318'], ['AEG20210318']]
# #session_subject = [['MY20210415'], ['TZ20210415'], ['MA20210415']]
# # session_subject = [['ES20210429'], ['DAA20210429'], ['CC20210429'], ['DC20210429']]

# # session_subject = [['Marine20201210']]
# # session_subject = [['Salim20201210']]
# session_subject = [['Fayed20210218']]

# session_subject = [['RJ20210318']]
# # session_subject = [['AEG20210318']]

# session_subject = [['MY20210415']]
# # session_subject = [['TZ20210415']]
# session_subject = [['MA20210415']]

# session_subject = [['ES20210429']]
# session_subject = [['DAA20210429']]
# session_subject = [['CC20210429']]
# session_subject = [['DC20210429']] 
# session_subject = [['LB20210520']]


# **** file ************************************************************
files_to_ana = ['agency']

# **** which channels to decode *****************************************
what = 'trigger'

 #petite fonction pour faciliter le save des data
def thedirectory(path_saving, what): #where we save and what we save
    if what == 'trigger':
        directory = op.join(path_saving, 'trigger')
    if not op.exists(directory):
        # print "directory"
        os.mkdir(directory)
    return directory

