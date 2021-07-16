#######################################################################################################################
######################### File regrouping all the variables used in the agency_task_bci script#########################
#######################################################################################################################

# All the imports needed for the agency script :

# Imports for psychopy
from __future__ import absolute_import, division
from psychopy import gui, visual, core, data, event, logging, parallel,monitors
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)

# Imports for the os and plots and other useful libraries
import os
import os.path as op
import matplotlib.pyplot as plt
import numpy as np
import time
from serial import Serial

# Imports for the pyacq node
from pyacq.core.stream import InputStream
from configs.MEGBuffer import MEGBuffer
from joblib import load



# ******** PARAMETERS TO CHECK AT THE BEGINNING OF THE SESSION **************

# computer (MEG/EEG/MEG_NIH/Marine/Marine_perso/Salim/Fayed/Corentin)
computer = 'Corentin' # MUST BE MEG IF ONLINE


# If not connected to the MEG, everything has to be false except for DEBUG and few_trials
DEBUG = True
trigger = False
eyelink = False
serialPort = False
few_trials = True # False for experiment

# CHOICE_OF_EXPERIMENT = 'S1_random', 'S2_without', 'S2_with'
# 'S1_random' : 
#   Script used for the first session : images only change randomly or after a button press
# 'S2_with' : 
#   The MEGBuffer will try to connect to a fieldtrip buffer : works only if 
#   you are connected to the MEG, or to a virtual fieldtripbuffer (MATLAB script)
#   Images will change depending on the data sent (classifier) or button press
# 'S2_without' : 
#   Used mostly for debugging : no connection to the MEGBuffer will be tried, but you can
#   access all the functions for the second session
CHOICE_OF_EXPERIMENT = 'S2_without' # MYST BE S2_WITH IF ONLINE

# **************END OF PARAMETERS TO CHECK AT THE BEGINNING OF THE SESSION **************



# GUI to define the participant, session and part (if session 2)
# debug mode
if DEBUG:
    fullscr = False
    logging.console.setLevel(logging.DEBUG)
else:
    fullscr = True
    # logging.console.setLevel(logging.WARNING)


if CHOICE_OF_EXPERIMENT == 'S1_random':
    expName = 'AgentivityRandom'
elif CHOICE_OF_EXPERIMENT == 'S2_without':
    expName = 'Agentivity_debug_BCI' # for the BCI part
elif CHOICE_OF_EXPERIMENT == 'S2_with':
    expName = 'Agentivity_BCI' # for the BCI part

# These variables are used for the textStim : windows with text areas to fill
# expInfo is the starting window
# expOk is the window asking if we should change the clf
# expChange is the actual window where you write the changes you want
# expMEGsave is the window where you write the current meg save number
if CHOICE_OF_EXPERIMENT == 'S1_random':
    expInfo = {'participant': '', 'run': ''}
else:
    expInfo = {'MEGsave' : '','participant': '', 'run': '','nbSteps':'', 'part': '', 'classifier': ''}
    expOk = {'OK':''}
    expChange = {'clf':'','nbSteps':''}
    expMEGsave = {'MEGsave':''}

# After the first time you fill in the informations on the first window, these informations are saved
# If it is the first time, we will fill with nothing
try : 
    previousSessionInfos = np.loadtxt('./saves/previousSession.txt',dtype = np.str, delimiter='\n')
    print("Loaded previous session's infos")
except:
    previousSessionInfos = ['','','','','']

# Make sure that the classifiers are in a directory under /classifiers/meg
# Returns the list of the classifiers that are inside that directory
def listClassifiers():
    return (os.listdir('./classifiers/meg'))
listClf = listClassifiers()


clfname = ''
MEGsave = 0

#
# GUI Part : creating the different windows and filling them up 
# 

# The information window : asking for all the informations about the subject
dlg = gui.Dlg(title=expName)
dlg.addField('participant:',previousSessionInfos[0])
dlg.addField('run:',previousSessionInfos[1])
if CHOICE_OF_EXPERIMENT == 'S2_without' or CHOICE_OF_EXPERIMENT == 'S2_with':
    dlg.addField('MEGsave:',previousSessionInfos[3])
    dlg.addField('nbSteps:',previousSessionInfos[2])
    dlg.addField('part:', choices=["part1", "part2","part2_blank"])
    dlg.addField('classifier:', choices=listClf)
    expInfo['participant'], expInfo['run'] , expInfo['MEGsave'] ,expInfo['nbSteps'], expInfo['part'] ,expInfo['classifier'] = dlg.show()  # show dialog and wait for OK or Cancel
else:
    expInfo['participant'], expInfo['run'] = dlg.show()  # show dialog and wait for OK or Cancel
    expInfo['part'] = ''
