import random
import math


class Layer:

    def __init__(self, input_count, neuron_count):

        self.weights = []
        self.biases = []

        for i in range(neuron_count):

            neuron_weights = []

            for j in range(input_count):

                neuron_weights.append(
                    random.uniform(-1, 1)
                )

            self.weights.append(
                neuron_weights
            )

            self.biases.append(
                random.uniform(-1, 1)
            )


    def forward(self, inputs):

        if len(inputs) != len(self.weights[0]):

            raise ValueError(
                "Number of inputs does not match number of weights"
            )

        outputs = []

        for i in range(len(self.weights)):

            weighted_sum = 0

            for j in range(len(inputs)):

                weighted_sum += (
                    inputs[j]
                    * self.weights[i][j]
                )

            weighted_sum += self.biases[i]

            output = math.tanh(
                weighted_sum
            )

            outputs.append(output)

        return outputs


class Neural_Network:

    def __init__(self, architecture):

        self.architecture = architecture.copy()

        self.layers = []

        for i in range(
            len(architecture) - 1
        ):

            input_count = architecture[i]

            neuron_count = architecture[i + 1]

            self.layers.append(
                Layer(
                    input_count,
                    neuron_count
                )
            )


    def forward(self, inputs):

        output = inputs

        for layer in self.layers:

            output = layer.forward(
                output
            )

        return output


    def copy(self):

        new_brain = Neural_Network(
            self.architecture
        )

        for i in range(
            len(self.layers)
        ):

            for j in range(
                len(self.layers[i].weights)
            ):

                for k in range(
                    len(self.layers[i].weights[j])
                ):

                    new_brain.layers[i].weights[j][k] = (
                        self.layers[i].weights[j][k]
                    )

                new_brain.layers[i].biases[j] = (
                    self.layers[i].biases[j]
                )

        return new_brain


    def mutate(
        self,
        mutation_rate=0.10,
        mutation_strength=0.30
    ):

        for layer in self.layers:

            for i in range(
                len(layer.weights)
            ):

                for j in range(
                    len(layer.weights[i])
                ):

                    if random.random() < mutation_rate:

                        layer.weights[i][j] += random.gauss(
                            0,
                            mutation_strength
                        )


                if random.random() < mutation_rate:

                    layer.biases[i] += random.gauss(
                        0,
                        mutation_strength
                    )


    # --------------------------------
    # FIX: Layer stores "biases" (plural),
    # not "bias". The old code read/wrote
    # layer.bias, which doesn't exist and
    # would raise AttributeError -- and
    # even if it hadn't crashed, it meant
    # bias values were never actually
    # saved/restored correctly.
    # --------------------------------

    def get_data(self):

        data = []

        for layer in self.layers:

            data.append({
                "weights": layer.weights,
                "biases": layer.biases
            })

        return data


    def set_data(self, data):

        for layer, layer_data in zip(self.layers, data):

            # Copy the lists rather than aliasing
            # the JSON-loaded lists directly.

            layer.weights = [
                row[:] for row in layer_data["weights"]
            ]

            layer.biases = layer_data["biases"][:]