"""
Programmer: Soumitri Chattopadhyay
Date of Development: 11/07/2021
This code has been developed according to the procedures mentioned in the following research article:
"Laith A., Diabat A., Mirjalili S., Elaziz M.A., Gandomi A.H. The Arithmetic Optimization Algorithm.
Computer Methods in Applied Mechanics and Engineering, 376, 113609 (2021)"
"""
import math
import numpy as np
import time
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn import datasets

from _utilities import Solution, Data, initialize, sort_agents, display, compute_fitness, Conv_plot
from _transfer_functions import get_trans_function


def AOA(num_agents, max_iter, train_data, train_label, obj_function=compute_fitness, trans_func_shape='s', save_conv_graph=False):
    
    # Arithmetic Optimization Algorithm
    ############################### Parameters ####################################
    #                                                                             #
    #   num_agents: number of agents                                              #
    #   max_iter: maximum number of generations                                   #
    #   train_data: training samples of data                                      #
    #   train_label: class labels for the training samples                        #
    #   obj_function: the function to maximize while doing feature selection      #
    #   trans_function_shape: shape of the transfer function used                 #
    #   save_conv_graph: boolean value for saving convergence graph               #
    #                                                                             #
    ###############################################################################

    short_name = 'AMOA'
    agent_name = 'Agent'
    train_data, train_label = np.array(train_data), np.array(train_label)
    num_features = train_data.shape[1]
    trans_function = get_trans_function(trans_func_shape)

    # setting up the objectives
    weight_acc = None
    if (obj_function == compute_fitness):
        weight_acc = float(input('Weight for the classification accuracy [0-1]: '))
    obj = (obj_function, weight_acc)
    compute_accuracy = (compute_fitness, 1)  # compute_accuracy is just compute_fitness with accuracy weight as 1

    # initialize agents and Leader (the agent with the max fitness)
    agents = initialize(num_agents, num_features)
    fitness = np.zeros(num_agents)
    accuracy = np.zeros(num_agents)
    Leader_agent = np.zeros((num_features,))
    Leader_fitness = float("-inf")
    Leader_accuracy = float("-inf")

    # initialize convergence curves
    convergence_curve = {}
    convergence_curve['fitness'] = np.zeros(max_iter)
    convergence_curve['feature_count'] = np.zeros(max_iter)

    # format the data
    data = Data()
    val_size = float(input('Enter the percentage of data wanted for valdiation [0, 100]: ')) / 100
    data.train_X, data.val_X, data.train_Y, data.val_Y = train_test_split(train_data, train_label, stratify=train_label,
                                                                          test_size=val_size)

    # create a solution object
    solution = Solution()
    solution.num_agents = num_agents
    solution.max_iter = max_iter
    solution.num_features = num_features
    solution.obj_function = obj_function

    # initializing parameters
    lb = 0.1
    ub = 0.9
    eps = 1e-6
    alpha = 5
    mu = 0.5

    # rank initial agents
    agents, fitness = sort_agents(agents, obj, data)

    # start timer
    start_time = time.time()

    for iter_no in range(max_iter):
        print('\n================================================================================')
        print('                          Iteration - {}'.format(iter_no + 1))
        print('================================================================================\n')

        # Eq. (2)
        MoA = moa(lb, ub, max_iter, iter_no)

        # Eq. (4)
        MoP = mop(max_iter, iter_no, alpha)

        for i in range(num_agents):
            for j in range(num_features):

                r1 = np.random.random()

                # Exploration phase (M,D)
                if r1 > MoA:
                    # Eq. (3)
                    r2 = np.random.random()
                    if r2 >= 0.5:
                        agents[i,j] = Leader_agent[j] * (MoP + eps) * ((ub-lb) * mu + lb)
                    else:
                        agents[i,j] = Leader_agent[j] / (MoP + eps) * ((ub - lb) * mu + lb)

                # Exploitation phase (A,S)
                else:
                    # Eq. (5)
                    r3 = np.random.random()
                    if r3 >= 0.5:
                        agents[i,j] = Leader_agent[j] + MoP * ((ub - lb) * mu + lb)
                    else:
                        agents[i,j] = Leader_agent[j] - MoP * ((ub - lb) * mu + lb)

                # convert to binary using transfer function
                if np.random.random() < trans_function(agents[i][j]):
                    agents[i,j] = 1
                else:
                    agents[i,j] = 0

        # update final information
        agents, fitness = sort_agents(agents, obj, data)
        display(agents, fitness, agent_name)

        # update Leader (best agent)
        if fitness[0] > Leader_fitness:
            Leader_agent = agents[0].copy()
            Leader_fitness = fitness[0].copy()

        convergence_curve['fitness'][iter_no] = Leader_fitness
        convergence_curve['feature_count'][iter_no] = int(np.sum(Leader_agent))

    # compute final accuracy
    Leader_agent, Leader_accuracy = sort_agents(Leader_agent, compute_accuracy, data)
    agents, accuracy = sort_agents(agents, compute_accuracy, data)

    print('\n================================================================================')
    print('                                    Final Result                                  ')
    print('================================================================================\n')
    print('Leader ' + agent_name + ' Dimension : {}'.format(int(np.sum(Leader_agent))))
    print('Leader ' + agent_name + ' Fitness : {}'.format(Leader_fitness))
    print('Leader ' + agent_name + ' Classification Accuracy : {}'.format(Leader_accuracy))
    print('\n================================================================================\n')

    # stop timer
    end_time = time.time()
    exec_time = end_time - start_time

    # plot convergence curves
    fig, axes = Conv_plot(convergence_curve)
    if (save_conv_graph):
        plt.savefig('convergence_graph_' + short_name + '.jpg')
    plt.show()

    # update attributes of solution
    solution.best_agent = Leader_agent
    solution.best_fitness = Leader_fitness
    solution.best_accuracy = Leader_accuracy
    solution.convergence_curve = convergence_curve
    solution.final_agents = agents
    solution.final_fitness = fitness
    solution.final_accuracy = accuracy
    solution.execution_time = exec_time

    return solution

def moa(lb,ub,max_iter,t):
    return lb + (ub-lb) * t/max_iter

def mop(max_iter,t,alpha=5):
    return 1 - math.pow((t/max_iter), (1/alpha))


if __name__ == '__main__':
    data = datasets.load_digits()
    AOA(20, 100, data.data, data.target, save_conv_graph=False)