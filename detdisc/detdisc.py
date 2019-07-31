""""
Auditory detection and discrimination task

Created by Stijn Nuiten on 2018-05-07.
Adapted by Lola Beerendonk, 2019

Copyright (c) 2018; All rights reserved.
"""

import numpy as np
import sounddevice, soundfile
import psychopy
from psychopy import prefs
prefs.general['audioLib'] = ['sounddevice']
prefs.general['audioDriver'] = ['portaudio']
#print(prefs)
from psychopy import sound

import os, sys, datetime
import subprocess
import pickle, datetime, time
import json
from math import *
from IPython import embed as shell
import shutil
from psychopy import logging, visual, clock, sound, event, core, monitors
from psychopy import parallel
from psychopy.sound import Sound

#import wave

logging.console.setLevel(logging.CRITICAL)

sys.path.append('/Users/lolabeerendonk/Documents/reps/exptools')
#sys.path.append('D:\USERS\Stijn\exptools')

import exptools
from exptools.core.trial import Trial
from exptools.core.session import EyelinkSession

from psychopy.tools.attributetools import attributeSetter, setAttribute
from psychopy.visual import GratingStim, TextStim, ImageStim, DotStim, Window

# The following imports are copied from simple_tracker_experiment.py
import constants
import pygaze
from pygaze import libscreen
from pygaze import libtime
from pygaze import liblog
from pygaze import libinput
from pygaze import eyetracker

p = ['FA', 'MISS']

fullscr = False
tracker_on = False
use_parallel = False
total_trials = 560
miniblocks = 4
NR_TRIALS = total_trials/miniblocks
block_length = 140

stim_size = 17
noise_size = 19

if use_parallel:
    from ctypes import windll
    portaddress = 0xA0D0
    port = windll.inpout32
    

