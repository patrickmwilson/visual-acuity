#Crowded Periphery
#Created by Patrick Wilson on 11/29/2019 
#Github.com/patrickmwilson
#Created for the Elegant Mind Collaboration at UCLA under Professor Katsushi Arisaka
#Copyright © 2019 Elegant Mind Collaboration. All rights reserved.

from __future__ import absolute_import, division

import psychopy
psychopy.useVersion('latest')

from psychopy import locale_setup, prefs, sound, gui, visual, core, data, event, logging, clock, monitors
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)
from psychopy.hardware import keyboard

import numpy as np  
from numpy import (sin, cos, tan, log, log10, pi, average,
                   sqrt, std, deg2rad, rad2deg, linspace, asarray)
from numpy.random import random, randint, normal, shuffle

import os, sys, time, random, math, csv

#CSVWRITER FUNCTION
def csvOutput(output):
    with open(filename,'a', newline ='') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(output)
    csvFile.close()

#CLOSE WINDOW, FLUSH LOG, STOP SCRIPT EXECUTION
def endExp():
    win.flip()
    logging.flush()
    win.close()
    core.quit()

#Y/N INPUT DIALOGUE FOR DATA RECORDING
datadlg = gui.Dlg(title='Record Data?', pos=None, size=None, style=None, labelButtonOK=' Yes ', labelButtonCancel=' No ', screen=-1)
ok_data = datadlg.show()
recordData = datadlg.OK

if recordData:
    #OUTPUT FILE PATH
    PATH = 'C:\\Users\\chand\\OneDrive\\Desktop\\VA Scripts\\Crowded Periphery'
    OUTPATH = '{0:s}\\Data\\'.format(PATH)
    
    #CD TO SCRIPT DIRECTORY
    _thisDir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(_thisDir)
    #STORE INFO ABOUT EXPERIMENT SESSION
    expName = 'Crowded Periphery'
    date = data.getDateStr(format='%m-%d') 
    expInfo = {'Participant': ''}
    
    #DIALOGUE WINDOW FOR PARTICIPANT NAME
    dlg = gui.DlgFromDict(dictionary=expInfo, sortKeys=False, title=expName)
    if dlg.OK == False:
        core.quit()
    
    #CREATE FILE NAME, PRINT HEADER IF FILE DOESN'T EXIST
    filename = OUTPATH + u'%s_%s_%s' % (expInfo['Participant'], date, expName) + '.csv'
    if not os.path.isfile(filename):
        csvOutput(["Direction","Letter Height (degrees)","Eccentricity (degrees)"]) 

#WINDOW CREATION
mon = monitors.Monitor('TV')
mon.setWidth(200)
win = visual.Window(
    size=(3840, 2160), fullscr=False, screen=-1, 
    winType='pyglet', allowGUI=True, allowStencil=False,
    monitor= mon, color='white', colorSpace='rgb',
    blendMode='avg', useFBO=True, 
    units='cm')

#CREATE DEFAULT KEYBOARD
defaultKeyboard = keyboard.Keyboard()
keyPress = keyboard.Keyboard()

#EXPERIMENTAL VARIABLES
letters = list("EPB")
sizes = [0.25, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4]
directions = [0, 1, 2, 3] #0 = R, 1 = D, 2 = L, 3 = U

#SPACING ADJUSTMENTS FOR TEXT DISPLAY
dirXMult = [1.62, 0, -1.68, 0]
dirYMult = [0, -1.562, 0, 1.748]
yOffset = [0.2, 0, 0.2, 0]
maxAngles = [61, 42, 61, 42]

#GENERATE TEXT STIM OBJECT
def genDisplay(text, xPos, yPos, height, colour):
    displayText = visual.TextStim(win=win,
    text= text,
    font='Arial',
    pos=(xPos, yPos), height=height, wrapWidth=500, ori=0, 
    color=colour, colorSpace='rgb', opacity=1, 
    languageStyle='LTR',
    depth=0.0);
    return displayText

