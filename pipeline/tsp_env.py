import numpy as np
import networkx as nx
import random
import os
import pickle

class TSP_env:
    def __init__(self, simulate=False, data_folder=None, replay_penalty=0, penalty=0):
        #self.data = data #we need dish
        #self.adjacency_matrices = adjacencies
        self.env_name = 'TSP'
        self.replay_penalty = replay_penalty
        self.ind = 0
        self.simulate = simulate
        self.data_loader(data_folder)
        self.graph = self.getGraph()
        self.penalty = penalty
        self.number_nodes = len(self.graph)
        self.embedding_dimension = self.embedding.shape[1]
        self.state_shape = [self.number_nodes]
        self.num_actions = self.number_nodes
    
    # Loads the file paths and sets num graphs
    def data_loader(self, data_folder):
        if not self.simulate:
            self.data_paths = [os.path.join(data_folder, d) for d in os.listdir(data_folder)]
            self.num_graphs = len(self.data_paths)
        else:
            self.data_paths = None
            self.num_graphs = 200
    
    def getGraph(self):
        if self.simulate:
            # Simulate the graph
            nodes = 10
            G = nx.complete_graph(nodes,create_using=nx.DiGraph)
            for (u,v,w) in G.edges(data=True):
                w['weight'] = random.randint(2,10)
            path = np.arange(nodes); np.random.shuffle(path)
            for i in range(nodes-1):
                G[path[i]][path[i+1]]['weight'] = 1

            self.adjacency_matrix = nx.to_numpy_matrix(G)
            self.embedding = self.adjacency_matrix
            self.weight_matrix = -self.adjacency_matrix
            self.optimal_solution = -10
            
            return(G)
        else:
            # Load from filepath
            with open(self.data_paths[self.ind], 'rb') as filehandle:
                pkl_dict = pickle.load(filehandle) 

            self.embedding = pkl_dict['embedding']
            self.weight_matrix = pkl_dict['adjacency'] - self.penalty 
            self.adjacency_matrix = np.ones(self.weight_matrix.shape)
            np.fill_diagonal(self.adjacency_matrix, 0)
            self.optimal_solution = -len(pkl_dict['truth'])
            G = nx.from_numpy_matrix(self.adjacency_matrix, create_using=nx.DiGraph)

            return(G)

    def getAdj_mat(self):
        if self.simulate:
            return None
        #return self.adjacency_matrices(self.ind)
    
    def getEmbedding(self):
        return(self.getAdj_mat())

    def reset(self):
        self.acc_reward = 0
        self.left_node = None
        self.right_node = None
        # Load Graph
        self.graph = self.getGraph()
        self.nodes = list(self.graph.nodes)
        self.edges = list(self.graph.edges)
        # State for each node
        self.state = np.zeros(self.number_nodes)
        self.ind += 1
       
        #nope
        #if len(self.edges) == 0:
        #    self.reset()
        
        return self.state

    # Checks state vector to see if any nodes not connected
    def is_done(self, state):
        done = True
        if np.isin(0, self.state):
            done = False
        return done

    # Checks to see if all graphs have been trained on
    def all_graphs_trained(self):
        return self.ind >= self.num_graphs

    def step(self, action, side):
        if self.state[action] != 1:
            self.state[action] = 1
            if (side == 'right'):
                if self.right_node:
                    rew = self.weight_matrix[self.right_node, action]
                else:
                    rew = self.penalty
                    self.left_node = action
                self.right_node = action
            else:
                if self.left_node:
                    rew = self.weight_matrix[action, self.left_node]
                else:
                    rew = self.penalty
                    self.right_node = action
                self.left_node = action

        self.acc_reward += rew

        return self.state, rew, self.is_done(self.state)

    def accumulated_reward(self):
        return self.acc_reward

    def at_random_solution(self):
        temp_state = np.zeros(self.number_nodes) + 1
        temp_cost = 0
        path = np.arange(self.number_nodes); np.random.shuffle(path)
        for i in range(self.number_nodes-1):
            temp_cost += -self.weight_matrix[path[i],path[i+1]]

        return temp_cost, temp_state

    def optimal_solution(self):
        return self.optimal_solution, None

    # TODO?
    def close(self):
        return