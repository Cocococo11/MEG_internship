# Code written by Romain Quentin and Marine Vernet

# -*- coding: utf-8 -*-
from __future__ import absolute_import, division
from psychopy import gui, visual, core, data, event, logging, parallel
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)
import os
import os.path as op

#TODO

#imports for the pyacq node
from pyacq.core.stream import InputStream
from MEGBuffer import MEGBuffer
from joblib import load

import numpy as np
from random import choice # for the BCI part

import time

# New for MEG: serial Port
from serial import Serial


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


# PARAMETERS TO CHECK AT THE BEGINNING OF THE SESSION

# computer (MEG/EEG/MEG_NIH/Marine/Marine_perso/Salim/Fayed)
computer = 'Corentin'

DEBUG = True
trigger = False
eyelink = False
serialPort = False

# number of trials TO BE CORRECTED FOR THE REAL EXPERIMENT !!!!!!!!!!!!!!!!!!!
nb_trials_before_short_break = 5 # 50
nb_trials_before_long_break = 20 # 200
max1_trials = 60 # 1200
max2_trials = 80 # 1400
threshold600 = 0 # did we reach 600 trials in each category?

# for the BCI part
nb_trials_before_question = 1
nb_of_blocks_before_question = 1
nb_of_trials_within_little_block = 0 # initialize counter
nb_of_big_blocks_performed = 1 # initialize counter


# debug mode
if DEBUG:
    fullscr = False
    logging.console.setLevel(logging.DEBUG)
else:
    fullscr = True
    # logging.console.setLevel(logging.WARNING)

# Path to save the results
if computer == 'EEG':
    home_folder = '/Users/chercheur/Documents/PythonScripts/Agency_Salim/scripts'  # noqa
elif computer == 'MEG':
    home_folder = 'C:\\Python_users\\Agency\\scripts'
elif computer == 'MEG_NIH':
    home_folder = 'C:\\Users\\meglab\\EExperiments\\Marine\\agentivity_task'
elif computer == 'Marine':
    home_folder = '/Users/vernetmc/Documents/lab_NIH_Marine/Python/psychopy/agentivity'  # noqa
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

#TODO

#Loading the MEGBuffer node 
MEGB =  MEGBuffer()
inputStream = InputStream()
MEGB.configure()

MEGB.outputs['signals'].configure( transfermode='plaindata')
MEGB.outputs['triggers'].configure( transfermode='plaindata')
MEGB.initialize()

inputStream.connect(MEGB.outputs['signals'])

MEGB.start()


#and the classifier
classifier = load('classifiers/0989_meg_CLF_pack [-0.3,-0.1]_filter.joblib')



# Store info about the experiment session
# expName = 'AgentivityRandom'
expName = 'AgentivityBCI' # for the BCI part
expInfo = {'participant': '', 'session': ''}
dlg = gui.DlgFromDict(dictionary=expInfo, title=expName)
if dlg.OK is False:
    core.quit()  # user pressed cancel
expInfo['expName'] = expName
expInfo['date'] = data.getDateStr()  # will create str of current date/time
expInfo['frameRate'] = 60  # store frame rate of monitor
frameDur = 1.0 / 60.0

# Data file name
edfFileName = expInfo['participant']+expInfo['session']
filename = results_folder + '/%s_%s_%s_%s' % (expName, expInfo['participant'],
                                              expInfo['session'],
                                              expInfo['date'])

# params
if computer == 'EEG':
    window_size = (1024, 768)
    value_parallel_huma = 1
    value_parallel_comp = 2
    addressPortParallel = '0x0378'
elif computer == 'MEG':  # CHECK THESE PARAMETERS
    window_size = (1920, 1080)
    value_parallel_huma = 20
    value_parallel_comp = 40
    addressPortParallel = '0x3FE8'
elif computer == 'MEG_NIH':
    window_size = (1024, 768)
    value_parallel_huma = 20
    value_parallel_comp = 40
    addressPortParallel = '0x0378'
elif computer == 'Marine':
    window_size = (2880, 1800)
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
    # port.setData(252)
if eyelink:
    import EyeLink
    selfEdf = EyeLink.tracker(window_size[0], window_size[1], edfFileName)

# list all images
images = list()
files_list = os.listdir(op.join(home_folder, 'AgencyImage_session1'))
for img in files_list:
    if '.jpg' in img:
        if img.startswith('A'):
            images.append(img)