#STAIRCASE ALGORITHM TO DETERMINE MAXIMUM LEGIBLE ANGLE
def stairCase(thisResponse, numReversals, angle, stairCaseCompleted, lastResponse, responses, maxAngle):
    responses += 1
    #IF TWO SEQUENTIAL IN/CORRECT ANSWERS, RESET NUMREVERSALS
    if numReversals > 0 and lastResponse == thisResponse:
        numReversals = 0
    #IF CORRECT, MOVE CHARACTER OUTWARD
    if thisResponse:
        if numReversals == 0:
            angle += 5
        else:
            angle += 1
    #IF INCORRECT, MOVE CHARACTER INWARD, INCREMENT NUMREVERSALS
    else:
        if angle > 0:
            angle -= 1
            numReversals += 1
    #COMPLETE STAIRCASE IF THE MAX ANGLE IS REACHED, OR 3 REVERSALS OR 25 RESPONSES OCCUR
    if numReversals >= 3 or responses >= 25 or angle > maxAngle:
        stairCaseCompleted = True
        
    return stairCaseCompleted, angle, numReversals, thisResponse, responses

#CONVERT DEGREE INPUT TO DISTANCE IN CENTIMETERS
def angleCalc(angle):
    radians = math.radians(angle)
    spacer = (math.tan(radians)*35)
    return spacer
    
#GENERATE A RANDOMIZED 3X3 ARRAY OF LETTERS, RETURN CENTER LETTER
def genArray():
    array = ''
    list = ['']*11
    for i in range(11):
        if i == 3 or i == 7:
            list[i] = '\n'
        else:
            list[i] = random.choice(letters)
    array = ''.join(list)
    return array, list[5]

#CALCULATE DISPLAY COORDINATES AND HEIGHT OF STIMULI
def displayVariables(angle, dir):
    #DISPLAY HEIGHT AND DISTANCE FROM CENTER IN CENTIMETERS
    heightCm = (angleCalc(size)*2.3378)
    angleCm = angleCalc(angle)
    #X AND Y DISPLAY COORDINATES
    xPos = (dirXMult[dir]*angleCm) 
    yPos = (dirYMult[dir]*angleCm) + yOffset[dir]
    #ADJUSTMENT TO CENTER CHARACTER
    if angle == 0 and dir%2 != 0:
        yPos += 0.2
    return heightCm, angleCm, xPos, yPos

#DISPLAY INSTRUCTIONS FOR CHINREST ALIGNMENT
instructions = genDisplay('  Align the edge of the headrest stand \nwith the edge of the tape marked 35cm \n\n       Press Spacebar to continue', 0, 5, 5, 'black')
instructions.draw()
win.flip()
theseKeys = event.waitKeys(keyList = ['space', 'escape'], clearEvents = False)
if theseKeys[0] == 'escape':
    endExp()

#GENERATE CENTER DOT
dot = genDisplay('.', 0, 1.1, 3, 'red')

#RANDOMIZE SIZES, LOOP THROUGH 
shuffle(sizes)
for size in sizes:
    
    #RANDOMIZE DIRECTIONS, LOOP THROUGH
    shuffle(directions)
    for dir in directions:
        
        #INITIALIZE TRIAL VARIABLES
        angle = 0
        numReversals = 0
        responses = 0
        stairCaseCompleted = False
        lastResponse = False
        
        #SET ANGLE LIMIT (EDGE OF SCREEN)
        maxAngle = maxAngles[dir]
        
        while not stairCaseCompleted:
            
            #GENERATE NEW STIMULI
            array, letter = genArray()
            heightCm, angleCm, xPos, yPos = displayVariables(angle, dir)
            displayText = genDisplay(array, xPos, yPos, heightCm, 'black')
            
            dot.draw()
            win.flip()
            
            time.sleep(0.5)
            
            #DRAW STIMULI, CLEAR KEYPRESS LOG
            dot.draw()
            displayText.draw()
            win.callOnFlip(keyPress.clearEvents, eventType='keyboard')
            win.flip()
            
            #SUSPEND EXECUTION UNTIL KEYPRESS
            theseKeys = event.waitKeys(keyList = ['e', 'p', 'b', 'escape', 'space'], clearEvents = False)
            
            #STOP SCRIPT IF ESCAPE IS PRESSED
            if theseKeys[0] == 'escape':
                endExp()
            
            #CHECK KEYPRESS AGAINST TARGET LETTER
            thisResponse = (letter.lower() == theseKeys[0])
            
            #CALL STAIRCASE ALGORITHM
            stairCaseCompleted, angle, numReversals, lastResponse, responses = stairCase(thisResponse, numReversals, angle, stairCaseCompleted, lastResponse, responses, maxAngle)
            
            if stairCaseCompleted:
                #ADVANCE DIRECTION
                direction = dir+1
                #CSV OUTPUT
                if recordData:
                    csvOutput([direction, size, angle])

endExp()