# Code written by Romain Quentin and Marine Vernet
# Modified by Fayed Rassoulou
# Integration of FieldTrip Buffer by Corentin Bel

# -*- coding: utf-8 -*-
from __future__ import absolute_import, division
from psychopy import gui, visual, core, data, event, logging, parallel
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)
import os
import os.path as op
import matplotlib.pyplot as plt

#imports for the pyacq node
from pyacq.core.stream import InputStream
from MEGBuffer import MEGBuffer
from joblib import load

# import yaml
import numpy as np
import time

from serial import Serial

# In case you're tired of avbin.dll
# import warnings
# warnings.filterwarnings("ignore")
# /!\


def serial_port(port='COM1', baudrate=9600, timeout=0):
    """
    Create serial port interface.

    :param str port:
        Which port to interface with.
    :param baudrate:
        Rate at which information is transferred in bits per second.
    :param int timeout:
        Waiting time in seconds for the port to respond.
    :return: serial port interface
    """
    open_port = Serial(port, baudrate, timeout=timeout)
    open_port.close()
    open_port = Serial(port, baudrate, timeout=timeout)
    open_port.flush()
    return open_port

def printTiming(trials, clock, taskEvent):
    trials.addData(taskEvent, clock.getTime())

# !!Make sure that the classifiers are in a directory under /classifiers
def listClassifiers():
    return (os.listdir('./classifiers'))
# def plotDict(dict):
#     listKeys = dict.keys()
#     values = dict.values()
#     plt.bar(listKeys,values,color=['lightcoral','indianred','brown','olive','olivedrab','yellowgreen','magenta','orchid','hotpink','darkorange','goldenrod','moccasin'])
#     plt.title("Early results of button presses")
#     plt.show()

def plotDict2(dict):
    A = [dictCounterAnswers['H_yes'], dictCounterAnswers['C_yes'], dictCounterAnswers['HB_yes'], dictCounterAnswers['CB_yes']]
    B = [dictCounterAnswers['H_no'],  dictCounterAnswers['C_no'],  dictCounterAnswers['HB_no'],  dictCounterAnswers['CB_no']]
    C = [dictCounterAnswers['H_nbw'], dictCounterAnswers['C_nbw'], dictCounterAnswers['HB_nbw'], dictCounterAnswers['CB_nbw']]
    X = ['Hum', 'Comp', 'Hum+But', 'Comp+But']
    plt.bar(X, A, color = 'brown', label='yes')
    plt.bar(X, B, color = 'olive', bottom = A, label='no')
    plt.bar(X, C, color = 'darkorange', bottom = np.sum([A, B], axis=0), label='nbw')
    plt.legend()
    plt.show()

def closeMEGB():
    if (CHOICE_OF_EXPERIMENT == 'S2_with'):
        MEGB.stop()
        inputStream.close()
        MEGB.close()

def prepare_pie_plot(button_presses, random_changes, early_button_presses_after_computer, early_button_presses_after_human, nb_trials):
    print('\n' + 'Since the start of the recordings:')
    print('rate of human changes: ', str(button_presses - early_button_presses_after_human), '/', str(nb_trials), ' = ', str((button_presses-early_button_presses_after_human)/nb_trials))
    print('rate of computer changes: ', str(random_changes - early_button_presses_after_computer), '/', str(nb_trials), ' = ', str((random_changes-early_button_presses_after_computer)/nb_trials))
    print('rate of early button presses after computer: ', str(early_button_presses_after_computer), '/', str(nb_trials), ' = ', str(early_button_presses_after_computer/nb_trials))
    print('rate of early button presses after human: ', str(early_button_presses_after_human), '/', str(nb_trials), ' = ', str(early_button_presses_after_human/nb_trials))
    print('\n')
    if button_presses-early_button_presses_after_human != 0:
        pietoplot = [button_presses-early_button_presses_after_human]
        pielabels = ['human']
    else:
        pietoplot = []
        pielabels = []
    if random_changes-early_button_presses_after_computer != 0:
        pietoplot.append(random_changes-early_button_presses_after_computer)
        pielabels.append('computer')
    if early_button_presses_after_computer != 0:
        pietoplot.append(early_button_presses_after_computer)
        pielabels.append('early BP after computer')
    if early_button_presses_after_human != 0:
        pietoplot.append(early_button_presses_after_human)
        pielabels.append('early BP after human')
    return pietoplot, pielabels


