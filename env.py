import gym

from gym import error, spaces, utils
from gym.utils import seeding

import numpy as np
import math

from control import rgv_system_step_1
from control import rgv_system_step_2

class RGVEnv:
    # paras = [m1, m2, m3, cw, dt, ut, break] for step 1
    # paras = tbc
    def __init__(self, paras, rgv_step = 1):
        self.origin_paras = paras
        self.actions = []
        self.max_steps = 1000
        self.cur_steps = 0
        if rgv_step == 1:
            self.rgv = rgv_system_step_1(*paras)
        else:
            self.rgv = rgv_system_step_2(*paras)

    # action means moving which one
    # return observation, reward, done
    def step(self, action):
        self.cur_steps += 1
        if self.cur_steps > self.max_steps:
            return np.array(self.rgv.state()), -1, True
        useless_step = self.rgv.take(action)
        self.actions.append(action)
        if useless_step:
            reward = -1
        else:
            reward = self.rgv.working_ratio() ** 2.5
        return np.array(self.rgv.state()), reward, self.rgv.whether_done()

    # return an observation
    def reset(self):
        self.action = []
        self.cur_steps = 0
        self.rgv.__init__(*self.origin_paras)
        return np.array(self.rgv.state())

    # display or something else
    def render(self):
        print ('rending:')
        print ('    time   = ' + str(self.rgv.cur_time / 60.0) + ' mins')
        print ('    ratio0 = ' + str(self.rgv.working_ratio()) + ' parts/h')
        print ('    ratio1 = ' + str(self.rgv.global_working_ratio()) + ' parts/h\n')
