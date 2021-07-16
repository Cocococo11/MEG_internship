# Code written by Romain Quentin and Marine Vernet
# Modified by Fayed Rassoulou
# Integration of FieldTrip Buffer by Corentin Bel

# -*- coding: utf-8 -*-

# The files imported contain everything we need to run the code : libraries, functions, parameters, variables
# For the functions : make sure the files follow Github's package placement
from configs.basemy_agency import *
from configs.config_agency import *

# ***********************************************************************
# ********************** STARTING MEGBUFFER *****************************
# ***********************************************************************

# Starting the MEGBuffer, the thread associated and the pull of data from the MEG

if CHOICE_OF_EXPERIMENT == 'S2_with':
    # Loading the MEGBuffer node
    
    MEGB =  MEGBuffer()
    inputStream = InputStream()
    nbSteps_chosen = expInfo['nbSteps']
    clfname = expInfo['classifier']
    partTypeChosen = expInfo['part']
    timeBeforeStart = data.getDateStr()
    # Configuring with all the parameters from the information window
    MEGB.configure(nb_steps_chosen =nbSteps_chosen,clf_name =clfname,run_nbr = run_nbr,subjectId = participant ,partType = partTypeChosen, timeStart = timeBeforeStart,MEGsave = MEGsave)

    MEGB.outputs['signals'].configure( transfermode='plaindata')
    MEGB.outputs['triggers'].configure( transfermode='plaindata')
    MEGB.initialize()

    inputStream.connect(MEGB.outputs['signals'])
    # Connection it to the InputStream, and starting it
    MEGB.start()


# ------Prepare to start Routine "Instructions"-------

continueRoutine = True
White_screen.setAutoDraw(True)
Instructions.setAutoDraw(True)
Pixel.setAutoDraw(True)

# -------Start Routine "Instructions"-------
# This is where the participant gets told all the basic instructions 
# That is also when the participant can start the whole experiment

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
        closeMEGB(MEGB,inputStream)
        win.close()
        core.quit()

# Start MEG recordings
if trigger:
    port.setData(0)
    time.sleep(0.1)
    port.setData(252)



########################################################################################################################
# **************************************** BEGGINING OF THE EXPERIMENT *************************************************
########################################################################################################################


