import numpy as np
import networkx as nx
import random

class TSP_env:
    def __init__(self, simulate=False, replay_penalty=0):
        #self.data = data #we need dish
        #self.adjacency_matrices = adjacencies
        self.env_name = 'TSP'
        self.replay_penalty = replay_penalty
        self.ind = 0
        self.simulate = simulate
        self.num_graphs = 200
        self.graph = self.getGraph()
        #self.adjacency_matrices = adjacencies
        self.number_nodes = len(self.graph)
        self.embedding_dimension = self.getEmbedding().shape[1]
        self.state_shape = [self.number_nodes]
        self.num_actions = self.number_nodes
        #self.adjacencies = self.getAdj_mat()

    def getGraph(self):
        if self.simulate:
            nodes = 10
            G = nx.complete_graph(nodes,create_using=nx.DiGraph)
            for (u,v,w) in G.edges(data=True):
                w['weight'] = random.randint(2,10)
            path = np.arange(nodes); np.random.shuffle(path)
            for i in range(nodes-1):
                G[path[i]][path[i+1]]['weight'] = 1
            return(G)
        else:
            return
        #return self.data(self.ind)
    
    def getAdj_mat(self):
        return(nx.to_numpy_matrix(self.graph))
        #return self.adjacency_matrices(self.ind)
    
    def getEmbedding(self):
        return(self.getAdj_mat())

    def reset(self):
        self.acc_reward = 0
        self.prior_node = None
        # Load Graph
        self.graph = self.getGraph()
        self.nodes = list(self.graph.nodes)
        self.edges = list(self.graph.edges)
        # State for each node
        self.state = np.zeros(self.number_nodes)
        self.embedding = self.getEmbedding()
        self.adjacency_matrix = self.getAdj_mat()
        self.weight_matrix = self.adjacency_matrix
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

    def step(self, action):
        if self.state[action] != 1:
            self.state[action] = 1
            if self.prior_node:
                rew = -self.weight_matrix[self.prior_node, action]
            else:
                rew = 0
            self.prior_node = action
        else:
            rew = -self.replay_penalty


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
        # TODO
        return -10, None

    # TODO?
    def close(self):
        return