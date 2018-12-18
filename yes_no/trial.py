import numpy as np
from psychopy import event

from exptools.core.trial import Trial

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

        self.config = config
        self.noise_played = False
        self.signal_played = False
        self.parameters['answer'] = -1

    def draw(self, *args, **kwargs):
        
        self.session.fixation.color = 'white'
        self.session.fixation.draw()

        # draw additional stimuli:
        if (self.phase == 0):
            self.session.instruction.draw()
            self.session.instruction2.draw()

        elif self.phase == 1: # delay
            pass
            
        elif self.phase == 2: # decision interval
            self.session.fixation.color = 'blue'
            self.session.fixation.draw()
            if not self.noise_played:
                self.session.noise.play(loops=None)
                self.noise_played = True
            if self.parameters['present']:
                if not self.signal_played:
                    self.session.target.play(loops=None) #, maxtime=self.parameters['duration_decision']*1000)
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

                elif ev in ['f', 'j']:
                    if (self.phase == 0):
                        self.phase_forward()
                    elif (self.phase == 2):
                        if ev == 'f':
                            self.parameters['answer'] = 0
                        elif ev == 'j':
                            self.parameters['answer'] = 1
                        self.parameters['answer_time'] = self.this_phase_time
                        self.session.noise.stop()
                        self.session.target.stop()
                        self.stop() 


            super(PRTrial, self).key_event(ev)

    def phase_forward(self):
        
        super(PRTrial, self).phase_forward()


        # if (self.phase == 2) & (self.ID % self.config['block_size'] == 0) & (self.ID != 0):
        #     self.session.instruction.draw()
        #     print('sleep')
        #     time_module.sleep(5)