import gym
from RL_brain import DQNPrioritizedReplay
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf

from env import RGVEnv

MEMORY_SIZE = 10000

if __name__ == "__main__":
    env = RGVEnv([20, 33, 46, 560, 28, 31, 25, False], rgv_step = 1)
    sess = tf.Session()
    with tf.variable_scope('DQN_with_prioritized_replay'):
        RL = DQNPrioritizedReplay(
            n_actions=8, n_features=9, memory_size=MEMORY_SIZE,
            e_greedy_increment=None, sess=sess, prioritized=True, output_graph=True,
        )
    sess.run(tf.global_variables_initializer())

    step = 0
    for episode in range(5000000):
        # initial observation
        observation = env.reset()

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
                # fresh env
                # print env.actions

                ev2 = env.rgv.global_working_ratio()
                # refresh
                observation = env.reset()
                while True:
                    action = RL.choose_action(observation, no_rand = True)
                    observation_, reward, done = env.step(action)
                    observation = observation_
                    if done:
                        print 'episode =', episode, 'ratio =', env.rgv.global_working_ratio(), 'training ratio =', ev2
                        break
                break
            step += 1

    # end of game
    print('game over')