# ******** PARAMETERS TO CHECK AT THE BEGINNING OF THE SESSION **************

# computer (MEG/EEG/MEG_NIH/Marine/Marine_perso/Salim/Fayed)
computer = 'Corentin'

DEBUG = True
trigger = False
eyelink = False
serialPort = False
few_trials = False

# CHOICE_OF_EXPERIMENT = 'S1_random', 'S2_without', 'S2_with'
CHOICE_OF_EXPERIMENT = 'S2_without'

threshold600 = 0 # did we reach 600 trials in each category?
nbPred = 0 # for 'S2_with'

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

if CHOICE_OF_EXPERIMENT == 'S1_random':
    expInfo = {'participant': '', 'run': ''}
else:
    expInfo = {'participant': '', 'run': '','nbSteps':'', 'part': '', 'classifier': ''}


dlg = gui.Dlg(title=expName)
dlg.addField('participant:')
dlg.addField('run:')
if CHOICE_OF_EXPERIMENT == 'S2_without' or CHOICE_OF_EXPERIMENT == 'S2_with':
    dlg.addField('nbSteps:')
    dlg.addField('part:', choices=["part1", "part2"])
    listClf = listClassifiers()
    dlg.addField('classifier:', choices=listClf)
    expInfo['participant'], expInfo['run'] , expInfo['nbSteps'], expInfo['part'] ,expInfo['classifier'] = dlg.show()  # show dialog and wait for OK or Cancel
else:
    expInfo['participant'], expInfo['run'] = dlg.show()  # show dialog and wait for OK or Cancel
    expInfo['part'] = ''
if dlg.OK is False:  # or if ok_data is not None
    core.quit()  # user pressed cancel

expInfo['expName'] = expName
expInfo['date'] = data.getDateStr()  # will create str of current date/time
expInfo['frameRate'] = 60  # store frame rate of monitor
frameDur = 1.0 / 60.0

# number of trials TO BE CORRECTED FOR THE REAL EXPERIMENT !!!!!!!!!!!!!!!!!!!
if few_trials:
    nb_trials_before_short_break = 20 # 50
    nb_trials_before_long_break = 80 # 200
    max1_trials = 40 # 1200
    max2_trials = 50 # 1400
elif CHOICE_OF_EXPERIMENT == 'S1_random' or expInfo['part']=='part1' :
    nb_trials_before_short_break = 50 # 50 for S1_random
    nb_trials_before_long_break = 200 # 200 for S1_random,
    max1_trials = 1200 # 1200
    max2_trials = 1400 # 1400
else :
    nb_trials_before_short_break = 20 # 20 for S2
    nb_trials_before_long_break = 80 # 80 for S2
    max1_trials = 1200 # 1200
    max2_trials = 1400 # 1400

print('Going for nb_trials_before_short_break = %d , nb_trials_before_long_break = %d' %(nb_trials_before_short_break ,nb_trials_before_long_break))
# image folders
if CHOICE_OF_EXPERIMENT == 'S1_random':
    session_image_choice = 'AgencyImage_session1'
elif expInfo['part'] == 'part1':
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


# ******** END OF PARAMETERS TO CHECK AT THE BEGINNING OF THE SESSION ********

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


# params
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
if DEBUG:
    window_size = (500, 500)
blank_time = 0.010  # in seconds
# number_of_images = 1500 # max2_trials # 600*2  # up to 1200
image_size = (0.6, 0.6*window_size[0]/window_size[1])

# set up the ports and Eyelink
if serialPort:
    port_s = serial_port()
if trigger:
    port = parallel.ParallelPort(address=addressPortParallel)
if eyelink:
    import EyeLink
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