if dlg.OK is False:  # or if ok_data is not None
    core.quit()  # user pressed cancel


# Saving the informations filled in the information window
savePreviousSession = [expInfo['participant'],expInfo['run'],expInfo['nbSteps'],expInfo['MEGsave'],expMEGsave['MEGsave']]
if not os.path.exists('./saves'):
           os.makedirs('./saves')
np.savetxt('./saves/previousSession.txt',savePreviousSession,fmt='%s')


# The basic 'asking for a change' window
dlgOk = gui.Dlg(title='Do you want to change the classifier ?',screen=1)
dlgOk.addText("Do you want to change the current classifier of its number of steps ?")
dlgOk.addText("Press OK if so, cancel if not")

# The parameters change for the clf window
dlgChange = gui.Dlg(title='Classifier or nbSteps change',screen=1)
dlgChange.addText("Please enter the new values you want, or press cancel")
dlgChange.addField('nbSteps:',previousSessionInfos[2])
dlgChange.addField('classifier:', choices=listClf)

# The megsave window
MEGsave = expInfo['MEGsave']
dlgMEGsave = gui.Dlg(title='Current MEG save file Number',screen=1)
dlgMEGsave.addText("This is the current MEG save run number, please modify it if it changed \n You will have to re-enter it at the beggining of the part2")
dlgMEGsave.addField('MEGsave:',MEGsave)

# Parameters of the information window
expInfo['expName'] = expName
expInfo['date'] = data.getDateStr()  # will create str of current date/time
expInfo['frameRate'] = 60  # store frame rate of monitor
frameDur = 1.0 / 60.0


# image folders
if CHOICE_OF_EXPERIMENT == 'S1_random':
    session_image_choice = 'AgencyImage_session1'
elif expInfo['part'] == 'part1' or expInfo['part'] == 'part2_blank':
    session_image_choice = 'AgencyImage_session2_part1'
elif expInfo['part'] == 'part2':
    session_image_choice = 'AgencyImage_session2_part2'

# Path to save the results
if computer == 'EEG':
    home_folder = '/Users/chercheur/Documents/PythonScripts/Agency_Salim/scripts'  # noqa
elif computer == 'MEG':
    if CHOICE_OF_EXPERIMENT == 'S1_random':
        home_folder = 'C:\\Python_users\\Agency\\scripts' #random session
    else:
        home_folder = 'C:\\Python_users\\Agency\\bci_agency' #bci session
elif computer == 'Marine_perso':
    home_folder = '/Users/marinevernet/Documents/lab_Lyon/python/psychopy/agency'  # noqa
elif computer == 'Salim':
    home_folder = '/Users/Zephyrus/Dropbox/Agency_Salim/scripts'
elif computer == 'Fayed':
    home_folder = '/Users/invitéLabo/Desktop/Fayed/scripts/pscyhopy'
elif computer == 'Fayed2':
    home_folder = '/Users/Fayed/Desktop/PC_STAGE/mne_analysis/scripts/pscyhopy'
elif computer == 'Corentin':
    home_folder = 'C:\\Users\\Coco'

results_folder = home_folder + '/data'

# Data file name
edfFileName = expInfo['participant']+expInfo['run']

if CHOICE_OF_EXPERIMENT == 'S1_random':
    filename = results_folder + '/%s_%s_%s_%s' % (expName, expInfo['participant'],
                                                  expInfo['run'],
                                                  expInfo['date'])

else:
    filename = results_folder + '/%s_%s_%s_%s_%s' % (expName,
                                                     expInfo['participant'],
                                                     expInfo['run'],
                                                     expInfo['part'],
                                                     expInfo['date'])

participant = expInfo['participant']
run_nbr = expInfo['run']


# for the BCI part (S2)
# nb_of_trials_within_little_block = 0 # initialize counter


dictCounterAnswers =	{
  "H_yes": 0,
  "H_no": 0,
  "H_nbw": 0,

  "C_yes": 0,
  "C_no": 0,
  "C_nbw": 0,

  "HB_yes": 0,
  "HB_no": 0,
  "HB_nbw": 0,

  "CB_yes": 0,
  "CB_no": 0,
  "CB_nbw": 0
}

dictCounterAnswersTotal =	{
  "H_yes": 0,
  "H_no": 0,
  "H_nbw": 0,

  "C_yes": 0,
  "C_no": 0,
  "C_nbw": 0,

  "HB_yes": 0,
  "HB_no": 0,
  "HB_nbw": 0,

  "CB_yes": 0,
  "CB_no": 0,
  "CB_nbw": 0
}

nbSteps_chosen = None