class DetectTrial(Trial):
    def __init__(self, task, parameters = {}, phase_durations=[], session=None, screen=None, tracker=None, ID=0): # self, parameters = {}, phase_durations=[], session=None, screen=None, tracker=None, ID=0,
        
        self.task = task
        self.screen = screen
        self.parameters = parameters
        self.ID = ID
        self.phase_durations = phase_durations 

        # Version for counterbalancing the mapping of the responses between subjects
        if int(initials) % 2 == 1:
            self.version = 1
        elif int(initials) % 2 == 0:
            self.version = 2

        self.session = session
        self.block = np.floor(self.ID/self.session.block_length)
        self.tracker = tracker
        self.create_stimuli()

        if self.ID == 0:
            self.session_start_time = clock.getTime()

        self.run_time = 0.0
        self.noise_played = False
        self.signal_played = False
        self.play_sound = False
        self.prestimulation_time = self.delay_1_time = self.delay_2_time = self.answer_time = self.stimulus_time = 0.0
        self.parameters.update({'confidence':-1,
                                'answer': -1, 
                                'correct': -1,
                                'block': self.block,
                                'RT': -1
                                })
        
        self.p_v_feedback_played = self.p_a_feedback_played = self.p_stim_played = self.cue_played = self.fixLost = False

        self.stopped = False
        self.too_early = False

        super(
            DetectTrial,
            self).__init__(
            phase_durations=phase_durations,
            parameters = parameters,
            screen = self.screen,
            session = self.session,
            tracker = self.tracker          
            )

    def create_stimuli(self):
        self.target1 = sound.backend_sounddevice.SoundDeviceSound('target1.wav', secs=0.5, sampleRate=44100,stereo=True,volume=1.0)
        self.target2 = sound.backend_sounddevice.SoundDeviceSound('target2.wav', secs=0.5, sampleRate=44100, stereo=True,volume=1.0)
        self.noise = sound.backend_sounddevice.SoundDeviceSound('TORC_424_02_h501.wav', secs=0.5,sampleRate=44100,stereo=True,volume=1.0)

        self.center = ( self.screen.size[0]/2.0, self.screen.size[1]/2.0 )
        self.noise.setVolume(1)

        if self.task == 'detect':
            if self.version == 1:
                intro_text = """
                Your task is to detect the target tone embedded in noise.\n\n
                Do you hear the target tone? And how confident are you?\n
                Please indicate your answer using these buttons:\n\n\n
                LEFT-green        LEFT-red           RIGHT-red         RIGHT-green\n
                no and sure     no and unsure      yes and unsure     yes and sure\n\n
                Press the spacebar to start."""   
            elif self.version == 2: 
                intro_text = """
                Your task is to detect the target tone embedded in noise.\n\n
                Do you hear the target tone? And how confident are you?\n
                Please indicate your answer using these buttons:\n\n\n
                LEFT-green         LEFT-red          RIGHT-red         RIGHT-green\n
                yes and sure     yes and unsure      no and unsure     no and sure\n\n
                Press the spacebar to start."""
        elif self.task == 'discrim':
            if self.version == 1:
                intro_text = """
                Your task is to discriminate between two target tones embedded in noise.\n\n
                Do you hear the high or the low tone? And how confident are you?\n
                Please indicate your answer using these buttons:\n\n\n
                LEFT-green          LEFT-red           RIGHT-red         RIGHT-green\n
                low and sure     low and unsure      high and unsure     high and sure\n\n
                Press the spacebar to start."""
            elif self.version == 2:
                intro_text = """
                Your task is to discriminate between two target tones embedded in noise.\n\n
                Do you hear the high or the low tone? And how confident are you?\n
                Please indicate your answer using these buttons:\n\n\n
                LEFT-green          LEFT-red            RIGHT-red         RIGHT-green\n
                high and sure     high and unsure      low and unsure     low and sure\n\n
                Press the spacebar to start."""

        if (self.ID % self.session.block_length == 0 and self.ID > 0) or self.session.trial_counter == self.session.nr_trials: #This entire section doesn't work when you initiate each block separately
            early = len(np.array(self.session.corrects)[-self.session.block_length:][np.array(self.session.corrects)[-self.session.block_length:] == -2]) / float(self.session.block_length) * 100.0
            misses = len(np.array(self.session.corrects)[-self.session.block_length:][np.array(self.session.corrects)[-self.session.block_length:] == -1]) / float(self.session.block_length) * 100.0
            no_ans = len(np.array(self.session.corrects)[-self.session.block_length:][np.array(self.session.corrects)[-self.session.block_length:] == -1]) + len(np.array(self.session.corrects)[-self.session.block_length:][np.array(self.session.corrects)[-self.session.block_length:] == -2])
            #calculate performance only over answered trials (i.e. block length - misses - early)
            perf = np.array(self.session.corrects)[-self.session.block_length:][np.array(self.session.corrects)[-self.session.block_length:] >= 0].sum() / (float(self.session.block_length)-no_ans) * 100.0

            print(self.session.signal_volume)
            print(self.session.step_size)
            
            # Adjust signal volume according to performance. If performance deviates 5-10% of target performance, adjust volume 5% of original volume (fixed step sizes). If performance deviates more than 10%, adjust 10%.
            if 65 < perf <= 70:
                self.session.signal_volume = self.session.signal_volume+.5*self.session.step_size
            elif perf <= 65:
                self.session.signal_volume = self.session.signal_volume+self.session.step_size
            elif 80 <= perf < 85:
                self.session.signal_volume = self.session.signal_volume-.5*self.session.step_size
            elif perf >= 85:
                self.session.signal_volume = self.session.signal_volume-self.session.step_size

            if 70 <= perf <= 80:
                part1 = """\n%i%% correct! The volume will stay te same.""" % (perf)
            else: 
                part1 = """\n%i%% correct! The volume will be adjusted.""" % (perf)

            conf = np.array(self.session.confidence)[-self.session.block_length:][np.array(self.session.confidence)[-self.session.block_length:] >= 0].sum() / float(self.session.block_length) * 100.0
            if conf<40 or conf>60:
                feedback_text = part1 + """\n\nYou were more confident in %i%% of the trials. Please try to keep this to 50%%.\n\nYou responded too quickly to %i%% of trials and you missed %i%% of trials. Please try to keep this to a minimum.\n\nPress the spacebar to continue.""" % (conf,early,misses)     
            else:
                feedback_text = part1 + """\n\nYou were more confident in %i%% of the trials.\n\nYou responded too quickly to %i%% of trials and you missed %i%% of trials. Please try to keep this to a minimum.\n\nPress the spacebar to continue.""" % (conf,early,misses)    

            print(str(perf) + ' percent correct') 
            print(str(conf) + ' percent high conf')
            print(str(early) + ' percent fast response trials')
            print(str(misses) + ' percent missed trials')
        else: 
            feedback_text = None
        
        if self.ID > 0:
            self.feedback = visual.TextStim(self.screen, font='avenir', pos=[0,0],text=feedback_text, color = (-1.0,-1.0,-1.0),wrapWidth=900)                           
        self.message = visual.TextStim(self.screen, font='avenir', pos=[0,0],text=intro_text, color = (-1.0, -1.0, -1.0),wrapWidth=900)

        if self.task == 'detect' and self.ID==0:
            self.message1 = visual.TextStim(self.screen, font='avenir', pos=[0,0], text='Your task is to detect the target tone embedded in noise. You can indicate your answer using the keyboard, the precise buttons will follow. Do not press any buttons before the stimulus is over and respond within 2.5 seconds (the fixation dot will turn red if you are too early or if you miss a trial).\n\nThere is a lot of time between trials and the block will last quite long (~15 minutes). Try to perform as well as possible, keep your eyes fixated on the fixation dot and keep your eyes open as much as possible.\n\nIf your performance increases/decreases too much, the difficulty of the task will be adjusted.\n\nYou will now get to hear the target tone so you know what to look for.\n\nPress the spacebar to continue.',color = (-1.0, -1.0, -1.0),wrapWidth=900) 
        elif self.task == 'detect':
            self.message1 = visual.TextStim(self.screen,font='avenir', pos=[0,0], text='You will now get to hear the target tone again so you know what to look for.\n\nPress the spacebar to continue.',color = (-1.0, -1.0, -1.0),wrapWidth=900) 
        elif self.task == 'discrim' and self.ID==0:
            self.message1 = visual.TextStim(self.screen, font='avenir', pos=[0,0], text='Your task is to discriminate between two tones embedded in noise. You can indicate your answer using the keyboard, the precise buttons will follow. Do not press any buttons before the stimulus is over and respond within 2.5 seconds (the fixation dot will turn red if you are too early or if you miss a trial).\n\nThere is a lot of time between trials and the block will last quite long (~15 minutes). Try to perform as well as possible, keep your eyes fixated on the fixation dot and keep your eyes open as much as possible.\n\nIf your performance increases/decreases too much, the difficulty of the task will be adjusted.\n\nYou will now get to hear the target tones so you know what to look for.\n\nPress the spacebar to continue.',color = (-1.0, -1.0, -1.0),wrapWidth=900) 
        elif self.task == 'discrim':
            self.message1 = visual.TextStim(self.screen, font='avenir', pos=[0,0], text='You will now get to hear the target tones again so you know what to look for.\n\nPress the spacebar to continue.',color = (-1.0, -1.0, -1.0),wrapWidth=900) 


        self.target_tone = visual.TextStim(self.screen, font='avenir', pos=[0,+100], text='This is the target tone with noise.',color = (-1.0, -1.0, -1.0))
        self.high_tone = visual.TextStim(self.screen, font='avenir', pos=[0,+100], text='This is the high tone with noise.',color = (-1.0, -1.0, -1.0))
        self.low_tone = visual.TextStim(self.screen, font='avenir', pos=[0,+100], text='This is the low tone with noise.',color = (-1.0, -1.0, -1.0))

        #for the improved fixation dot
        self.d1 = 30 #diameter outer circle. larger option: 1.5, 0.15, 7
        self.d2 = 2 #diameter inner circle
        self.w1 = 4 #linewidth
        self.backgroundColor = (.5,.5,.5) #Set according to the backgroundcolor of the experiment
        self.fixation_color = (0,0,0)

        self.fixation1 = visual.Circle(self.screen, lineColor=self.backgroundColor, lineColorSpace = 'rgb', fillColor = self.fixation_color, fillColorSpace='rgb', size=self.d1)
        self.line1 = visual.Line(self.screen,lineWidth=self.w1,start=(self.d1/2,0),end=(-self.d1/2,0),lineColor=self.backgroundColor,lineColorSpace='rgb')
        self.line2 = visual.Line(self.screen,lineWidth=self.w1,start=(0,self.d1/2),end=(0,-self.d1/2),lineColor=self.backgroundColor,lineColorSpace='rgb')
        self.fixation2 = visual.Circle(self.screen, lineColor =self.fixation_color, lineColorSpace = 'rgb', fillColor =self.fixation_color, fillColorSpace='rgb', size=self.d2)

    def draw_fixation(self): #For the circle + cross fixation (see Thaler, Shutz, Goodale & Gegenfurtner (2013))
        self.fixation1.fillColor = 'black'
        self.fixation2.lineColor = 'black'
        self.fixation2.fillColor = 'black'
        self.fixation1.draw()
        self.line1.draw()
        self.line2.draw()
        self.fixation2.draw()

    def draw_red_fixation(self): #Red version of the circle + cross fixation
        self.fixation1.fillColor = 'red'
        self.fixation2.lineColor = 'red'
        self.fixation2.fillColor = 'red'
        self.fixation1.draw()
        self.line1.draw()
        self.line2.draw()
        self.fixation2.draw()

    def example_tones(self):
        self.message1.draw()
        self.screen.flip()
        event.waitKeys('spacebar')

        # Example tones so participants are reminded of the template.
        if self.task == 'detect':
            self.target_tone.draw()
        elif self.task == 'discrim':
            self.low_tone.draw()
        self.draw_fixation()
        self.screen.flip()

        for i in range(0,3):
            self.target1 = sound.backend_sounddevice.SoundDeviceSound('target1.wav', secs=0.5, sampleRate=44100,stereo=True,volume=1.0)
            self.target1.setVolume(0.2)
            self.noise.play()
            self.target1.play()
            core.wait(0.5)
            core.wait(1)

        core.wait(1)
        
        if self.task == 'discrim':
            self.high_tone.draw()
            self.draw_fixation()
            self.screen.flip()
            for i in range(0,3):
                self.target2 = sound.backend_sounddevice.SoundDeviceSound('target2.wav', secs=0.5, sampleRate=44100, stereo=True,volume=1.0)
                self.target2.setVolume(0.2)
                self.noise.play()
                self.target2.play()
                core.wait(0.5)
                core.wait(1)

        self.draw_fixation()
        self.screen.flip()
   
        self.message.draw()
        self.screen.flip()
    #Not so neat, but otherwise it gets stuck.
        for ev in event.waitKeys(keyList='spacebar'):
            if ev:
                self.phase_forward()

    def draw(self):
        #draw additional stimuli:
        if self.phase == 0: # 
            if self.ID % self.session.block_length == 0:
                if self.ID > 0:
                    self.feedback.draw()
                    self.screen.flip()
                    event.waitKeys('spacebar')
                self.example_tones()
            else:
                self.draw_fixation()

        if self.phase == 1: # Baseline
            self.signal_played = False
            self.draw_fixation()
            self.target1.setVolume(self.session.signal_volume)
            self.target2.setVolume(self.session.signal_volume)
            self.parameters['signal_volume']=self.session.signal_volume
            self.back_to_black = False
        if self.phase ==2:  # Stimulus presentation
            self.draw_fixation()
            if not self.noise_played:
                self.noise.play()
                self.noise_played = True
            #to turn task into discrimination       
            if task == 'detect' and self.parameters['signal_present'] == 1:
                if not self.signal_played:
                    self.target1.play()
                    self.signal_played = True
                    self.signal_played = True
            elif task == 'discrim':
                if self.parameters['disc_stim'] == 1:
                    if not self.signal_played:
                        self.target1.play()
                        self.signal_played = True  
                elif self.parameters['disc_stim'] == 2:
                    if not self.signal_played:
                        self.target2.play()
                        self.signal_played = True
                        
            if self.too_early: #turn red if subjects press during phase 2
                self.draw_red_fixation()
            
        elif self.phase == 3:# decision interval
            if self.too_early:
                self.draw_red_fixation()
            else:
                self.draw_fixation() 

        elif self.phase == 4: # ITI
        #turn red if not answered
            if self.parameters['correct'] == -1 and not self.back_to_black:
                #shell()
                self.draw_red_fixation()
                # self.draw_fixation()
            else: self.draw_fixation()

            #self.draw_fixation()

        super(DetectTrial, self).draw()

    def event(self):
        trigger = None
        for ev in event.getKeys():
            if len(ev) > 0:
                if ev in ['esc', 'escape']:
                    self.session.escape_pressed = True
                    self.events.append(
                        [-99, clock.getTime() - self.start_time])
                    self.stopped = True
                    self.session.stopped = True
                    print('run canceled by user')

                elif ev == 'space':
                    self.events.append(
                        [99, clock.getTime() - self.start_time])
                    if self.phase == 0:
                        self.phase_forward()

                if ev in ['a','s','k','l'] and self.phase == 2:
                    self.too_early = True
                    self.parameters['confidence'] = -2
                    self.parameters['answer'] = -2
                    self.parameters['correct'] = -2

                if ev in ['a','s','k','l'] and (self.phase == 3 and not self.too_early):
                    self.events.append([1,clock.getTime()-self.start_time])
                    self.parameters['RT'] = clock.getTime() - self.stim_time
                    #confidence is always the same
                    if ev in ['a','l'] and self.phase == 3:
                        self.parameters['confidence'] = 1
                    elif ev in ['s','k'] and self.phase == 3:
                        self.parameters['confidence'] = 0

                    if task == 'discrim':
                        if self.version == 1:
                            if ev in ['a','s']:
                                self.parameters['answer'] = 1
                            elif ev in ['k','l']:
                                self.parameters['answer'] = 2
                        elif self.version == 2:
                            if ev in ['a','s']:
                                self.parameters['answer'] = 2
                            elif ev in ['k','l']:
                                self.parameters['answer'] = 1
                        if self.parameters['answer'] == self.parameters['disc_stim']:
                           self.parameters['correct'] = 1
                        else:
                           self.parameters['correct'] = 0
                        # if self.session.use_parallel:
                        #     port.Out32(portaddress,self.session.p_choice_left_sure)
                        #     core.wait(self.session.p_width)
                        #     port.Out32(portaddress,0)
                        self.phase_forward()


                    elif task == 'detect': 
                        if self.version == 1:    
                            if ev in ['a','s']:
                                self.parameters['answer'] = 0
                            elif ev in ['k','l']:
                                self.parameters['answer'] = 1
                        elif self.version == 2:
                            if ev in ['a','s']:
                                self.parameters['answer'] = 1
                            elif ev in ['k','l']:
                                self.parameters['answer'] = 0
                        if self.parameters['answer'] == self.parameters['signal_present']:
                           self.parameters['correct'] = 1
                        else:
                           self.parameters['correct'] = 0
                        # if self.session.use_parallel:
                        #     port.Out32(portaddress,self.session.p_choice_left_sure)
                        #     core.wait(self.session.p_width)
                        #     port.Out32(portaddress,0)
                        self.phase_forward()
                     
            super(DetectTrial, self).key_event( event )
        
    def run(self):
        super(DetectTrial, self).run()
        self.start_time = self.session.clock.getTime()
        if tracker_on:
            self.tracker.log('trial ' + str(self.ID) + ' started at ' + str(self.start_time) )
            self.tracker.send_command('record_status_message "Trial ' + str(self.ID) + '"')
        self.events.append('trial ' + str(self.ID) + ' started at ' + str(self.start_time))

        trigger = None
        restart = 0 
        while not self.stopped:
            self.run_time = clock.getTime() - self.start_time
                            
            if self.phase == 0:
                self.prestimulation_time = clock.getTime()
                # For all trials that are not FTIB, skip phase 0
                if self.ID != 0 and self.ID % self.session.block_length != 0:
                    if ( self.prestimulation_time  - self.start_time ) > self.phase_durations[0]:
                        self.phase_forward()
                
            elif self.phase == 1:  # pre-stim cue; phase is timed
                self.delay_1_time = clock.getTime()
                if ( self.delay_1_time - self.prestimulation_time ) > self.phase_durations[1]:
                    self.phase_forward()

            elif self.phase == 2:  # stimulus presentation; phase is timed
                self.stim_time = clock.getTime()
                    
                if ( self.stim_time - self.delay_1_time ) > self.phase_durations[2]: 
                    self.phase_forward()

            elif self.phase == 3:              # Decision interval; phase is timed, but aborted at response
                self.answer_time = clock.getTime()
                if self.parameters['answer'] != -1 and self.parameters['answer'] != -2: #end phase when respond
                    self.phase_forward()
                if ( self.answer_time  - self.stim_time) > self.phase_durations[3]: #end phase after some time when no response
                    self.phase_forward()

            elif self.phase == 4: #ITI

                self.ITI_time = clock.getTime()
                self.too_early = False # Reset for next trial
                if (self.ITI_time - self.answer_time) > 0.5:
                    self.back_to_black = True
                if ( self.ITI_time - self.answer_time ) > self.phase_durations[4]:
                    self.stopped = True
                    self.stop()
                    return
            
            # events and draw:
            self.event()
            self.draw()
                        
        # we have stopped:
        self.stop()