# for the BCI part (part 2)
if (CHOICE_OF_EXPERIMENT == 'S2_without' or CHOICE_OF_EXPERIMENT == 'S2_with') and expInfo['part'] == 'part2':
    Question = visual.TextStim(win=win, name='Question', text="Avez-vous changé l'image ?",
                               font='Arial', pos=(0, 0.3), height=0.1, wrapWidth=None,
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

# Count number of button press and number of random changes
button_presses = 0
random_changes = 0
early_button_presses_after_computer = 0
early_button_presses_after_human = 0

# # Count number of yes and no response (for the BCI part)
# button_yes = 0
# button_no = 0
# button_no_but_wanted = 0

# Handy variable to know the previous trigger
previousTrigger = ''
timeEarlyBTNPress = 0
is_there_an_early = 0

print('\n')


if CHOICE_OF_EXPERIMENT == 'S2_with':
    #Loading the MEGBuffer node
    MEGB =  MEGBuffer()
    inputStream = InputStream()
    nbSteps_chosen = expInfo['nbSteps']
    clfname = expInfo['classifier']
    MEGB.configure(nb_steps_chosen =nbSteps_chosen,clf_name =clfname )

    MEGB.outputs['signals'].configure( transfermode='plaindata')
    MEGB.outputs['triggers'].configure( transfermode='plaindata')
    MEGB.initialize()

    inputStream.connect(MEGB.outputs['signals'])

    MEGB.start()


# ------Prepare to start Routine "Instructions"-------
continueRoutine = True
White_screen.setAutoDraw(True)
Instructions.setAutoDraw(True)
Pixel.setAutoDraw(True)

# -------Start Routine "Instructions"-------
key_from_serial = []
key_from_serial2 = ''
win.flip()
while continueRoutine:
    if serialPort:
        key_from_serial2 = str(port_s.readline())[2:-1]
        if len(key_from_serial2) > 0:
            key_from_serial2 = key_from_serial2[-1]
        if key_from_serial2 == '2':
            Instructions.setAutoDraw(False)
            continueRoutine = False
    if event.getKeys(keyList=['y']):
        Instructions.setAutoDraw(False)
        continueRoutine = False
    if event.getKeys(keyList=["escape"]):
        thisExp.saveAsWideText(filename+'.csv')
        thisExp.saveAsPickle(filename)
        if eyelink:
            EyeLink.tracker.close(selfEdf, edfFileName)
        closeMEGB()
        win.close()
        core.quit()

# Start MEG recordings
if trigger:
    port.setData(0)
    time.sleep(0.1)
    port.setData(252)


# Start the trials
for trial in trials:

    # ------ Stop the recordings and close everything for S2 part 1 -------
    if (CHOICE_OF_EXPERIMENT == 'S2_without' or CHOICE_OF_EXPERIMENT == 'S2_with') and expInfo['part'] == 'part1' and \
       (trials.thisN % nb_trials_before_long_break) == 0 and trials.thisN != 0:

        # Stop MEG recordings
        if trigger:
            time.sleep(1)
            port.setData(253)
            time.sleep(1)
            port.setData(0)

        end_text = 'Pause ! Veuillez ne pas bouger et attendre les instructions. \n\nVous pouvez fermer les yeux.'
        Instructions.setText(end_text)
        Instructions.setAutoDraw(True)
        Cross.setAutoDraw(False)
        win.flip()

        pietoplot, pielabels = prepare_pie_plot(button_presses, random_changes, early_button_presses_after_computer, early_button_presses_after_human, trials.thisN)
        plt.pie(pietoplot,labels=pielabels)
        plt.show()

        time.sleep(5)
        thisExp.saveAsWideText(filename+'.csv')
        thisExp.saveAsPickle(filename)
        if eyelink:
            EyeLink.tracker.close(selfEdf, edfFileName)
        win.close()
        core.quit()


    # ------Condition for Long Break-------
    if (CHOICE_OF_EXPERIMENT == 'S1_random' or expInfo['part'] == 'part2') and \
       ((trials.thisN % nb_trials_before_long_break) == 0 and trials.thisN != 0 and trials.thisN < max1_trials) or \
       (button_presses >= max1_trials/2 and random_changes >= max1_trials/2 and threshold600 == 0) or \
       (button_presses >= max2_trials/2 and random_changes >= max2_trials/2):

        # ------Prepare to start Routine "Long Break"-------
        continueRoutine = True
        if ((trials.thisN % nb_trials_before_long_break) == 0 and trials.thisN != 0 and trials.thisN < max1_trials):
            long_break_text = 'Pause ! Veuillez ne pas bouger et attendre les instructions. \n\nVous pouvez fermer les yeux.'
        elif (button_presses >= max1_trials/2 and random_changes >= max1_trials/2 and threshold600 == 0) or (button_presses >= max2_trials/2 and random_changes >= max2_trials/2):
            long_break_text = 'Presque fini ! Veuillez ne pas bouger et attendre les instructions \n\nVous pouvez fermer les yeux.'
            threshold600 = 1
        Instructions.setText(long_break_text)
        Instructions.setAutoDraw(True)
        Cross.setAutoDraw(False)
        win.callOnFlip(longBreackClock.reset)

        # -------Start Routine "Long Break"-------
        win.flip()
        if CHOICE_OF_EXPERIMENT == 'S1_random':
            print('Long break') # for the random part
            print('Partipant : ' + str(button_presses) + '\nOrdinateur : ' + str(random_changes) + '\n') # for the random part
            print('Participant-Ordinateur : ' + str(button_presses-random_changes) + '\n') # for the random part
        key_from_serial = []
        key_from_serial2 = ''

        # Stop MEG recordings
        if trigger:
            time.sleep(1)
            port.setData(253)
            time.sleep(1)
            port.setData(0)

        if button_presses >= max2_trials/2 and random_changes >= max2_trials/2:
            time.sleep(5)
            thisExp.saveAsWideText(filename+'.csv')
            thisExp.saveAsPickle(filename)
            if eyelink:
                EyeLink.tracker.close(selfEdf, edfFileName)
            win.close()
            core.quit()

        while continueRoutine:
            if event.getKeys(keyList=['a']):
                Instructions.setAutoDraw(False)
                continueRoutine = False
                # win.flip()
            if event.getKeys(keyList=["escape"]):
                thisExp.saveAsWideText(filename+'.csv')
                thisExp.saveAsPickle(filename)
                if eyelink:
                    EyeLink.tracker.close(selfEdf, edfFileName)
                closeMEGB()
                win.close()
                core.quit()

        # Start MEG recordings
        if trigger:
            port.setData(252)

    event.clearEvents(eventType='keyboard')

    # ------Condition for Short Break-------
    if (trials.thisN % nb_trials_before_short_break) == 0 and trials.thisN != 0:

        # ------Prepare to start Routine "Short Break"-------
        continueRoutine = True
        if CHOICE_OF_EXPERIMENT == 'S1_random':
            difference = button_presses - random_changes
            if difference > 6:
                break_text = "Petite pause ! \n\n Vous répondez trop souvent par rapport à l'ordinateur. \nAppuyez moins souvent. \n\n Pour continuer, appuyez sur le bouton de droite."
            elif difference < -6:
                break_text = "Petite pause ! \n\n Vous ne répondez pas assez souvent par rapport à l'ordinateur. \nAppuyez plus souvent. \n\n Pour continuer, appuyez sur le bouton de droite."
            else:
                break_text = "Petite pause ! \n\n Vous répondez aussi souvent que l'ordinateur, bravo ! \n\n Pour continuer, appuyez sur le bouton de droite."
            # break_text = 'Petite pause !' + '\n\nVous : ' + str(button_presses) + '\n\n Ordinateur : ' + str(random_changes) + '\n\n Appuyez sur le bouton de droite pour continuer.'  # for the random part
        else: # for the BCI part
            break_text = 'Petite pause \n\n Veuillez ne pas bouger et attendre les instructions'  # for the BCI part

        Instructions.setText(break_text)
        Instructions.setAutoDraw(True)
        Pixel.setAutoDraw(True)
        Cross.setAutoDraw(False)
        win.callOnFlip(shortBreackClock.reset)
        continueRoutine = True

        # -------Start Routine "Short Break"-------
        win.flip()

        if CHOICE_OF_EXPERIMENT == 'S1_random':
            print('Partipant : ' + str(button_presses) + '\nOrdinateur : ' + str(random_changes) + '\n') # for the random part
            print('Participant-Ordinateur : ' + str(button_presses-random_changes) + '\n') # for the random part
        else:
            if expInfo['part'] == 'part2': # max(dictCounterAnswers.values())>0 :
                plotDict2(dictCounterAnswers)
                # print(yaml.dump(dictCounterAnswers, sort_keys=False, default_flow_style=False))
            elif expInfo['part'] == 'part1':
                pietoplot, pielabels = prepare_pie_plot(button_presses, random_changes, early_button_presses_after_computer, early_button_presses_after_human, trials.thisN)
                plt.pie(pietoplot,labels=pielabels)
                plt.show()
            # nb_of_trials_within_little_block = 0

        key_from_serial = []
        key_from_serial2 = ''

        while continueRoutine:
            if serialPort:
                key_from_serial2 = str(port_s.readline())[2:-1]
                if len(key_from_serial2) > 0:
                    key_from_serial2 = key_from_serial2[-1]
                if key_from_serial2 == '2' and CHOICE_OF_EXPERIMENT == 'S1_random':
                    Instructions.setAutoDraw(False)
                    continueRoutine = False
            if (event.getKeys(keyList=['y']) and CHOICE_OF_EXPERIMENT == 'S1_random') or \
               (event.getKeys(keyList=['a']) and (CHOICE_OF_EXPERIMENT == 'S2_with' or CHOICE_OF_EXPERIMENT == 'S2_without')):
                Instructions.setAutoDraw(False)
                continueRoutine = False
            if event.getKeys(keyList=["escape"]):
                thisExp.saveAsWideText(filename+'.csv')
                thisExp.saveAsPickle(filename)
                if eyelink:
                    EyeLink.tracker.close(selfEdf, edfFileName)
                closeMEGB()
                win.close()
                core.quit()
            if shortBreackClock.getTime() > 30 and CHOICE_OF_EXPERIMENT == 'S1_random':  # noqa
                Instructions.setAutoDraw(False)
                continueRoutine = False

    # ------Prepare to start Routine "Blank"-------
    continueRoutine = True
    Cross.setAutoDraw(True)

    # -------Start Routine "Blank"-------
    win.callOnFlip(blankClock.reset)
    win.callOnFlip(printTiming, trials, globalClock, 'globalTiming')
    win.flip()
    if trigger:
        port.setData(0)
    while continueRoutine:
        frameRemains = blank_time - win.monitorFramePeriod * 0.75  # most of one frame period left   # noqa
        if blankClock.getTime() >= frameRemains:
            Cross.setAutoDraw(False)
            continueRoutine = False
        if event.getKeys(keyList=["escape"]):
            thisExp.saveAsWideText(filename+'.csv')
            thisExp.saveAsPickle(filename)
            if eyelink:
                EyeLink.tracker.close(selfEdf, edfFileName)
            closeMEGB()
            win.close()
            core.quit()

    # ------Prepare to start Routine "Image"-------
    preload_images[trial['image_nb']].setAutoDraw(True)
    Cross.setAutoDraw(True)
    Pixel.setAutoDraw(False)
    event.clearEvents(eventType='keyboard')

    # # Increase nb of trials (for the BCI part)
    # if CHOICE_OF_EXPERIMENT == 'S2_without' or CHOICE_OF_EXPERIMENT == 'S2_with':
    #     nb_of_trials_within_little_block += 1

    # -------Start Routine "Image"-------
    win.callOnFlip(imageClock.reset)
    win.callOnFlip(printTiming, trials, blankClock, 'blank')
    win.flip()

    keyPress = []
    key_from_serial = []
    key_from_serial2 = ''
    is_there_an_early = 0
    frameRemainsRT = np.maximum(0.5, np.random.gamma(k_shape, scale=theta_scale, size=1))  # noqa

    if CHOICE_OF_EXPERIMENT == 'S2_with':
        detectPrep = False
        inputStream.empty_queue()
        cond_for_loop = True
    else:
        if (imageClock.getTime() < frameRemainsRT):
            cond_for_loop = True
        else:
            cond_for_loop = False

    ActiveStatus = 0

    while cond_for_loop:  # noqa
        if trigger :
            port.setData(0)

        #MEGBuffer Part
        # Polling and receiving the data sent by the MEGBuffer node
        if (CHOICE_OF_EXPERIMENT == 'S2_with') and (imageClock.getTime() > 0.5):
            try :
                inputStream.empty_queue()
                dataIsAvailable = inputStream.poll(1000)
            except :
                print("Error with polling the input stream")
                break

            #nbPaquetsToTest = 10000 #  represents the number of packages of 24 we want to test
            if(dataIsAvailable):
                data = inputStream.recv() # Pulling the data from the
                # print(data)
                # print(time.time())
                if( data[1][0] == 1):
                    if trigger:
                        port.setData(value_parallel_comp)
                    if eyelink:
                        EyeLink.tracker.sendMessage(selfEdf, 'C')
                    RT = imageClock.getTime()
                    ActiveStatus = 0
                    random_changes += 1
                    nbPred+=1
                    detectPrep = True
                    cond_for_loop=False
                    print('computer change')
                    previousTrigger  = 'C'
                    preload_images[trial['image_nb']].setAutoDraw(False)
                    Pixel.setAutoDraw(True)

        if serialPort:  # and (imageClock.getTime() > 0.5):
            key_from_serial2 = str(port_s.readline())[2:-1]
            if len(key_from_serial2) > 0:
                key_from_serial2 = key_from_serial2[-1]
        keyPress = event.getKeys(keyList=['r', 'escape'])

        if ((keyPress and keyPress[0][0] == 'r') or key_from_serial2 == '1'):

            if imageClock.getTime() > 0.5 or CHOICE_OF_EXPERIMENT == 'S1_random' :
                if trigger:
                    port.setData(value_parallel_huma)
                if eyelink:
                    EyeLink.tracker.sendMessage(selfEdf, 'H')
                previousTrigger = 'H'
                print("Human Change")
                preload_images[trial['image_nb']].setAutoDraw(False)
                Pixel.setAutoDraw(True)
                RT = imageClock.getTime()
                # RT = keyPress[0][1]
                ActiveStatus = 1
                button_presses += 1
                cond_for_loop = False
            else:
                if previousTrigger == '':
                    if trigger:
                        port.setData(value_parallel_huma_early_after_begin)
                    print("Early BP after beginning!")
                if previousTrigger == 'H':
                    if trigger:
                        port.setData(value_parallel_huma_early_after_huma)
                    print("Early BP after human")
                    is_there_an_early += 1
                    early_button_presses_after_human += 1
                    previousTrigger='HB'
                elif previousTrigger == 'C':
                    if trigger:
                        port.setData(value_parallel_huma_early_after_comp)
                    print("Early BP after computer")
                    is_there_an_early += 1
                    early_button_presses_after_computer += 1
                    previousTrigger='CB'
                elif previousTrigger == 'HB' or previousTrigger == 'CB':
                    if trigger:
                        port.setData(value_parallel_huma_early_after_early)
                    print("Early BP after early!")

                if eyelink:
                    EyeLink.tracker.sendMessage(selfEdf, 'E')
                timeEarlyBTNPress = imageClock.getTime()

        if (keyPress and keyPress[0][0] == 'escape'):
            thisExp.saveAsWideText(filename+'.csv')
            thisExp.saveAsPickle(filename)
            if eyelink:
                EyeLink.tracker.close(selfEdf, edfFileName)
            closeMEGB()
            win.close()
            core.quit()

        if (imageClock.getTime() > frameRemainsRT) and (CHOICE_OF_EXPERIMENT == 'S1_random' or CHOICE_OF_EXPERIMENT == 'S2_without'):
            cond_for_loop = False
            if trigger:
                port.setData(value_parallel_comp)
            if eyelink:
                EyeLink.tracker.sendMessage(selfEdf, 'C')
            print('computer change')
            previousTrigger  = 'C'
            preload_images[trial['image_nb']].setAutoDraw(False)
            Pixel.setAutoDraw(True)
            RT = frameRemainsRT[0]
            ActiveStatus = 0
            random_changes += 1

    win.callOnFlip(printTiming, trials, imageClock, 'image')
    win.flip()

    if trigger :
        port.setData(0)


    # ------Condition for Question, BCI part (part 2) -------
    if (CHOICE_OF_EXPERIMENT == 'S2_without' or CHOICE_OF_EXPERIMENT == 'S2_with') and expInfo['part'] == 'part2':

        if trigger :
            port.setData(0)
        win.callOnFlip(blankBeforeQuestionClock.reset)
        win.flip()
        is_there_an_early = 0
        while blankBeforeQuestionClock.getTime() < 0.5:
            if serialPort:
                key_from_serial2 = str(port_s.readline())[2:-1]
                if len(key_from_serial2) > 0:
                    key_from_serial2 = key_from_serial2[-1]
            keyPress = event.getKeys(keyList=['r'])
            if ((keyPress and keyPress[0][0] == 'r') or key_from_serial2 == '1'):
                print("Early BP")
                if previousTrigger == 'H' or previousTrigger == 'HB' or previousTrigger == 'CB':
                    if trigger:
                        port.setData(value_parallel_huma_early_after_huma)
                    if previousTrigger == 'H':
                        early_button_presses_after_human += 1
                    previousTrigger = 'HB'
                elif previousTrigger=='C':
                    if trigger:
                        port.setData(value_parallel_huma_early_after_comp)
                    early_button_presses_after_computer += 1
                    previousTrigger = 'CB'
                if eyelink:
                    EyeLink.tracker.sendMessage(selfEdf, 'E')
                is_there_an_early += 1
                timeEarlyBTNPress = blankBeforeQuestionClock.getTime()
        if trigger :
            port.setData(0)

        # ------Prepare to start Routine "Question"-------

        continueRoutine = True
        Question.setAutoDraw(True)
        AnswerYes.setAutoDraw(True)
        AnswerNo.setAutoDraw(True)
        AnswerNoButWanted.setAutoDraw(True)
        AnswerYes.alignText = 'left'
        AnswerNo.alignText = 'right'
        AnswerNoButWanted.alignText== 'middle'
        Cross.setAutoDraw(False)
        win.callOnFlip(questionClock.reset)
        AnswerYes.setColor(color = 'black')
        AnswerNo.setColor(color = 'black')
        AnswerNoButWanted.setColor(color = 'black')
        selectedAnswer = ''

        # -------Start Routine "Question"-------
        win.flip()
        key_from_serial = []
        key_from_serial2 = ''
        while continueRoutine:
            if serialPort:
                key_from_serial2 = str(port_s.readline())[2:-1]
                if len(key_from_serial2) > 0:
                    key_from_serial2 = key_from_serial2[-1]
            keyPress = event.getKeys(keyList=['r', 'y', 'c', 'escape'])

            # Switching buttons
            # press r/1 to go left
            # press y/2 to go right
            # press c/3 to validate

            if (((keyPress and keyPress[0][0] == 'r') or key_from_serial2 == '1') and selectedAnswer=='') or \
               (((keyPress and keyPress[0][0] == 'y') or key_from_serial2 == '2') and selectedAnswer=='N') or \
               (((keyPress and keyPress[0][0] == 'r') or key_from_serial2 == '1') and selectedAnswer=='NBW'):
                AnswerYes.setColor('white')
                AnswerNo.setColor('black')
                AnswerNoButWanted.setColor('black')
                selectedAnswer='Y'
            elif (((keyPress and keyPress[0][0] == 'y') or key_from_serial2 == '2') and selectedAnswer=='') or \
                 (((keyPress and keyPress[0][0] == 'r') or key_from_serial2 == '1') and selectedAnswer=='Y') or \
                 (((keyPress and keyPress[0][0] == 'y') or key_from_serial2 == '2') and selectedAnswer=='NBW'):
                AnswerYes.setColor('black')
                AnswerNo.setColor('white')
                AnswerNoButWanted.setColor('black')
                selectedAnswer='N'
            elif ((keyPress and keyPress[0][0] == 'y') or key_from_serial2 == '2') and selectedAnswer=='Y' or \
                 (((keyPress and keyPress[0][0] == 'r') or key_from_serial2 == '1') and selectedAnswer=='N'):
                AnswerYes.setColor('black')
                AnswerNo.setColor('black')
                AnswerNoButWanted.setColor('white')
                selectedAnswer='NBW'
            elif ((keyPress and keyPress[0][0] == 'c') or key_from_serial2 == '8') and selectedAnswer != '':
                Question.setAutoDraw(False)
                AnswerYes.setAutoDraw(False)
                AnswerNo.setAutoDraw(False)
                AnswerNoButWanted.setAutoDraw(False)
                continueRoutine = False
                if selectedAnswer == 'Y':
                    if trigger :
                        port.setData(value_answer_yes)
                    # button_yes += 1
                    active_answer = 1
                    print('yes chosen' + '\n')
                    # TODO adding +1 depending on the trigger that created the question
                    dictKey = previousTrigger + '_yes'
                    dictCounterAnswers[dictKey]=dictCounterAnswers[dictKey]+1
                elif selectedAnswer == 'N':
                    if trigger :
                        port.setData(value_answer_no)
                    # button_no += 1
                    active_answer = 0
                    print('no chosen' + '\n')
                    dictKey = previousTrigger + '_no'
                    dictCounterAnswers[dictKey]=dictCounterAnswers[dictKey]+1
                elif selectedAnswer == 'NBW':
                    if trigger :
                        port.setData(value_answer_nbw)
                    # button_no_but_wanted += 1
                    active_answer = 0.5
                    print('nbw chosen' + '\n')
                    dictKey = previousTrigger + '_nbw'
                    dictCounterAnswers[dictKey]=dictCounterAnswers[dictKey]+1
                previousTrigger = ''

            win.flip()
            if trigger :
                port.setData(0)

            if event.getKeys(keyList=["escape"]):
                thisExp.saveAsWideText(filename+'.csv')
                thisExp.saveAsPickle(filename)
                if eyelink:
                    EyeLink.tracker.close(selfEdf, edfFileName)
                closeMEGB()
                win.close()
                core.quit()

    trials.addData('RT', RT)
    trials.addData('ActiveStatus', ActiveStatus)
    # for the BCI part
    if CHOICE_OF_EXPERIMENT == 'S2_without' or CHOICE_OF_EXPERIMENT == 'S2_with':
        if expInfo['part'] == 'part1':
            trials.addData('ActiveAnswer', 99)
            trials.addData('EarlyBP_trialbefore', is_there_an_early)
            if is_there_an_early != 0:
                trials.addData('RT_earlyBP_trialbefore', timeEarlyBTNPress)
            else:
                trials.addData('RT_earlyBP_trialbefore', 99)
        elif expInfo['part'] == 'part2':
            trials.addData('ActiveAnswer', active_answer)
            trials.addData('EarlyBP', is_there_an_early)
            if is_there_an_early != 0:
                trials.addData('RT_earlyBP', timeEarlyBTNPress)
            else:
                trials.addData('RT_earlyBP', 99)
    thisExp.nextEntry()

    # -------Ending Trials loop -------

print('saving')
thisExp.saveAsWideText(filename+'.csv')
thisExp.saveAsPickle(filename)
print('closing exp')
logging.flush()
print('closing log')
if CHOICE_OF_EXPERIMENT == 'S2_with':
    MEGB.stop()
    inputStream.close()
    MEGB.close()
    print('closing megb')
print('closing')

# make sure everything is closed down
thisExp.abort()  # or data files will save again on exit
if eyelink:
    EyeLink.tracker.close(selfEdf, edfFileName)
win.close()
core.quit()
exit()
