import numpy as np
from typing import List
"""
Notes:
    - The brain is a multi-layer perceptron with a variable number of layers and nodes per layer.
    - the input is a set of 6 points that represent vision of the agent, first 3 points 
    are the depth perception of the agent at 3 different points, the other 3 points are whether the agent sees the goal at any of these points
"""
class Brain:
    """the main neural network class
        weights: The weights of the multi-layer perceptron that drives the agent.
        biases: The biases of the multi-layer perceptron that drives the agent.
    """
    def __init__(self, layers:list, weights=None, biases=None):
        """Receive a list of layers and initialize the weights and biases randomly
            Note that the last element in layers should be 3 since the output has 3 values
        """
        if weights is not None and biases is not None:
            self.weights = weights
            self.biases = biases
        else:
            self.weights = [] # type: List[np.ndarray] 
            self.biases = [] # type: List[np.ndarray]
            for i in range(len(layers)):
                if i == 0:
                    self.weights.append(np.random.randn(11, layers[i]))
                    self.biases.append(np.random.randn(layers[i]))
                else:
                    self.weights.append(np.random.randn(layers[i-1], layers[i]))
                    self.biases.append(np.random.randn(layers[i]))

    def get_softmax(self, output):
        """Return the softmax of the output of the network"""
        return np.exp(output)/np.sum(np.exp(output))
    
    def feedforward(self, inputs:list, activation="relu") -> np.ndarray:
        """Feed the inputs through the network and return the output

           Keyword arguments:
              inputs -- the inputs to the network
              activation -- the activation function to use (default "relu")
        """
        # normalize inputs
        curr = normalize(inputs)
        
        for i in range(len(self.weights)):
            curr = np.dot(curr, self.weights[i]) + self.biases[i]
            if activation == "relu":
                curr = np.maximum(0, curr)
        if np.sum(curr) > 500:
            curr /= np.sum(curr)
        curr = self.get_softmax(curr)
        curr = np.nan_to_num(curr)

        return curr 

    def mutate(self, mutate_probability_threshold:float, seed=None):
        """Mutate the weights and biases of the network
        
        Use a Guassian distribution with mean 0 and standard deviation 0.1 to mutate the weights and biases

        Keyword arguments:
        mutate_probability_threshold -- The probability of a weight or bias being mutated
        seed -- The seed to use for the random number generator, mainly for testing
        """

        # When testing, use a seed to make sure the same mutations are applied to all networks
        if seed is not None:
            rng = np.random.default_rng(seed)
        else:
            rng = np.random.default_rng()

        for weights in self.weights:
            mutations = rng.normal(scale=0.1, size=tuple(weights.shape))
            random_sample = rng.uniform(size=tuple(weights.shape))
            weights[random_sample <= mutate_probability_threshold] += mutations[random_sample <= mutate_probability_threshold]

        for biases in self.biases:
            mutations = rng.normal(scale=0.1, size=tuple(biases.shape))
            random_sample = rng.uniform(size=tuple(biases.shape))
            biases[random_sample <= mutate_probability_threshold] += mutations[random_sample <= mutate_probability_threshold]

        return self

    def crossover(self, other_brain):
        """Return a new network that is a crossover of this network and another network

        Keyword arguments:
        other_brain -- The other network to crossover with
        """

        assert len(self.weights) == len(other_brain.weights)
        assert len(self.biases) == len(other_brain.biases)

        new_weights = []
        new_biases = []

        for i in range(len(self.weights)):
            assert self.weights[i].shape == other_brain.weights[i].shape
            new_weights.append(np.where(np.random.uniform(size=self.weights[i].shape) < 0.5, self.weights[i], other_brain.weights[i]))

        for i in range(len(self.biases)):
            assert self.biases[i].shape == other_brain.biases[i].shape
            new_biases.append(np.where(np.random.uniform(size=self.biases[i].shape) < 0.5, self.biases[i], other_brain.biases[i]))

        res = Brain([], new_weights, new_biases)
        # print(res)

        return res

    def copy(self):
        """Return a copy of the network"""
        return Brain([], self.weights.copy(), self.biases.copy())

    def remove_node(self, layer:int, node:int):
        """Remove a node from the network"""

        assert layer < len(self.weights), f"Layer {layer} does not exist in the network"
        assert node < self.weights[layer].shape[1], f"Node {node} does not exist in layer {layer}"

        # remove the node-th column of the weights and biases in the specified layer
        weight_layer_with_node_to_remove = self.weights[layer]
        weight_layer_with_node_to_remove = np.delete(weight_layer_with_node_to_remove, node, 1)
        self.weights[layer] = weight_layer_with_node_to_remove

        bias_layer_with_node_to_remove = self.biases[layer]
        bias_layer_with_node_to_remove = np.delete(bias_layer_with_node_to_remove, node, 1)
        self.biases[layer] = bias_layer_with_node_to_remove

        # remove the node-th row of the weights and biases in the specified layer
        next_weight_layer = self.weights[layer + 1]
        next_weight_layer = np.delete(next_weight_layer, node, 0)
        self.weights[layer + 1] = next_weight_layer

        next_bias_layer = self.biases[layer + 1]
        next_bias_layer = np.delete(next_bias_layer, node, 0)
        self.biases[layer + 1] = next_bias_layer

    def add_node(self, layer:int, node:int):
        """Add a node to the network"""
        assert layer >= len(self.weights) or layer < 0, f"Layer number {layer} out of bounds [0, {len(self.weights) - 1}]"
        assert node >= len(self.weights[layer]) or node < 0, f"Node number {node} out of bounds [0, {len(self.weights[layer]) - 1}]"

        # add a column of weights and biases to the specified layer
        weight_layer_with_node_to_add = self.weights[layer]
        random_node_weights = np.random.default_rng.normal(0, 1, weight_layer_with_node_to_add.shape[0])
        weight_layer_with_node_to_add = np.insert(weight_layer_with_node_to_add, node, random_node_weights, 1)
        self.weights[layer] = weight_layer_with_node_to_add

        bias_layer_with_node_to_add = self.biases[layer]
        random_node_biases = np.random.default_rng.normal(0, 1, bias_layer_with_node_to_add.shape[0])
        bias_layer_with_node_to_add = np.insert(bias_layer_with_node_to_add, node, random_node_biases, 1)
        self.biases[layer] = bias_layer_with_node_to_add

        # add a row of weights and biases to the specified layer
        next_weight_layer = self.weights[layer + 1]
        next_weight_layer = np.insert(next_weight_layer, node, 0, 0)
        self.weights[layer + 1] = next_weight_layer

        next_bias_layer = self.biases[layer + 1]
        next_bias_layer = np.insert(next_bias_layer, node, 0, 0)
        self.biases[layer + 1] = next_bias_layer

def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0: 
       return v
    return v / norm
