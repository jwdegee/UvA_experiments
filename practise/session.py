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
        self.volume = pd.read_csv(os.path.join(os.path.abspath(os.getcwd()), 'volumes', '{}.csv'.format(self.subject_initials)))
        
        # sound_files = glob.glob(os.path.join('/Users/jwdegee/Documents/repos/UvA_experiments/sounds/', '*.wav'))
        sound_files = glob.glob(os.path.join('/Users/beauchamplab/Documents/jwdegee/repos/UvA_experiments/sounds/', '*.wav'))

        self.sounds = {}
        for sf in sound_files:
            sound_name = os.path.splitext(os.path.split(sf)[-1])[0]
            sound_var = sound.Sound(sf)
            self.sounds.update({sound_name: sound_var})

        self.config = config
        self.create_trials()
        self.setup_stimuli()
        self.stopped = False

    def create_trials(self):
        """creates trials by creating a restricted random walk through the display from trial to trial"""

        stim = list(np.concatenate((np.ones(int(self.config['signal_probability']*10)),np.zeros(int((1-self.config['signal_probability'])*10)))))
        print(stim)
        self.trial_parameters = []
        for t in xrange(self.config['trials_n'] / len(stim)):
            for s in stim:
                self.trial_parameters.append({'duration_intro': 0, #1 + np.random.exponential(1.5),
                                             'duration_delay' : np.random.uniform(0.75,1.25),
                                             'duration_decision': 2.5,
                                             'present': s,
                                             'signal_probability': self.config['signal_probability'],
                                             'volume': self.volume.loc[self.index_number,'volume']
                                             })
        
        # shuffle:
        random.shuffle(self.trial_parameters)
        
        # fix duration into screen:
        for t in np.arange(self.config['trials_n'])[::self.config['block_size']]:
            self.trial_parameters[t]['duration_intro'] = 30

    def setup_stimuli(self):
        size_fixation_pix = self.deg2pix(self.config['fixation_size'])

        self.fixation = visual.GratingStim(self.screen,
                                           pos=(0,0),
                                           tex='sin',
                                           mask='circle',
                                           size=size_fixation_pix,
                                           texRes=9,
                                           color='white',
                                           sf=0)

        if self.version_number == 1:
            this_instruction_string = """Signal present? Press 'f' for no and 'j' for yes."""
        elif self.version_number == 2:
            this_instruction_string = """Signal present? Press 'f' for yes and 'j' for no."""
        this_instructing2_string = """Press either to start."""
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
        
        self.target = self.sounds['TORC_TARGET']
        self.target.setVolume(self.volume.loc[self.index_number,'volume'])
        self.noise = self.sounds['TORC_424_02_h501']

    def run(self):
        """run the session"""

        # cycle through trials
        correct = []
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
            
            # keep track of accuracy:
            correct.append(trial.parameters['answer'] == trial.parameters['present'])
            if (trial_id != 0):
                accuracy = int(np.mean(correct[-self.config['block_size']:]) * 100)
                self.instruction.text = "{}% correct".format(accuracy)
                self.instruction2.text = "Press 'f' or 'j' to continue."

        self.close()
