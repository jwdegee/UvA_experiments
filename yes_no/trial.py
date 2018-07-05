from exptools.core.trial import Trial
import os
import exptools
import json
from psychopy import logging, visual, clock, event
from psychopy import sound, core
import numpy as np

import pyaudio
import wave
import sys



#print('Using %s (with %s) for sounds' % (sound.audioLib, sound.audioDriver))

class PRTrial(Trial):



    def __init__(self, ti, config, parameters, *args, **kwargs):

        self.ID = ti
        # self.parameters = parameters

        phase_durations = [parameters['duration_intro'], 
                           parameters['duration_delay'],
                           parameters['duration_decision'],]
        
        super(
            PRTrial,
            self).__init__(
            phase_durations=phase_durations,
            parameters=parameters,
            *args,
            **kwargs)

        self.noise_played = False
        self.signal_played = False

    def draw(self, *args, **kwargs):

        # draw additional stimuli:
        if (self.phase == 0 ) * (self.ID == 0):
            self.session.fixation.color = 'white'
            self.session.instruction.draw()

        if self.phase == 0: # intro text
            self.session.fixation.color = 'white'
            self.session.fixation.draw()

        elif self.phase == 1: # delay
            self.session.fixation.color = 'white'
            self.session.fixation.draw()


        elif self.phase == 2: # decision interval
            self.session.fixation.color = 'blue'
            self.session.fixation.draw()
            if not self.noise_played:
                self.session.noise.play(loops=None)
                self.noise_played = True
            #self.session.play( sound_index='TORC_424_02_h501') #maxtime=self.parameters['duration_decision']*1000)
            if self.parameters['present']:
                if not self.signal_played:
                    self.session.target.play()  #, maxtime=self.parameters['duration_decision']*1000)
                    self.signal_played = True

        super(PRTrial, self).draw()

    def event(self):
        for ev in event.getKeys():
            if len(ev) > 0:
                if ev in ['esc', 'escape', 'q']:
                    self.events.append(
                        [-99, self.session.clock.getTime() - self.start_time])
                    self.stopped = True
                    self.session.stopped = True
                    print 'run canceled by user'

                elif ev in ['a', 's', 'k', 'l']:
                    if (self.phase == 0) * (self.ID == 0):
                        self.phase_forward()                    
                    elif (self.phase == 2):
                        if ev == 'a':
                            self.parameters['answer'] = 0
                            self.parameters['confidence'] = 1
                        elif ev == 's':
                            self.parameters['answer'] = 0
                            self.parameters['confidence'] = 0
                        elif ev == 'k':
                            self.parameters['answer'] = 1
                            self.parameters['confidence'] = 0
                        elif ev == 'l':
                            self.parameters['answer'] = 1
                            self.parameters['confidence'] = 1
                        self.parameters['answer_time'] = self.this_phase_time
                        self.session.noise.stop()
                        self.session.target.stop()
                        self.stop() 


            super(PRTrial, self).key_event(ev)

    def phase_forward(self):

        super(PRTrial, self).phase_forward()

