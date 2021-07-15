#######################################################################################################################
######################### File regrouping all the functions used in the agency_task_bci script#########################
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
from configs.config_agency import * 

# Imports for the pyacq node
from pyacq.core.stream import InputStream
from MEGBuffer import MEGBuffer
from joblib import load




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


# Simple closing plot function
def close_event():
    plt.close()


def plotDict2(dictCounterAnswers,dictCounterAnswersTotal,participant,run_nbr,timeBeforeStart,bloc_nb,fileMEG):

    plt.subplot(2, 1, 1)
    A = [dictCounterAnswers['H_yes'], dictCounterAnswers['C_yes'], dictCounterAnswers['HB_yes'], dictCounterAnswers['CB_yes']]
    B = [dictCounterAnswers['H_no'],  dictCounterAnswers['C_no'],  dictCounterAnswers['HB_no'],  dictCounterAnswers['CB_no']]
    C = [dictCounterAnswers['H_nbw'], dictCounterAnswers['C_nbw'], dictCounterAnswers['HB_nbw'], dictCounterAnswers['CB_nbw']]
    X = ['Hum', 'Comp', 'Hum+But', 'Comp+But']

    plt.bar(X, A, color = 'brown', label='Comp')
    plt.bar(X, B, color = 'olive', bottom = A, label='Human')
    plt.bar(X, C, color = 'darkorange', bottom = np.sum([A, B], axis=0), label='Comp + But')
    plt.legend()
    plt.title("Results from the current bloc")

    plt.subplot(2, 1, 2)

    A = [dictCounterAnswersTotal['H_yes'], dictCounterAnswersTotal['C_yes'], dictCounterAnswersTotal['HB_yes'], dictCounterAnswersTotal['CB_yes']]
    B = [dictCounterAnswersTotal['H_no'],  dictCounterAnswersTotal['C_no'],  dictCounterAnswersTotal['HB_no'],  dictCounterAnswersTotal['CB_no']]
    C = [dictCounterAnswersTotal['H_nbw'], dictCounterAnswersTotal['C_nbw'], dictCounterAnswersTotal['HB_nbw'], dictCounterAnswersTotal['CB_nbw']]
    X = ['Hum', 'Comp', 'Hum+But', 'Comp+But']

    plt.bar(X, A, color = 'brown', label='Comp')
    plt.bar(X, B, color = 'olive', bottom = A, label='Human')
    plt.bar(X, C, color = 'darkorange', bottom = np.sum([A, B], axis=0), label='Comp + but')
    plt.legend()
    plt.title("General results")

    if DEBUG == False:
        mngr = plt.get_current_fig_manager()
        mngr.window.setGeometry(2000, 100, 1000, 700)
    
    if not os.path.exists('./fig/%s'%participant):
        os.makedirs('./fig/%s'%participant)
    plt.savefig('./fig/%s/fig_%s_part2_run%s_bloc%s_%s_megSave%s'%(participant,participant,run_nbr,bloc_nb,timeBeforeStart,fileMEG))
    plt.show()

def closeMEGB(MEGB,inputStream):
    if (CHOICE_OF_EXPERIMENT == 'S2_with'):
        MEGB.stop()
        inputStream.close()
        MEGB.close()

def prepare_pie_plot(button_presses, random_changes, early_button_presses_after_computer, early_button_presses_after_human, nb_trials,participant,run_nbr,timeBeforeStart,bloc_nb):
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

# Old version of the plot 
# def plotDict(dict):
#     listKeys = dict.keys()
#     values = dict.values()
#     plt.bar(listKeys,values,color=['lightcoral','indianred','brown','olive','olivedrab','yellowgreen','magenta','orchid','hotpink','darkorange','goldenrod','moccasin'])
#     plt.title("Early results of button presses")
#     plt.show()
