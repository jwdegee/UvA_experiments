from exptools.core.trial import Trial
import os
import exptools
import json
from psychopy import logging, visual, event
import numpy as np


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
            self.session.play_sound( sound_index='TORC_424_02_h501') #maxtime=self.parameters['duration_decision']*1000)
            # if self.parameters['present']:
            #     self.session.play_sound( sound_index='TORC_TARGET') #, maxtime=self.parameters['duration_decision']*1000)
            
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

                elif ev in ('f','j'):
                    if (self.phase == 0) * (self.ID == 0):
                        self.phase_forward()                    
                    elif (self.phase == 2):
                        self.parameters['answer'] = ['f','j'].index(ev)
                        self.stop() 

            super(PRTrial, self).key_event(ev)

    def phase_forward(self):

        super(PRTrial, self).phase_forward()