# images = images[:number_of_images]  # take only the number_of_images defined

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
if computer == 'MEG_NIH':
    Pixel = visual.Line(
        win=win, name='topleftpixel', units='pix',
        start=(-window_size[0]/2, window_size[1]/2),
        end=(-window_size[0]/2+1, window_size[1]/2+1),
        lineColor=[1, 1, 1])
else:
    Pixel = visual.Rect(
        win=win, name='topleftpixel', units='pix',
        pos=(-window_size[1], window_size[1]/2),
        size=(window_size[0]*2/5, 200),
        fillColor=[-1, -1, -1],
        lineColor=[-1, -1, -1])

# Initialize components for Routine "image"
fname = op.join(home_folder, 'AgencyImage_session1', images[1])
Image = visual.ImageStim(
    win, image=fname, pos=(0, 0), size=image_size)
preload_images = [
    visual.ImageStim(win, op.join(home_folder, 'AgencyImage_session1', img), size=image_size)
    for img in images]

# for the BCI part
Question = visual.TextStim(win=win, name='Question', text="Avez-vous changé l'image ?",
                           font='Arial', pos=(0, 0.3), height=0.1, wrapWidth=None,
                           ori=0, color='black', colorSpace='rgb', opacity=1)
AnswerYes = visual.TextStim(win=win, name='AnswerYes', text='VOUS',
                            font='Arial', pos=(0, -0.1), height=0.1, wrapWidth=None,
                            ori=0, color='black', colorSpace='rgb', opacity=1)
AnswerNo = visual.TextStim(win=win, name='AnswerNo', text='ORDI',
                           font='Arial', pos=(0, -0.1), height=0.1, wrapWidth=None,
                           ori=0, color='black', colorSpace='rgb', opacity=1)

# Create some handy timers
imageClock = core.Clock()
blankClock = core.Clock()
longBreackClock = core.Clock()
shortBreackClock = core.Clock()
questionClock = core.Clock() # for the BCI part
globalClock = core.Clock()  # to track the time since experiment started
globalClock.reset()  # clock

# Create the parameters of the gamma function
k_shape = 3
theta_scale = 1

# Count number of button press and number of random changes
button_presses = 0
random_changes = 0

# Count number of yes and no response (for the BCI part)
button_yes = 0
button_no = 0

this_is_a_long_break = 0




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
            # win.flip()
    # else:
    if event.getKeys(keyList=['y']):
        Instructions.setAutoDraw(False)
        continueRoutine = False
        # win.flip()
    if event.getKeys(keyList=["escape"]):
        thisExp.saveAsWideText(filename+'.csv')
        thisExp.saveAsPickle(filename)
        if eyelink:
            EyeLink.tracker.close(selfEdf, edfFileName)
        win.close()
        core.quit()

# Start MEG recordings
if trigger:
    port.setData(0)
    time.sleep(0.1)
    port.setData(252)