class DetectSession(EyelinkSession):
    def __init__(self, subject_initials, task, nr_trials, block_length, index_number=1, tracker_on=False, use_parallel=False, miniblock=0):
        super(DetectSession, self).__init__(subject_initials,index_number)
        config_file = os.path.join(os.path.abspath(os.getcwd()), 'default_settings.json')

        self.create_screen(  size=[1920, 1080],full_screen = fullscr, background_color = (0.5, 0.5, 0.5), physical_screen_distance = 80, engine = 'pygaze') #,  ,

        self.goodbye = visual.TextStim(self.screen, pos=[0,0],font='avenir', text='This is the end of this block.\n\nThis window will close automatically.',color = (-1.0, -1.0, -1.0))
        self.miniblock=miniblock
        self.block_length = block_length
        self.nr_trials = nr_trials
        self.index_number = index_number
        self.task = task 
        self.back_to_black = False

        if tracker_on:
            pygaze.settings.EVENTDETECTION = 'native'
            self.create_tracker(sensitivity_class = 1, sample_rate=500) #
            print self.tracker.connected()
            self.tracker_setup(sensitivity_class = 1, sample_rate=500)

        #Took out self.create_output_filename() because I don't like the filenames with the date and time in it.
        datadir = os.path.join('data', self.task, str(self.subject_initials))
        
        if not os.path.exists(datadir):
            os.makedirs(datadir)     

        #if a file already exists, add a number to the file until it doesn't exist. 
        if not os.path.isfile(datadir + '/' + str(self.subject_initials) + '_' + str(self.task) + '_' + str(self.index_number) + '_' + str(self.miniblock) + '_outputDict.pkl'):
            #shell()
            self.output_file = os.path.join(datadir, str(self.subject_initials) + '_' + self.task + '_' + str(self.index_number) + '_' + str(self.miniblock))  
        else:
            print('file already exists')
            #shell()
            i=1
            while True:
                if not os.path.isfile(datadir + '/' + str(self.subject_initials) + '_' + self.task + '_' + str(self.index_number) + '_' + str(self.miniblock) + '__' + str(i) + '_outputDict.pkl'):
                    self.output_file = os.path.join(datadir, str(self.subject_initials) + '_' + self.task + '_' + str(self.index_number) + '_' + str(self.miniblock) + '__' + str(i))
                    print('New file name: ', self.output_file)
                    break
                i += 1  

        self.use_parallel = use_parallel
        self.p_width = 5/float(1000)
        # Trigger values
        run_start_trigger = {'discrim':125 , 'detect':126}
        
        self.p_run_start = run_start_trigger[self.task]
        self.p_run_end = 126                        #
        self.p_cue = 5                              #
        self.p_stimulus_left = 8                    #
        self.p_stimulus_right = 9                   #
        self.p_stimulus_noise = 10                  #
        self.p_choice_left_sure = 16                #
        self.p_choice_left_unsure = 17              #
        self.p_choice_right_sure = 18               #
        self.p_choice_right_unsure = 19             #
        self.p_feedback_sound = 32                  #
        self.p_feedback_visual = 33 

        self.create_yes_no_trials()

    def create_yes_no_trials(self):
        """creates trials for yes/no runs"""
        try:
            self.signal_volume= np.array([np.loadtxt(os.getcwd() + '/data/' + self.task + '_staircase/participant_' + initials + '/' + initials + '_' + self.task + '_threshold.txt')]) 
        except:
            raise NameError('no staircase data for participant')  
        print(self.signal_volume)
        if self.signal_volume < 0.01:
            shell()
            self.signal_volume = 0.01
            print(self.signal_volume)

        self.step_size = self.signal_volume*.05 #Fixed step size (5% of original volume) to adjust volume during the task.

        self.signal_present = np.array([0,1])
        self.disc_stim = np.array([1,2])
        # standard parameters (same for all trials):
        self.standard_parameters = {'signal_volume': self.signal_volume,
                                    'miniblock': self.miniblock,
                                    }
        
        # create yes-no trials in nested for-loop:
        self.trial_parameters_and_durs = []    
        self.trial_counter = 0
        self.total_duration = 0
        for i in range(self.nr_trials/self.signal_present.shape[0]):
            for j in range(self.signal_present.shape[0]):

                # phase durations, and iti's:
                phase_durs = [-0.01, 0.6, 0.5, 2.5, np.random.uniform(3,4)]

                params = self.standard_parameters
                params.update({'signal_present': self.signal_present[j]})
                params.update({'disc_stim': self.disc_stim[j]})

                self.trial_parameters_and_durs.append([params.copy(), np.array(phase_durs)])
                self.total_duration += np.array(phase_durs).sum()

                self.trial_counter += 1

        self.run_order = np.argsort(np.random.rand(len(self.trial_parameters_and_durs)))

        # print params:
        print("number trials: %i." % self.trial_counter)
        if self.trial_counter != NR_TRIALS:
            raise ValueError('number of created trials does not match pre-defined number of trials')

        print("total duration: %.2f min." % (self.total_duration / 60.0))

    def run(self):
        """run the session"""
        # cycle through trials
        self.corrects = []
        self.answers = []
        self.confidence = []
        self.clock = clock

        self.escape_pressed = False

        #trigger:
        #--------
        if self.use_parallel:
          port.Out32(portaddress,self.p_run_start)
          core.wait(self.p_width)
          port.Out32(portaddress,0)
          print('trigger!')
        
        if tracker_on:
            self.tracker.status_msg('run started at ' + str(clock.getTime()) + ' trigger ' + str(self.p_run_start) )
        
        self.start_time = clock.getTime()
                
        # Display black - white - black screens to determine pupil size limits
        self.center = ( self.screen.size[0]/2.0, self.screen.size[1]/2.0 )
        self.fixation = visual.Circle(self.screen,lineColor=(.5,.5,.5),lineColorSpace='rgb', fillColor = (.5,.5,.5), fillColorSpace='rgb', size=4)
        self.baseline_instruct = visual.TextStim(self.screen, text = 'Keep looking at the dot.', font = 'avenir', pos = (0,0 ), color = 'black')
        
        if tracker_on:
            if self.miniblock==0:
                t0 = clock.getTime()
                while clock.getTime() - t0 < 5:
                    self.fixation.draw()
                    self.baseline_instruct.draw()
                    self.screen.flip()
            
                t1 = clock.getTime()
                self.tracker.status_msg('pupil baseline 1 started ' + str(clock.getTime())  )
                while clock.getTime() - t1 < 15:
                    self.screen.color=(-1,-1,-1)
                    self.fixation.draw()
                    self.screen.flip()
                self.tracker.status_msg('pupil baseline 1 ended ' + str(clock.getTime())  )     

                t2 = clock.getTime()
                self.tracker.status_msg('pupil baseline 2 started ' + str(clock.getTime())  )               
                while clock.getTime() - t2 < 15:
                    self.screen.color=(1,1,1)
                    self.fixation.draw() 
                    self.screen.flip()  
                self.tracker.status_msg('pupil baseline 2 ended ' + str(clock.getTime())  )
                
                t3 = clock.getTime()
                self.tracker.status_msg('pupil baseline 3 started ' + str(clock.getTime())  )
                while clock.getTime() - t3 < 3:
                    self.screen.color=(-1,-1,-1)
                    self.fixation.draw()
                    self.screen.flip()
                self.tracker.status_msg('pupil baseline 3 ended ' + str(clock.getTime())  )
                
            self.screen.color=(0.5, 0.5, 0.5)
            self.screen.flip()
        
        self.trial_counter = 0

        while self.trial_counter < self.nr_trials:
            
            if self.trial_counter == self.nr_trials: 
                this_trial = DetectTrial(task=task, parameters=self.trial_parameters_and_durs[self.run_order[self.trial_counter]][0], phase_durations=[-0.01, 0.6, 0.5, 2.5, 4 ], session=self, screen=self.screen, tracker=self.tracker, ID=self.trial_counter)
            else:      
                this_trial = DetectTrial(task=task, parameters=self.trial_parameters_and_durs[self.run_order[self.trial_counter]][0], phase_durations=self.trial_parameters_and_durs[self.run_order[self.trial_counter]][1], session=self, screen=self.screen, tracker=self.tracker, ID=self.trial_counter)
            this_trial.run()    
            print(self.trial_counter)
            print(self.signal_volume)
            self.corrects.append(this_trial.parameters['correct'])
            self.confidence.append(this_trial.parameters['confidence']) 

            if self.stopped == True:
                break
            self.trial_counter += 1

        self.stop_time = clock.getTime()

        perf = np.array(self.corrects)[-self.block_length:][np.array(self.corrects)[-self.block_length:] >= 0].sum() / float(self.block_length) * 100.0
        early = len(np.array(self.corrects)[-self.block_length:][np.array(self.corrects)[-self.block_length:] == -2]) / float(self.block_length) * 100.0
        misses = len(np.array(self.corrects)[-self.block_length:][np.array(self.corrects)[-self.block_length:] == -1]) / float(self.block_length) * 100.0
        conf = np.array(self.confidence)[-self.block_length:][np.array(self.confidence)[-self.block_length:] >= 0].sum() / float(self.block_length) * 100.0
        
        self.signal_volume= np.loadtxt(os.getcwd() + '/data/' + self.task + '_staircase/participant_' + initials + '/' + initials + '_' + self.task + '_threshold.txt') 
        self.step_size = self.signal_volume*.05 #Fixed step size (5% of original volume) to adjust volume during the task.

        # Adjust signal volume according to performance. If performance deviates 5-10% of target performance, adjust volume 5% of original volume (fixed step sizes). If performance deviates more than 10%, adjust 10%.
        if 65 < perf <= 70:
            self.signal_volume = self.signal_volume+.5*self.step_size
        elif perf <= 65:
            self.signal_volume = self.signal_volume+self.step_size
        elif 80 <= perf < 85:
            self.signal_volume = self.signal_volume-.5*self.step_size
        elif perf >= 85:
            self.signal_volume = self.signal_volume-self.step_size

        #shell() 
        if not self.escape_pressed:
            f = open(os.getcwd() + '/data/' + self.task + '_staircase/participant_' + initials + '/' + initials + '_' + self.task + '_threshold.txt','w')
            f.write(str(self.signal_volume))
            f.close()

        if 70 <= perf <= 80:
            part1 = """\n%i%% correct! The volume will stay te same.""" % (perf)
        else: 
            part1 = """\n%i%% correct! The volume will be adjusted.""" % (perf)

        conf = np.array(self.confidence)[-self.block_length:][np.array(self.confidence)[-self.block_length:] >= 0].sum() / float(self.block_length) * 100.0
        if conf<40 or conf>60:
            feedback_text = part1 + """\n\nYou were more confident in %i%% of the trials. Please try to keep this to 50%%.\n\nYou responded too quickly to %i%% of trials and you missed %i%% of trials. Please try to keep this to a minimum.\n\nThis screen will close automatically.""" % (conf,early,misses)     
        else:
            feedback_text = part1 + """\n\nYou were more confident in %i%% of the trials.\n\nYou responded too quickly to %i%% of trials and you missed %i%% of trials. Please try to keep this to a minimum.\n\nThis screen will close automatically.""" % (conf,early,misses)    

        print(str(perf) + ' percent correct') 
        print(str(conf) + ' percent high conf')
        print(str(early) + ' percent fast response trials')
        print(str(misses) + ' percent missed trials')

        self.feedback = visual.TextStim(self.screen, font='avenir', pos=[0,0],text=feedback_text, color = (-1.0,-1.0,-1.0),wrapWidth=1900) 

        self.feedback.draw()
        self.screen.flip()
        core.wait(10)

        print('elapsed time: %.2fs' %(self.stop_time-self.start_time))

        if self.tracker_on:
            self.tracker.status_msg('run ended at ' + str(clock.getTime()) + ' trigger ' + str(self.p_run_end) )
        
        self.screen.clearBuffer

        self.close()

def main(initials, task, nr_trials, block_length, index_number, miniblock=0):
    ts = DetectSession(subject_initials=initials, nr_trials=NR_TRIALS, block_length = block_length,  index_number=index_number, tracker_on=tracker_on, use_parallel=use_parallel, task=task,miniblock=miniblock)
    ts.run()

    if not os.path.exists('data/' + task + '/' + initials + '/'):
        os.makedirs('data/' + task +'/' + initials + '/')     

if __name__ == '__main__':
    # Store info about the experiment session
    initials = raw_input('Participant: ') 
    task = raw_input('detect or discrim: ') # 
    index_number = int(raw_input('Which session: ')) 
    miniblock = int(raw_input('Which block: ')) 

    main(initials=initials, index_number=index_number, block_length = block_length, nr_trials=NR_TRIALS, task = task, miniblock = miniblock)

