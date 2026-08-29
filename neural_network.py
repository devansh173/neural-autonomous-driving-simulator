import random
import math


class Layer:
    def __init__(self, input_count, neuron_count):
        self.weights = []
        self.bias = []

        for i in range(neuron_count):
            neuron_weights = []

            for j in range(input_count):
                neuron_weights.append(random.uniform(-1, 1))

            self.weights.append(neuron_weights)
            self.bias.append(random.uniform(-1, 1))

    def forward(self, inputs):
        if len(inputs) != len(self.weights[0]):
            raise ValueError("Number of inputs does not match number of weights")

        outputs = []

        for i in range(len(self.weights)):
            weighted_sum = 0

            for j in range(len(inputs)):
                weighted_sum += inputs[j] * self.weights[i][j]

            weighted_sum += self.bias[i]

            output = math.tanh(weighted_sum)

            outputs.append(output)

        return outputs


class Neural_Network:
    def __init__(self, architecture):
        self.layers = []

        for i in range(len(architecture) - 1):
            self.layers.append(
                Layer(architecture[i], architecture[i + 1])
            )

    def forward(self, inputs):
        for current_layer in self.layers:
            inputs = current_layer.forward(inputs)

        return inputs


inputs = [0.2, 0.5, 0.8, 0.3, 0.9, 0.4, 0.7]

brain = Neural_Network([7, 8, 2])

outputs = brain.forward(inputs)

print(outputs)
