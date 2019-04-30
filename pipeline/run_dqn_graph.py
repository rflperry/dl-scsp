import argparse
import gym
from gym import wrappers
import os.path as osp
import random
import numpy as np
import tensorflow as tf
import tensorflow.contrib.layers as layers
import dqn_graph_model_v2 as dqn
from dqn_utils import *
#from atari_wrappers import *
#from knapsack_env import *
# import Q_function
import Q_function as Q_function_graph_model
import tsp_env


def graph_learn(env, num_timesteps, q_func, modelfile):
    # This is just a rough estimate
    num_iterations = float(num_timesteps) / 4.0

    lr_multiplier = 1.0
    # From dqn_utils
    lr_schedule = LinearSchedule(schedule_timesteps = num_iterations, 
                                 final_p = 0.0, 
                                 initial_p=1.0)

    optimizer = dqn.OptimizerSpec(
        constructor=tf.train.AdamOptimizer,
        kwargs=dict(epsilon=1e-4),
        lr_schedule=lr_schedule
    )

    # TODO we want a stopping criterion I assume
    def stopping_criterion(env, t):
        # notice that here t is the number of steps of the wrapped env,
        # which is different from the number of steps in the underlying env
        return(env.is_done(env.state) and env.all_graphs_trained())

    exploration_schedule = LinearSchedule(schedule_timesteps = num_iterations, 
                                 final_p = 0.0, 
                                 initial_p=1.0)

    dqn.learn(
        env,
        q_func=q_func,
        pre_pooling_mlp_layers=2,
        post_pooling_mlp_layers=1,
        n_hidden_units=-1, T=4,
        initialization_stddev=1e-3,
        exploration=exploration_schedule,
        stopping_criterion=stopping_criterion,
        replay_buffer_size=100,
        batch_size=16,
        gamma=0.99,
        learning_starts=50,
        learning_freq=2,
        target_update_freq=10,
        grad_norm_clipping=10,
        double_DQN=True,
        n_steps_ahead=3,
        learning_rate=1e-4,
        LOG_EVERY_N_STEPS = 200,
        burn_in_period=50, 
        filename=modelfile
    )
    env.close()

def graph_test(session,env,q_func,modelfile):
    
    def stopping_criterion(env, t):
        # notice that here t is the number of steps of the wrapped env,
        # which is different from the number of steps in the underlying env
        return(env.is_done(env.state) and env.all_graphs_trained())
    
    dqn.test(session=session, 
             env=env, 
             q_func=Q_function_graph_model.Q_func,
             pre_pooling_mlp_layers=2,
             post_pooling_mlp_layers=1,
             n_hidden_units=-1, T=4,
             stopping_criterion=stopping_criterion, 
             modelfile=modelfile)

import argparse

def main(train=False,test=False,simulate=False,folder=None,modelfile=None,penalty=0):
    num_timesteps = 100000
    if train:
        #with tf.Session() as sess:
            #sess.run(initialize_all_variables())
        env = tsp_env.TSP_env(simulate=simulate, data_folder=folder,penalty=penalty)
        graph_learn(env, num_timesteps=num_timesteps,
        q_func=Q_function_graph_model.Q_func, modelfile=modelfile)

    elif test:
        with tf.Session() as sess:    
            env = tsp_env.TSP_env(simulate=simulate, data_folder=folder, penalty=penalty)
            graph_test(session=sess, 
                     env=env, 
                     q_func=Q_function_graph_model.Q_func,
                     modelfile=modelfile)
    else:
        print('Please select to train or test')
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--train", help="true to train the model",
                        action="store_true")
    parser.add_argument("-t", "--test", help="true to test the model",
                        action="store_true")
    parser.add_argument("-s", "--simulate", help="true if run on simulated data, false for real data",
                        action="store_true")
    parser.add_argument("-f", "--folder", help="folder with data to test or train",
                         type=str, dest='folder', default= 'test_default' if test else 'train_default',
                          metavar='FOLDER')
    parser.add_argument("-p", "--length", help="length of substrings",
                         type=int, dest='penalty', default=0, metavar='STRING_length')
    parser.add_argument("--modelfile", help="file name to save models",
                        type=str, dest='modelfile', default='TSP', metavar='MODELFILE'))
    args = parser.parse_args()
    
    main(train=args.train,
        test=args.test,
        simulate=args.simulate,
        folder=args.folder,
        modelfile=args.modelfile,
        penalty=penalty)   