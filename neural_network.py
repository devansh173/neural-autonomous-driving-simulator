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


    def mutate(self, mutation_rate=0.1, mutation_strength=0.1):

        for layer in self.layers:

            for i in range(len(layer.weights)):

                for j in range(len(layer.weights[i])):

                    if random.random() < mutation_rate:

                        layer.weights[i][j] += random.uniform(
                            -mutation_strength,
                            mutation_strength
                        )


                if random.random() < mutation_rate:

                    layer.biases[i] += random.uniform(
                        -mutation_strength,
                        mutation_strength
                    )