# Parameters about the triggers sent depending on the event
if computer == 'EEG':
    window_size = (1024, 768)
    value_parallel_huma = 1
    value_parallel_comp = 2
    value_parallel_huma_early_after_comp = 6
    value_parallel_huma_early_after_huma = 5
    value_parallel_huma_early_after_begin = 4
    value_parallel_huma_early_after_early = 3
    value_answer_yes = 10
    value_answer_no = 30
    value_answer_nbw = 20
    addressPortParallel = '0x0378'
elif computer == 'MEG':  # CHECK THESE PARAMETERS
    window_size = (1920, 1080)
    value_parallel_huma = 20
    value_parallel_comp = 40
    value_parallel_huma_early_after_comp = 10
    value_parallel_huma_early_after_huma = 6
    value_parallel_huma_early_after_begin = 4
    value_parallel_huma_early_after_early = 2
    value_answer_yes = 110
    value_answer_no = 130
    value_answer_nbw = 120
    addressPortParallel = '0x3FE8'
elif computer == 'Marine_perso':
    window_size = (1792, 1120) # old mac (1440, 900)
elif computer == 'Fayed':
    window_size = (1440, 900)
elif computer == 'Fayed2':
    window_size = (1920, 1080)
elif computer == 'Corentin':
    window_size = (1920, 1080)  
if DEBUG:
    window_size = (500, 500)
blank_time = 0.010  # in seconds
# number_of_images = 1500 # max2_trials # 600*2  # up to 1200
image_size = (0.6, 0.6*window_size[0]/window_size[1])


# number of trials TO BE CORRECTED FOR THE REAL EXPERIMENT !!!!!!!!!!!!!!!!!!!
if few_trials:
    nb_trials_before_short_break = 4 # 50
    nb_trials_before_long_break = 8 # 200
    max1_trials = 40 # 1200
    max2_trials = 50 # 1400
elif CHOICE_OF_EXPERIMENT == 'S1_random' or expInfo['part']=='part1' :
    nb_trials_before_short_break = 50 # 50 for S1_random
    nb_trials_before_long_break = 1000 # 200 for S1_random, 1000 for part 1 (infinite so it never ends except when pressing escape)
    max1_trials = 1200 # 1200
    max2_trials = 1400 # 1400
elif CHOICE_OF_EXPERIMENT == 'S2_with' and expInfo['part']=='part2_blank':
    nb_trials_before_short_break = 500 # 50 for S1_random
    nb_trials_before_long_break = 1000 # 200 for S1_random, 1000 for part 1 (infinite so it never ends except when pressing escape)
    max1_trials = 1200 # 1200
    max2_trials = 1400 # 1400
else :
    nb_trials_before_short_break = 20 # 20 for S2
    nb_trials_before_long_break = 80 # 80 for S2
    max1_trials = 1200 # 1200
    max2_trials = 1400 # 1400



print('Going for nb_trials_before_short_break = %d , nb_trials_before_long_break = %d' %(nb_trials_before_short_break ,nb_trials_before_long_break))

# Create some handy timers
imageClock = core.Clock()
blankClock = core.Clock()
longBreackClock = core.Clock()
shortBreackClock = core.Clock()
blankBeforeQuestionClock = core.Clock() # for the BCI part
questionClock = core.Clock() # for the BCI part
globalClock = core.Clock()  # to track the time since experiment started
globalClock.reset()  # clock

# Create the parameters of the gamma function
k_shape = 3
theta_scale = 1

# For part 1
# Count number of button press and number of random changes
button_presses = 0
random_changes = 0
early_button_presses_after_computer = 0
early_button_presses_after_human = 0

# Button presses with resetting count for the part 1 plots
button_presses_bloc = 0
random_changes_bloc = 0
early_button_presses_after_computer_bloc = 0
early_button_presses_after_human_bloc = 0

# Handy variable to know the previous trigger
previousTrigger = ''
timeEarlyBTNPress = 0 # Variable that stores the time when the button was pressed after the image change triggered by the clf
is_there_an_early = 0 # Variable that stores if there was an early button press or not
bloc_nb = 0 # Keeping track of the bloc number we are in (how many short breaks have passed)
threshold600 = 0 # did we reach 600 trials in each category?


###########################################################################################################################
# ***********************************INITIALIZATION OF ALL THE IMAGES, MODULES, WINDOWS etc *******************************
###########################################################################################################################
# Maybe it can be better to put all of this in the configs.config_agency module ?

# Make sure the dir to save images exists
if not os.path.exists('./fig'):
           os.makedirs('./fig')

# set up the ports and Eyelink
if serialPort:
    port_s = serial_port()
if trigger:
    port = parallel.ParallelPort(address=addressPortParallel)
if eyelink:
    import EyeLink #noqa
    selfEdf = EyeLink.tracker(window_size[0], window_size[1], edfFileName)

# list all images
images = list()
files_list = os.listdir(op.join(home_folder, session_image_choice))
for img in files_list:
    if '.jpg' in img:
        if img.startswith('A'):
            images.append(img)


