import numpy as np
import random
import os
import json
import glob
from psychopy import visual, clock, sound, core

import exptools
from exptools.core.session import EyelinkSession
from trial import PRTrial

class PRSession(EyelinkSession):

    def __init__(self, *args, **kwargs):

        super(PRSession, self).__init__(*args, **kwargs)

        config_file = os.path.join(os.path.abspath(os.getcwd()), 'default_settings.json')

        with open(config_file) as config_file:
            config = json.load(config_file)

        self.config = config
        self.create_trials()
        self.setup_stimuli()
        self.setup_sound_system(directory='/Users/lolabeerendonk/Documents/reps/UvA_experiments/sounds/')

        self.stopped = False


    def create_trials(self):
        """creates trials by creating a restricted random walk through the display from trial to trial"""

        stim = [0,1]
        self.trial_parameters = []
        for t in xrange(self.config['nTrials'] / len(stim)):
        	for s in stim:
				self.trial_parameters.append({'duration_intro': 0, #1 + np.random.exponential(1.5),
			                                 'duration_delay' : np.random.uniform(2,3),
			                                 'duration_decision': 3,
			                                 'present': s})
        # shuffle:
        random.shuffle(self.trial_parameters)

        # fix duration into screen:
        self.trial_parameters[0]['duration_intro'] = 30
    
    def setup_stimuli(self):
        size_fixation_pix = self.deg2pix(self.config['size_fixation_deg'])

        self.fixation = visual.GratingStim(self.screen,
                                           tex='sin',
                                           mask='circle',
                                           size=size_fixation_pix,
                                           texRes=512,
                                           color='white',
                                           sf=0)

        this_instruction_string = """Signal present?\nPress 'f' for no and 'j' for yes. \nPress either key to start."""
        self.instruction = visual.TextStim(self.screen, 
            text = this_instruction_string, 
            font = 'Helvetica Neue',
            pos = (0, 0),
            italic = True, 
            height = 20, 
            alignHoriz = 'center',
            color=(1,0,0))
        self.instruction.setSize((1200,50))

        self.target = sound.Sound('TORC_TARGET.wav')
        self.target.setVolume(0.5) #this should be set based on staircase (0.08 is difficult)
        self.noise = sound.Sound('TORC_424_02_h501.wav')

    def run(self):
        """run the session"""
        # cycle through trials


        for trial_id, parameters in enumerate(self.trial_parameters):

            trial = PRTrial(ti=trial_id,
                           config=self.config,
                           screen=self.screen,
                           session=self,
                           parameters=parameters,
                           tracker=self.tracker)
            trial.run()

            if self.stopped == True:
                break

        self.close()
