"""measure your JND in orientation using a staircase method"""
from psychopy import core, visual, data, event, sound
from psychopy.tools.filetools import fromFile, toFile
import numpy, random
import os, glob

subject_initials = 'test'
nr_trials = 20

expInfo = {'observer':subject_initials,}
expInfo['dateStr'] = data.getDateStr()  # add the current time

# make a text file to save data
fileName = expInfo['observer'] + expInfo['dateStr']
dataFile = open(fileName+'.csv', 'w')  # a simple text file with 'comma-separated-values'
dataFile.write('targetSide,volume,correct\n')

# create the staircase handler
staircase = data.QuestHandler(startVal=0.5, startValSd=0.05,
    pThreshold=0.65, gamma=0.5, beta=3.5, delta=0.01,
    nTrials=nr_trials, minVal=0, maxVal=1)

# create window and stimuli
win = visual.Window([1920,1080], fullscr=True, allowGUI=True,
                    monitor='testMonitor', units='deg')
fixation = visual.GratingStim(win, color=-1, colorSpace='rgb',
                              tex=None, mask='circle', size=0.2)

sound_files = glob.glob(os.path.join('/Users/beauchamplab/Documents/jwdegee/repos/UvA_experiments/sounds/', '*.wav'))
sounds = {}
for sf in sound_files:
    sound_name = os.path.splitext(os.path.split(sf)[-1])[0]
    sound_var = sound.Sound(sf)
    sounds.update({sound_name: sound_var})
target = sounds['TORC_TARGET']
noise = sounds['TORC_424_02_h501']

# and some handy clocks to keep track of time
globalClock = core.Clock()
trialClock = core.Clock()

# display instructions and wait
message1 = visual.TextStim(win, pos=[0,+3],text='Hit a key when ready.')
message2 = visual.TextStim(win, pos=[0,-3],
    text="Then press left or right to identify the deg probe.")
message1.draw()
message2.draw()
fixation.draw()
win.flip()#to show our newly drawn 'stimuli'
#pause until there's a keypress
event.waitKeys()

for trial in range(staircase.nTrials):  # will continue the staircase until it terminates!

    noise1_played = False
    noise2_played = False
    target_played = False

    # set location of stimuli
    targetSide = random.choice([0,1])  # will be either +1(right) or -1(left)

    # set volume
    target.setVolume(staircase.mean())

    fixation.color = (1,1,1)
    fixation.draw()
    win.flip()

    # play sounds 1:
    if not noise1_played:
        noise.play(loops=None)
        noise1_played = True
    if targetSide == 0:
        if not target_played:
            target.play(loops=None) #, maxtime=self.parameters['duration_decision']*1000)
            target_played = True
    core.wait(1.5)
    noise.stop()
    target.stop()

    core.wait(0.5)

    # play sounds 2:
    if not noise2_played:
        noise.play(loops=None)
        noise2_played = True
    if targetSide == 1:
        if not target_played:
            target.play(loops=None) #, maxtime=self.parameters['duration_decision']*1000)
            target_played = True
    core.wait(1.5)
    noise.stop()
    target.stop()

    # wait 500ms; but use a loop of x frames for more accurate timing
    core.wait(0.1)

    # blank screen
    fixation.color = (1,0,0)
    fixation.draw()
    win.flip()

    # get response
    thisResp=None
    while thisResp==None:
        allKeys=event.waitKeys()
        for thisKey in allKeys:
            if thisKey=='left':
                if targetSide==0: 
                    thisResp = 1  # correct
                else: 
                    thisResp = 0 # incorrect
            elif thisKey=='right':
                if targetSide==1: 
                    thisResp = 1  # correct
                else: 
                    thisResp = 0 # incorrect
            elif thisKey in ['q', 'escape']:
                core.quit()  # abort experiment
        event.clearEvents()  # clear other (eg mouse) events - they clog the buffer

    # add the data to the staircase so it can calculate the next level
    staircase.addResponse(thisResp)
    dataFile.write('%i,%.3f,%i\n' %(targetSide, staircase.mean(), thisResp))
    core.wait(1)

# staircase has ended
dataFile.close()
staircase.saveAsPickle(fileName)  # special python binary file to save all the info

# give some output to user in the command line in the output window
print('threshold = {}'.format(staircase.mean()))

win.close()

# autmatically move files:
if not os.path.exists('data/staircase/{}/'.format(subject_initials)):
    os.makedirs('data/staircase/{}/'.format(subject_initials))
os.system('mv %s %s' % (fileName + '.csv', 'data/staircase/' + subject_initials + '/' + fileName + '.csv'))

import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('data/staircase/' + subject_initials + '/' + fileName + '.csv')
fig = plt.figure()
plt.plot(df['volume'])
plt.ylabel('Volume')
plt.xlabel('Trial #')
fig.savefig('data/staircase/' + subject_initials + '/' + fileName + '.jpg')

core.quit()