# Start the trials : this is the loop that will go on until the experiment finishes
for trial in trials:


    # ************************************************************
    # *************** 1st CONDITION TO TRY ***********************
    # ************************************************************
    #
    # ------ Stop the recordings and close everything for S2 part 1 -------
    # Conditions for stopping and closing everything : has to be the first thing checked for every trial (trial = image change)
    # We can ignore this part this for now, we want the part 1 to go on forever (and we stop it during a short break with escape)
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

        timeBeforeStart = data.getDateStr()
        bloc_nb = int(trials.thisN/nb_trials_before_short_break)

        # Plot of the current bloc 
        plt.subplot(2, 1, 1)
        pietoplot, pielabels = prepare_pie_plot(button_presses_bloc, random_changes_bloc, early_button_presses_after_computer_bloc, early_button_presses_after_human_bloc, trials.thisN,participant,run_nbr,timeBeforeStart,bloc_nb)
        plt.pie(pietoplot,labels=pielabels)
        plt.title('Current bloc: %d'%bloc_nb)
        if (nbSteps_chosen == None): # For testing in S2_withouts
            nbSteps_chosen = 777
        # Resetting the counts : 
        button_presses_bloc = 0
        random_changes_bloc = 0
        early_button_presses_after_computer_bloc = 0
        early_button_presses_after_human_bloc = 0



        # Plot of the next bloc
        plt.subplot(2, 1, 2)
        pietoplot, pielabels = prepare_pie_plot(button_presses, random_changes, early_button_presses_after_computer, early_button_presses_after_human, trials.thisN,participant,run_nbr,timeBeforeStart,bloc_nb)
        plt.pie(pietoplot,labels=pielabels)
        plt.title("Total on the current run")

        if (nbSteps_chosen == None): # For testing in S2_withouts
            nbSteps_chosen = 777




        plt.savefig('fig/' + str(participant) + '_' + str(nbSteps_chosen)+'steps_run'+str(run_nbr)+'_'+expInfo['date']+'_megsave'+str(MEGsave))
        if DEBUG == False:
            mngr = plt.get_current_fig_manager()
            mngr.window.setGeometry(2000, 100, 1000, 700)
        plt.show()

        time.sleep(5)
        plt.close()
        thisExp.saveAsWideText(filename+'.csv')
        thisExp.saveAsPickle(filename)
        if eyelink:
            EyeLink.tracker.close(selfEdf, edfFileName)
        closeMEGB(MEGB,inputStream)
        win.close()
        core.quit()

    # ************************************************************
    # *************** 2nd CONDITION TO TRY ***********************
    # ************************************************************
    #
    # ------Condition for Long Break-------
    # Happens after a certain number of trials : check the variable nb_trials_before_long_break
    # Print the current stats of the run, and send a trigger to start another recording if it's needed at the MEG
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
                closeMEGB(MEGB,inputStream)
                win.close()
                core.quit()

        # Start MEG recordings
        if trigger:
            port.setData(252)

    event.clearEvents(eventType='keyboard')


    # ************************************************************
    # *************** 3rd CONDITION TO TRY ***********************
    # ************************************************************
    #
    # ------Condition for Short Break-------
    # This is the short break that happens both in part 1 or part 2
    # For part 1 : it allows us to look at the figure generated and potentially adjust the classifier parameters
    # For part 2 : it allows us to change the MEGsave file number if needed (for the part 2, we loop until we manually
    # leave the experiment, and since the meg saves are only 7 minutes long, for better file's saving names, we want to make
    # sure we use the right meg save number if the current run is longer than 7 minutes)
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
            timeBeforeStart = data.getDateStr()
            bloc_nb = int(trials.thisN/nb_trials_before_short_break)
            if expInfo['part'] == 'part2': # max(dictCounterAnswers.values())>0 :
                # Show the windows to potentially change the MEGsave number :
                print('here')
                isLongBreak = ((trials.thisN+1 % nb_trials_before_long_break) == 0)
                if(isLongBreak):
                    plotDict2(dictCounterAnswers ,dictCounterAnswersTotal,participant,run_nbr,timeBeforeStart,bloc_nb,MEGsave )
                    dictCounterAnswers = dict.fromkeys(dictCounterAnswers, 0) # Resetting the temporary dict to 0
                else : 
                    print('there')
                    plotDict2(dictCounterAnswers,dictCounterAnswersTotal,participant,run_nbr,timeBeforeStart,bloc_nb, MEGsave)
                    dictCounterAnswers = dict.fromkeys(dictCounterAnswers, 0)

                # print(yaml.dump(dictCounterAnswers, sort_keys=False, default_flow_style=False))
            elif expInfo['part'] == 'part1':
                print("and everywhere")

                if DEBUG == False:
                    mngr = plt.get_current_fig_manager()
                    mngr.window.setGeometry(2000, 100, 1000, 700)       

                # fig = plt.figure()  
                # timer = fig.canvas.new_timer(interval = 1000)
                # timer.add_callback(close_event)
                # timer.start()  
                # Plot of the current bloc 
                plt.subplot(2, 1, 1)
                pietoplot, pielabels = prepare_pie_plot(button_presses_bloc, random_changes_bloc, early_button_presses_after_computer_bloc, early_button_presses_after_human_bloc, trials.thisN,participant,run_nbr,timeBeforeStart,bloc_nb)
                plt.pie(pietoplot,labels=pielabels)
                plt.title('Current bloc: %d'%bloc_nb)
                if (nbSteps_chosen == None): # For testing in S2_withouts
                    nbSteps_chosen = 777
                # Resetting the counts : 
                button_presses_bloc = 0
                random_changes_bloc = 0
                early_button_presses_after_computer_bloc = 0
                early_button_presses_after_human_bloc = 0



                # Plot of the next bloc
                plt.subplot(2, 1, 2)
                pietoplot, pielabels = prepare_pie_plot(button_presses, random_changes, early_button_presses_after_computer, early_button_presses_after_human, trials.thisN,participant,run_nbr,timeBeforeStart,bloc_nb)
                plt.pie(pietoplot,labels=pielabels)
                plt.title("Total on the current run")
                
                if not os.path.exists('./fig/%s'%participant):
                    os.makedirs('./fig/%s'%participant)
                # print(bloc_nb)
                plt.savefig('./fig/%s/fig_%s_part1_run%s_bloc%s_%s'%(participant,participant,run_nbr,bloc_nb,timeBeforeStart))
                # plt.close()
                plt.show()
                dictCounterAnswers = dict.fromkeys(dictCounterAnswers, 0) # Resetting the temporary dict to 0


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
                if trigger:
                    port.setData(252)
                Instructions.setAutoDraw(False)
                continueRoutine = False
            if event.getKeys(keyList=["escape"]):
                thisExp.saveAsWideText(filename+'.csv')
                thisExp.saveAsPickle(filename)
                if eyelink:
                    EyeLink.tracker.close(selfEdf, edfFileName)
                closeMEGB(MEGB,inputStream)
                win.close()
                core.quit()
            if shortBreackClock.getTime() > 30 and CHOICE_OF_EXPERIMENT == 'S1_random':  # noqa
                Instructions.setAutoDraw(False)
                continueRoutine = False
        textMEGsave = "Current run : "+str(MEGsave)
        dlgMEGsave.addText(textMEGsave)
        expMEGsave['MEGsave'] = dlgMEGsave.show()
        MEGsave = expMEGsave['MEGsave']
        if(CHOICE_OF_EXPERIMENT=='S2_with' and partTypeChosen=='part1'):
            
            expOk['OK'] = dlgOk.show()
            if dlgOk.OK :# and (expOk['OK']==True ): 
                try :
                    expChange['nbSteps'],expChange['clf'] =dlgChange.show()
                except:
                    print('Change cancelled')
                if dlgChange.OK and (expChange['clf'] != clfname or expChange['nbSteps']!=nbSteps_chosen):
                    print('Change successful: MEGBuffer will restart with the new values ')
                    
                    closeMEGB(MEGB,inputStream)
                    plt.savefig('fig/' + str(participant) + '_' + str(nbSteps_chosen)+'steps_run'+str(run_nbr)+'_'+expInfo['date']) 
                    print("We saved the fig generated with the previous values !    ")
                    # inputStream.close() # Do we have to close it ?
                    # Restart everything : 
                    MEGB =  MEGBuffer()
                    inputStream = InputStream()
                    nbSteps_chosen = expInfo['nbSteps']
                    clfname = expInfo['classifier']
                    timeBeforeStart = data.getDateStr()
                    MEGB.configure(nb_steps_chosen =expChange['nbSteps'],clf_name =expChange['clf'],run_nbr = run_nbr,subjectId = participant ,partType = partTypeChosen, timeStart = timeBeforeStart,MEGsave = MEGsave)
                    # MEGB.configure(nb_steps_chosen =nbSteps_chosen,clf_name =clfname,run_nbr = run_nbr,subjectId = participant ,partType = partTypeChosen, timeStart = timeBeforeStart)

                    MEGB.outputs['signals'].configure( transfermode='plaindata')
                    MEGB.outputs['triggers'].configure( transfermode='plaindata')
                    MEGB.initialize()

                    inputStream.connect(MEGB.outputs['signals'])

                    MEGB.start()
                    # Resend a trigger to show we started again
                    if trigger:
                        port.setData(252)

                else : 
                    print("Same values as previous run kept")
                    


                
            else : 
                print('User cancelled : acting as if there was no change in clf')

        # elif(CHOICE_OF_EXPERIMENT=='S2_with' and partTypeChosen=='part2'):
        #     expMEGsave['MEGsave'] = dlgMEGsave.show()
        #     if dlgMEGsave.OK :# and (expOk['OK']==True ): 
        #         MEGsaveNumber = expMEGsave['MEGsave']
        time.sleep(0.01)
        if trigger:
            port.setData(0)

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
            closeMEGB(MEGB,inputStream)
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
                dataMEG = inputStream.recv() # Pulling the data from the
                # print("Time after receiving the data : ",time.time())
                # 
                # print(data)
                # print(time.time())
                if( dataMEG[1][0] == 1):
                    if trigger:
                        port.setData(value_parallel_comp)
                    if eyelink:
                        EyeLink.tracker.sendMessage(selfEdf, 'C')
                    RT = imageClock.getTime()
                    ActiveStatus = 0
                    random_changes += 1
                    random_changes_bloc+=1
                    detectPrep = True
                    cond_for_loop=False
                    print('computer change')
                    # print("Time after confirming the data for a change : ",time.time())
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
                button_presses_bloc+=1
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
                    early_button_presses_after_human_bloc+=1
                    previousTrigger='HB'
                elif previousTrigger == 'C':
                    if trigger:
                        port.setData(value_parallel_huma_early_after_comp)
                        time.sleep(0.01)
                    print("Early BP after computer")
                    is_there_an_early += 1
                    early_button_presses_after_computer += 1
                    early_button_presses_after_computer_bloc+=1
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
            closeMEGB(MEGB,inputStream)
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
            random_changes_bloc+=1

    win.callOnFlip(printTiming, trials, imageClock, 'image')
    win.flip()
    # print("Time when imagine changed : ",time.time())

    if trigger :
        port.setData(0)


    # ------Condition for Question, BCI part (part 2) -------
    if (CHOICE_OF_EXPERIMENT == 'S2_without' or CHOICE_OF_EXPERIMENT == 'S2_with') and (expInfo['part'] == 'part2' or expInfo['part']== 'part2_blank') :

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
                        early_button_presses_after_human_bloc +=1
                    previousTrigger = 'HB'
                elif previousTrigger=='C':
                    if trigger:
                        port.setData(value_parallel_huma_early_after_comp)
                        time.sleep(0.01)
                    early_button_presses_after_computer += 1
                    early_button_presses_after_computer_bloc+=1
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
                    print('Human choisi' + '\n')
                    # TODO adding +1 depending on the trigger that created the question
                    dictKey = previousTrigger + '_yes'
                    dictCounterAnswers[dictKey]=dictCounterAnswers[dictKey]+1
                    dictCounterAnswersTotal[dictKey]=dictCounterAnswersTotal[dictKey]+1
                elif selectedAnswer == 'N':
                    if trigger :
                        port.setData(value_answer_no)
                    # button_no += 1
                    active_answer = 0
                    print('Computer choisi' + '\n')
                    dictKey = previousTrigger + '_no'
                    dictCounterAnswers[dictKey]=dictCounterAnswers[dictKey]+1
                    dictCounterAnswersTotal[dictKey]=dictCounterAnswersTotal[dictKey]+1
                elif selectedAnswer == 'NBW':
                    if trigger :
                        port.setData(value_answer_nbw)
                    # button_no_but_wanted += 1
                    active_answer = 0.5
                    print('Ordi avant vous choisi' + '\n')
                    dictKey = previousTrigger + '_nbw'
                    dictCounterAnswers[dictKey]=dictCounterAnswers[dictKey]+1
                    dictCounterAnswersTotal[dictKey]=dictCounterAnswersTotal[dictKey]+1
                previousTrigger = ''

            win.flip()
            if trigger :
                port.setData(0)

            if event.getKeys(keyList=["escape"]):
                thisExp.saveAsWideText(filename+'.csv')
                thisExp.saveAsPickle(filename)
                if eyelink:
                    EyeLink.tracker.close(selfEdf, edfFileName)
                closeMEGB(MEGB,inputStream)
                win.close()
                core.quit()

    trials.addData('RT', RT)
    trials.addData('ActiveStatus', ActiveStatus)
    trials.addData('blocNumber',bloc_nb)
    trials.addData('MEGsave',MEGsave)
    if CHOICE_OF_EXPERIMENT == 'S2_with':
        trials.addData('nbSteps',nbSteps_chosen)
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