# Start the trials
for trial in trials:

    # ------Condition for Long Break-------
    if ((trials.thisN % nb_trials_before_long_break) == 0 and trials.thisN != 0 and trials.thisN < max1_trials) or \
       (button_presses >= max1_trials/2 and random_changes >= max1_trials/2 and threshold600 == 0) or \
       (button_presses >= max2_trials/2 and random_changes >= max2_trials/2):

        this_is_a_long_break = 1

        nb_of_big_blocks_performed += 1 # for the BCI part

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
        print('Long break') # for the random part
        print('Partipant : ' + str(button_presses) + '\nOrdinateur : ' + str(random_changes)) # for the random part
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
        # # for the random part
        # difference = button_presses - random_changes
        # if difference > 6:
        #     break_text = "Petite pause ! \n\n Vous répondez trop souvent par rapport à l'ordinateur. \nAppuyez moins souvent. \n\n Pour continuer, appuyez sur le bouton de droite."
        # elif difference < -6:
        #     break_text = "Petite pause ! \n\n Vous ne répondez pas assez souvent par rapport à l'ordinateur. \nAppuyez plus souvent. \n\n Pour continuer, appuyez sur le bouton de droite."
        # else:
        #     break_text = "Petite pause ! \n\n Vous répondez aussi souvent que l'ordinateur, bravo ! \n\n Pour continuer, appuyez sur le bouton de droite."
        # # break_text = 'Petite pause !' + '\n\nVous : ' + str(button_presses) + '\n\n Ordinateur : ' + str(random_changes) + '\n\n Appuyez sur le bouton de droite pour continuer.'  # for the random part
        # for the BCI part
        break_text = 'Pause !' + '\n\n Appuyez sur le bouton de droite pour continuer.'  # for the BCI part
        Instructions.setText(break_text)
        Instructions.setAutoDraw(True)
        Pixel.setAutoDraw(True)
        Cross.setAutoDraw(False)
        win.callOnFlip(shortBreackClock.reset)

        # -------Start Routine "Short Break"-------
        win.flip()
        if this_is_a_long_break == 0:
            print('Partipant : ' + str(button_presses) + '\nOrdinateur : ' + str(random_changes)) # for the random part
            print('Participant-Ordinateur : ' + str(button_presses-random_changes) + '\n') # for the random part
        else:
            this_is_a_long_break = 0
        # Reset nb of trials (for the BCI part)
        nb_of_trials_within_little_block = 0
        key_from_serial = []
        key_from_serial2 = ''
        while continueRoutine:
            if serialPort:
                key_from_serial2 = str(port_s.readline())[2:-1]
                if len(key_from_serial2) > 0:
                    key_from_serial2 = key_from_serial2[-1]
                if key_from_serial2 == '2':
                    Instructions.setAutoDraw(False)
                    continueRoutine = False
                    # win.flip()
            # else:
            if event.getKeys(keyList=['y']):
                Instructions.setAutoDraw(False)
                continueRoutine = False
                # win.flip()
            if event.getKeys(keyList=["escape"]):
                thisExp.saveAsWideText(filename+'.csv')
                thisExp.saveAsPickle(filename)
                if eyelink:
                    EyeLink.tracker.close(selfEdf, edfFileName)
                win.close()
                core.quit()
            if shortBreackClock.getTime() > 30:  # noqa
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
            win.close()
            core.quit()

    # ------Prepare to start Routine "Image"-------
    preload_images[trial['image_nb']].setAutoDraw(True)
    Cross.setAutoDraw(True)
    Pixel.setAutoDraw(False)
    event.clearEvents(eventType='keyboard')

    # Increase nb of trials (for the BCI part)
    nb_of_trials_within_little_block += 1

    # -------Start Routine "Image"-------
    win.callOnFlip(imageClock.reset)
    win.callOnFlip(printTiming, trials, blankClock, 'blank')
    win.flip()
    # while continueRoutine:
    keyPress = []
    key_from_serial = []
    key_from_serial2 = ''
    frameRemainsRT = np.maximum(0.5, np.random.gamma(k_shape, scale=theta_scale, size=1))  # noqa
    prediction =[2,2]   
    detectPrep = False
    #TODO
    while not keyPress and not detectPrep and key_from_serial2 != '1':  # noqa
        keyPress = event.getKeys(keyList=['r', 'escape'],
                                 timeStamped=imageClock)
        
        #MEGBuffer Part
        # Polling and receiving the data sent by the MEGBuffer node
        dataIsAvailable = inputStream.poll()
        data = inputStream.recv()
          
        i=0
        nbPaquetsToTest = 10000 #  represents the number of packages of 24 we want to test
        nbPred = 0
        while(dataIsAvailable and i<nbPaquetsToTest):        
            data = inputStream.recv() # Pulling the data from the stream
            if( data[1][0] == 1):
                print('Detection ')
                nbPred+=1
                            
            else:
                #print('NO DETEK')
                a = 2
            try :
                dataIsAvailable = inputStream.poll(1000)
            except : 
                print("Error with polling the input stream")
                break
            i=i+1
            
        print("Nb detek : ",nbPred)
        
        

        if serialPort:
            key_from_serial2 = str(port_s.readline())[2:-1]
            if len(key_from_serial2) > 0:
                key_from_serial2 = key_from_serial2[-1]
                if key_from_serial2 == '1':
                    if trigger:
                        port.setData(value_parallel_huma)
                    if eyelink:
                        EyeLink.tracker.sendMessage(selfEdf, 'H')
                    preload_images[trial['image_nb']].setAutoDraw(False)
                    Pixel.setAutoDraw(True)
                    RT = imageClock.getTime()
                    ActiveStatus = 1
                    button_presses += 1
        # else:
        if keyPress and keyPress[0][0] == 'r':
            if trigger:
                port.setData(value_parallel_huma)
            if eyelink:
                EyeLink.tracker.sendMessage(selfEdf, 'H')
            preload_images[trial['image_nb']].setAutoDraw(False)
            Pixel.setAutoDraw(True)
            RT = keyPress[0][1]
            ActiveStatus = 1
            button_presses += 1
        if (keyPress and keyPress[0][0] == 'escape'):
            thisExp.saveAsWideText(filename+'.csv')
            thisExp.saveAsPickle(filename)
            if eyelink:
                EyeLink.tracker.close(selfEdf, edfFileName)
            win.close()
            core.quit()
    if not keyPress and key_from_serial2 != '1':
        if trigger:
            port.setData(value_parallel_comp)
        if eyelink:
            EyeLink.tracker.sendMessage(selfEdf, 'C')
        preload_images[trial['image_nb']].setAutoDraw(False)
        Pixel.setAutoDraw(True)
        RT = frameRemainsRT[0]
        ActiveStatus = 0
        random_changes += 1
    win.callOnFlip(printTiming, trials, imageClock, 'image')
    win.flip()

    # for the BCI part

    # ------Condition for Question -------
    if ((trials.thisN % nb_trials_before_question) == 0 and
        (nb_of_trials_within_little_block != 0) and
        (nb_of_big_blocks_performed > nb_of_blocks_before_question)):

        # ------Prepare to start Routine "Question"-------
        continueRoutine = True
        Question.setAutoDraw(True)
        AnswerYes.setAutoDraw(True)
        AnswerNo.setAutoDraw(True)
        AnswerYes.alignText=choice(['right', 'left'])
        if AnswerYes.alignText == 'left':
            AnswerNo.alignText = 'right'
        else:
            AnswerNo.alignText = 'left'
        Cross.setAutoDraw(False)
        win.callOnFlip(questionClock.reset)

        # -------Start Routine "Question"-------
        win.flip()
        key_from_serial = []
        key_from_serial2 = ''
        while continueRoutine:
            if serialPort:
                key_from_serial2 = str(port_s.readline())[2:-1]
                if len(key_from_serial2) > 0:
                    key_from_serial2 = key_from_serial2[-1]
                if ((key_from_serial2 == '0' and AnswerYes.alignText == 'left') or
                    (key_from_serial2 == '2' and AnswerYes.alignText == 'right')):
                    Instructions.setAutoDraw(False)
                    Question.setAutoDraw(False)
                    AnswerYes.setAutoDraw(False)
                    AnswerNo.setAutoDraw(False)
                    continueRoutine = False
                    button_yes += 1
                    active_answer = 1
                elif ((key_from_serial2 == '0' and AnswerYes.alignText == 'right') or
                    (key_from_serial2 == '2' and AnswerYes.alignText == 'left')):
                    Instructions.setAutoDraw(False)
                    Question.setAutoDraw(False)
                    AnswerYes.setAutoDraw(False)
                    AnswerNo.setAutoDraw(False)
                    continueRoutine = False
                    button_no += 1
                    active_answer = 0
                # win.flip()
            # else:
            if ((event.getKeys(keyList=['c']) and AnswerYes.alignText == 'left') or
                (event.getKeys(keyList=['y']) and AnswerYes.alignText == 'right')):
                Question.setAutoDraw(False)
                AnswerYes.setAutoDraw(False)
                AnswerNo.setAutoDraw(False)
                continueRoutine = False
                button_yes += 1
                active_answer = 1
            elif ((event.getKeys(keyList=['c']) and AnswerYes.alignText == 'right') or
                (event.getKeys(keyList=['y']) and AnswerYes.alignText == 'left')):
                Question.setAutoDraw(False)
                AnswerYes.setAutoDraw(False)
                AnswerNo.setAutoDraw(False)
                continueRoutine = False
                button_no += 1
                active_answer = 0
                # win.flip()
            if event.getKeys(keyList=["escape"]):
                thisExp.saveAsWideText(filename+'.csv')
                thisExp.saveAsPickle(filename)
                if eyelink:
                    EyeLink.tracker.close(selfEdf, edfFileName)
                win.close()
                core.quit()

    trials.addData('RT', RT)
    trials.addData('ActiveStatus', ActiveStatus)
    # for the BCI part
    if (nb_of_big_blocks_performed > nb_of_blocks_before_question):
        trials.addData('ActiveAnswer', active_answer)
        trials.addData('ActiveAnswerPosition', AnswerYes.alignText)
    else:
        trials.addData('ActiveAnswer', 99)
        trials.addData('ActiveAnswerPosition', 'None')
    thisExp.nextEntry()

    # -------Ending Trials loop -------

thisExp.saveAsWideText(filename+'.csv')
thisExp.saveAsPickle(filename)
logging.flush()
# make sure everything is closed down
thisExp.abort()  # or data files will save again on exit
if eyelink:
    EyeLink.tracker.close(selfEdf, edfFileName)
win.close()
core.quit()
exit()
