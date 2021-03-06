import numpy as np
from psychopy import event, core

from exptools.core.trial import Trial

class PRTrial(Trial):

    def __init__(self, ti, config, parameters, *args, **kwargs):

        self.ID = ti
        self.parameters = parameters

        phase_durations = [parameters['duration_intro'], 
                           parameters['delay'],
                           parameters['stimulation'],]
        
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
        
        self.stimulation_frame_nr = 0 

        self.noise_played = False
        exec('self.sound = self.session.pp{}_p{}'.format(parameters['prepulse'], parameters['probe']))

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
                if not self.noise_played:
                    self.sound.play(loops=None)
                    self.noise_played = True
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