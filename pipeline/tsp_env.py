import numpy as np
import networkx as nx

class TSP_env:
    def __init__(self, p = 0.15, replay_penalty=0, data, adjacencies):
        self.data = data #we need dish
        self.adjacency_matrices = adjacencies
        self.p = p
        self.env_name = 'TSP'
        self.replay_penalty = replay_penalty
        self.ind = 0
        
        self.graph = self.getGraph()
        self.num_nodes = self.graph.shape[0]
        self.state_shape = [self.num_nodes]
        self.num_actions = self.num_nodes
        self.adjacencies = self.getAdj_mat()

    def getGraph(self):
        return self.data(self.ind)
    
    def getAdj_mat(self)
        return self.adjacency_matrices(self.ind)
    
    def reset(self):
        self.acc_reward = 0
        self.graph = self.getGraph()
        #self.graph = nx.erdos_renyi_graph(n = self.number_nodes, p = self.p)
        #self.nodes = list(self.graph.nodes)
        #self.edges = list(self.graph.edges)
        self.state = np.zeros(self.num_nodes())
        self.adjacency_matrix = self.getAdj_mat()
        self.weight_matrix = self.adjacency_matrix
        self.ind += 1
       
        #nope
        #if len(self.edges) == 0:
        #    self.reset()
        #return self.state

    def is_done(self, state):
        done = True
        if np.isin(0, self.state):
            done = False
        return done

    def step(self, action):
        if self.state[action] != 1:
            self.state[action] = 1
            rew = -1
        else:
            rew = -self.replay_penalty

        self.acc_reward += rew

        return self.state, rew, self.is_done(self.state)

    def accumulated_reward(self):
        return self.acc_reward

    def at_random_solution(self):
        temp_state = np.zeros(self.number_nodes)
        while not self.is_done(temp_state):
            temp_state[np.random.randint(self.number_nodes)] = 1

        return -np.sum(temp_state), temp_state

    def optimal_solution(self):
        # TODO
        return 0, None