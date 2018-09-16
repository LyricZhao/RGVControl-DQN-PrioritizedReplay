import gym
from RL_brain import DQNPrioritizedReplay
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf

import gc
import sys
import random

from env import RGVEnv

MEMORY_SIZE = 10000

cases = [
[20, 33, 46, 560, 400, 378, 28, 31, 25, False],
[23, 41, 59, 580, 280, 500, 30, 35, 30, False],
[18, 32, 46, 545, 455, 182, 27, 32, 25, False]
]

rstr = ['10101010', '01010101', '10101110', '10100010', '01011101', '01010001']

def re_test(RL, env, has_break):
    observation = env.reset()
    env.change_break(has_break)
    while True:
        action = RL.choose_action(observation, no_rand = True)
        observation_, reward, done = env.step(action)
        observation = observation_
        if done:
            return env.rgv.global_working_ratio()
    return -1

def run_step_case(case, final_steps, rgvs, cnc_st, cid):
    env = RGVEnv(case + [cnc_st], rgvs)
    hpc_file = 'output/' + cnc_st + 'nn_case' + str(cid) + '_model_step_' + str(rgvs) + '.csv'
    max_file_no_break = 'output/' + cnc_st + 'nn_case' + str(cid) + '_best_step_' + str(rgvs) + '_no_break.dt'
    max_file_with_break = 'output/' + cnc_st + 'nn_case' + str(cid) + '_best_step_' + str(rgvs) + '_with_break.dt'
    hpc_csv = []
    mfnb = []; mfnb_v = 0
    mfwb = []; mfwb_v = 0
    with tf.Session() as sess:
        with tf.variable_scope('DQN_with_prioritized_replay', reuse = tf.AUTO_REUSE):
            RL = DQNPrioritizedReplay(
                n_actions=8, n_features=9, memory_size=MEMORY_SIZE,
                e_greedy_increment=None, sess=sess, prioritized=True, output_graph=True,
            )
        sess.run(tf.global_variables_initializer())

        step = 0
        for episode in range(final_steps):
            # initial observation
            observation = env.reset()
            env.change_break(False)

            while True:

                # RL choose action based on observation
                action = RL.choose_action(observation)

                # RL take action and get next observation and reward
                observation_, reward, done = env.step(action)

                RL.store_transition(observation, action, reward, observation_)

                if (step > 200) and (step % 5 == 0):
                    RL.learn()

                # swap observation
                observation = observation_

                # break while loop when end of this episode
                if done:
                    training_ratio = env.rgv.global_working_ratio()

                    # play again
                    real_ratio_no_break   = re_test(RL, env, False)
                    if real_ratio_no_break > mfnb_v:
                        mfnb = env.log
                        mfnb_v = real_ratio_no_break
                        print 'meeting max no break =', real_ratio_no_break

                    real_ratio_with_break = re_test(RL, env,  True)
                    if real_ratio_with_break > mfwb_v and env.break_tot > 0:
                        mfwb = env.log
                        mfwb_v = real_ratio_with_break
                        print 'meeting max with break =', real_ratio_with_break

                    print 'episode:', episode, 'tr:', training_ratio, 'rrnb:', real_ratio_no_break, 'rrwb:', real_ratio_with_break
                    hpc_csv.append([episode, training_ratio, real_ratio_no_break, real_ratio_with_break])
                    break
                step += 1
        del RL
        del sess
        gc.collect()

    # save file
    with open(hpc_file, 'w') as f:
        for i in hpc_csv:
            f.write(','.join([str(j) for j in i]) + '\n')
        f.close()

    with open(max_file_no_break, 'w') as f:
        for i in mfnb:
            f.write(str(i[0]) + ' ' + str(i[1]) + ' ')
        f.close()

    with open(max_file_with_break, 'w') as f:
        for i in mfwb:
            f.write(str(i[0]) + ' ' + str(i[1]) + ' ')
        f.close()

def rand_str():
    v = random.randint(3, 5)
    arr = []
    for i in range(0, v): arr.append('1')
    for i in range(0, 8 - v): arr.append('0')
    random.shuffle(arr)
    return ''.join(arr)

if __name__ == "__main__":
    for i in range(0, 3):
        print 'starting to run case #', i
        run_step_case(cases[i], 400, 1, '', i)
        print 'case #', i, 'done !!!\n'

    for i in range(0, 3):
        print 'starting to run case #', i
        for j in rstr:
            print 'shape:', j
            run_step_case(cases[i], 300, 2, j, i)
        print 'case #', i, 'done !!!\n'

    print 'all done !!!'
