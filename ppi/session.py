import os, glob
import numpy as np
import pandas as pd
import random
import json
from psychopy import visual, clock, sound, core

import exptools
from exptools.core.session import EyelinkSession
from trial import PRTrial

class PRSession(EyelinkSession):

    def __init__(self, version_number=1, *args, **kwargs):

        super(PRSession, self).__init__(*args, **kwargs)

        config_file = os.path.join(os.path.abspath(os.getcwd()), 'default_settings.json')

        with open(config_file) as config_file:
            config = json.load(config_file)
        
        self.version_number = version_number

        self.config = config
        self.create_trials()
        self.setup_stimuli()
        self.stopped = False

    def create_trials(self):
        """creates trials by creating a restricted random walk through the display from trial to trial"""

        self.trial_parameters = []

        nr_repititions = 9
        prepulses = [0, 1, 2, 3]
        probes = [0, 1]

        prepulses = [3]
        probes = [0,1]

        for repetition in range(nr_repititions):
            for prepulse in prepulses:
                for probe in probes:
                    self.trial_parameters.append({
                                                'prepulse':prepulse,
                                                'probe':probe,
                                                'duration_intro': 0, #1 + np.random.exponential(1.5),
                                                # 'delay' : np.random.uniform(10,20),
                                                'delay' : np.random.uniform(3,5),
                                                'stimulation' : 2,
                                                })
        
        # shuffle:
        random.shuffle(self.trial_parameters)
        
        # fix duration into screen:
        self.trial_parameters[0]['duration_intro'] = 30

    def setup_stimuli(self):
        

        sound_dir = '/Users/jwdegee/Documents/repos/UvA_experiments/ppi/sounds/'
        # sound_dir = '/Users/beauchamplab/Documents/jwdegee/repos/UvA_experiments/sounds/'
        self.background = sound.Sound(os.path.join(sound_dir, 'background.wav'))
        self.pp0_p0 = sound.Sound(os.path.join(sound_dir, 'pp0_p0.wav'))
        self.pp0_p1 = sound.Sound(os.path.join(sound_dir, 'pp0_p1.wav'))
        self.pp1_p0 = sound.Sound(os.path.join(sound_dir, 'pp1_p0.wav'))
        self.pp1_p1 = sound.Sound(os.path.join(sound_dir, 'pp1_p1.wav'))
        self.pp2_p0 = sound.Sound(os.path.join(sound_dir, 'pp2_p0.wav'))
        self.pp2_p1 = sound.Sound(os.path.join(sound_dir, 'pp2_p1.wav'))
        self.pp3_p0 = sound.Sound(os.path.join(sound_dir, 'pp3_p0.wav'))
        self.pp3_p1 = sound.Sound(os.path.join(sound_dir, 'pp3_p1.wav'))

        # fixation:
        size_fixation_pix = self.deg2pix(self.config['fixation_size'])

        self.fixation = visual.GratingStim(self.screen,
                                           pos=(0,0),
                                           tex='sin',
                                           mask='circle',
                                           size=size_fixation_pix,
                                           texRes=9,
                                           color='white',
                                           sf=0)

        this_instruction_string = """Please fixate and minimize blinking"""
        this_instructing2_string = """Press spacebar to start."""
        self.instruction = visual.TextStim(self.screen, 
            text = this_instruction_string, 
            font = 'Helvetica Neue',
            pos = (0,0),
            italic = True, 
            height = 20, 
            alignHoriz = 'center',
            color=(1,0,0))
        
        self.instruction2 = visual.TextStim(self.screen, 
            text = this_instructing2_string,
            font = 'Helvetica Neue',
            pos = (0,-25),
            italic = True, 
            height = 20, 
            alignHoriz = 'center',
            color=(1,0,0))
        
    def run(self):
        """run the session"""

        self.background.play(loops=-1)

        # cycle through trials
        for trial_id, parameters in enumerate(self.trial_parameters):
            print(trial_id)
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