# build trials
conditions = []
for trial in range(len(images)):
    conditions.append({'image_nb': trial})
trials = data.TrialHandler(trialList=conditions, nReps=1, method='random')

# An ExperimentHandler isn't essential but helps with data saving
thisExp = data.ExperimentHandler(dataFileName=filename)
thisExp.addLoop(trials)

# save a log file for detail verbose info
logFile = logging.LogFile(filename+'.log', level=logging.EXP)
logging.console.setLevel(logging.WARNING)  # this outputs to the screen

# Setup the Window
win = visual.Window(
    size=window_size, fullscr=fullscr, screen=0,
    allowGUI=False, allowStencil=False,
    monitor='testMonitor', color=[0, 0, 0], colorSpace='rgb',
    blendMode='avg', useFBO=True)

# Setup the elements to display
White_screen = visual.Rect(
    win=win, name='White_screen', units='cm',
    width=(2000, 2000)[0], height=(2000, 2000)[1],
    ori=0, pos=(0, 0),
    lineWidth=1, lineColor=[1, 1, 1], lineColorSpace='rgb',
    fillColor=[0.5, 0.5, 0.5], fillColorSpace='rgb',
    opacity=1, interpolate=True)
Instructions = visual.TextStim(
    win=win, name='Instructions',
    text='''Une image va apparaitre à l'écran.
            \nPrenez quelques secondes pour l'observer sans bouger les yeux de la croix centrale.
            \nClignez les yeux le moins possible.
            \nPour démarrer, appuyez sur le bouton de droite.''',
    font='Arial',
    pos=(0, 0), height=0.1, wrapWidth=None, ori=0,
    color='black', colorSpace='rgb', opacity=1)
Cross = visual.ShapeStim(
    win=win, name='Cross', vertices='cross', units='cm',
    size=(0.8, 0.8),
    ori=0, pos=(0, 0),
    lineWidth=0.5, lineColor=[1, 0, 0], lineColorSpace='rgb',
    fillColor=[1, 0, 0], fillColorSpace='rgb',
    opacity=1, interpolate=True)
Pixel = visual.Rect(
    win=win, name='topleftpixel', units='pix',
    pos=(-window_size[1], window_size[1]/2),
    size=(window_size[0]*2/5, 200),
    fillColor=[-1, -1, -1],
    lineColor=[-1, -1, -1])

# Initialize components for Routine "image"
fname = op.join(home_folder, session_image_choice, images[1])
Image = visual.ImageStim(
    win, image=fname, pos=(0, 0), size=image_size)
preload_images = [
    visual.ImageStim(win, op.join(home_folder, session_image_choice, img), size=image_size)
    for img in images]

# for the BCI part (part 2) : create the question window
if (CHOICE_OF_EXPERIMENT == 'S2_without' or CHOICE_OF_EXPERIMENT == 'S2_with') and (expInfo['part'] == 'part2' or expInfo['part']== 'part2_blank') :
    if (expInfo['part'] == 'part2'):
        Question = visual.TextStim(win=win, name='Question', text="Avez-vous changé l'image ?",
                                font='Arial', pos=(0, 0.3), height=0.1, wrapWidth=None,
                                ori=0, color='black', colorSpace='rgb', opacity=1)
    else : # If we are in the blank part 2 : participant discovering the buttons and how they work
        Question = visual.TextStim(win=win, name='Question', 
                                text="Avez-vous changé l'image ? \n \n  Utilisez les boutons du haut pour vous déplacer d'un côté à l'autre \n et celui de gauche pour valider !    ",
                                font='Arial', pos=(0, 0.5   ), height=0.1, wrapWidth=None,
                                ori=0, color='black', colorSpace='rgb', opacity=1)
    AnswerYes = visual.TextStim(win=win, name='AnswerYes', text='VOUS',
                                font='Arial', pos=(0, -0.1), height=0.06, wrapWidth=None,
                                ori=0, color='black', colorSpace='rgb', opacity=1)
    AnswerNo = visual.TextStim(win=win, name='AnswerNo', text='ORDI',
                               font='Arial', pos=(0, -0.1), height=0.06, wrapWidth=None,
                               ori=0, color='black', colorSpace='rgb', opacity=1)
    AnswerNoButWanted = visual.TextStim(win=win, name='AnswerNoButWanted', text='ORDI AVANT VOUS',
                               font='Arial', pos=(0, -0.1), height=0.06, wrapWidth=None,
                               ori=0, color='black', colorSpace='rgb', opacity=1)
print('\n')

###########################################################################################################################
# *************************** END OF INITIALIZATION OF ALL THE IMAGES, MODULES, WINDOWS etc *******************************
###########################################################################################################################