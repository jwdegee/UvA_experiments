import numpy as np
from psychopy import event, core

from exptools.core.trial import Trial

class PRTrial(Trial):

    def __init__(self, ti, config, parameters, *args, **kwargs):

        self.ID = ti
        # self.parameters = parameters

        phase_durations = [parameters['duration_intro'], 
                           parameters['delay'],
                           parameters['stimulation'],]
        
        self.parameters = parameters
        
        self.background = 0.02
        
        if parameters['prepulse'] == 0:
            self.prepulse = 0.02
        elif parameters['prepulse'] == 1:
            self.prepulse = 0.10
        elif parameters['prepulse'] == 2:
            self.prepulse = 0.15
        elif parameters['prepulse'] == 3:
            self.prepulse = 0.20
        
        if parameters['probe'] == 0:
            self.probe = 0.02
        else:
            self.probe = 0.5

        self.prepulse_time = 2 # 2 frames is 20 ms at 100Hz refresh rate
        self.probe_time = 4  # 4 frames is 40 ms at 100Hz refresh rate
        self.inter_stimulus_time = 8 # 8 frames is 80 ms at 100Hz refresh rate
        self.stimulation_frame_nr = 0
        self.noise_played = False

        super(
            PRTrial,
            self).__init__(
            phase_durations=phase_durations,
            parameters=parameters,
            *args,
            **kwargs)

        self.config = config

        self.my_clock = core.Clock()
        self.current_time = self.my_clock.getTime()

    def draw(self, *args, **kwargs):
        
        self.session.fixation.color = 'black'
        self.session.fixation.draw()

        # draw additional stimuli:
        if (self.phase == 0):
            self.session.instruction.draw()
            self.session.instruction2.draw()

        elif self.phase == 1: # delay:
            delay_time = core.Clock()

        elif self.phase == 2: # stimulation

                if (self.stimulation_frame_nr <= self.prepulse_time):
                    volume = self.prepulse
                elif (self.stimulation_frame_nr > self.prepulse_time) & (self.stimulation_frame_nr <= (self.prepulse_time+self.inter_stimulus_time)):
                    volume = self.background
                elif (self.stimulation_frame_nr > (self.prepulse_time+self.inter_stimulus_time)) & (self.stimulation_frame_nr <= (self.prepulse_time+self.inter_stimulus_time+self.probe_time)):
                    volume = self.probe
                else:
                    volume = self.background
                self.session.white_noise.setVolume(volume)
                self.stimulation_frame_nr += 1
                
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
                elif ev in ['space']:
                    if (self.phase == 0):
                        self.phase_forward()

            super(PRTrial, self).key_event(ev)

    def phase_forward(self):
        
        super(PRTrial, self).phase_forward()


        # if (self.phase == 2) & (self.ID % self.config['block_size'] == 0) & (self.ID != 0):
        #     self.session.instruction.draw()
        #     print('sleep')
        #     time_module.sleep(5)