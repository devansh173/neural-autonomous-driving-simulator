import random
import math
import json
import copy


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
                    inputs[j] *
                    self.weights[i][j]
                )

            weighted_sum += self.biases[i]

            output = math.tanh(
                weighted_sum
            )

            outputs.append(output)

        return outputs


class Neural_Network:

    def __init__(self, architecture):

        self.layers = []

        for i in range(
            len(architecture) - 1
        ):

            layer = Layer(
                architecture[i],
                architecture[i + 1]
            )

            self.layers.append(
                layer
            )


    def forward(self, inputs):

        output = inputs

        for layer in self.layers:

            output = layer.forward(
                output
            )

        return output


    def mutate(
        self,
        mutation_rate=0.1,
        mutation_strength=0.1
    ):

        for layer in self.layers:

            for i in range(
                len(layer.weights)
            ):

                for j in range(
                    len(layer.weights[i])
                ):

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


    def copy(self):

        return copy.deepcopy(
            self
        )


    def get_data(self):

        data = {
            "layers": []
        }

        for layer in self.layers:

            data["layers"].append({

                "weights": layer.weights,

                "biases": layer.biases

            })

        return data


    def set_data(self, data):

        for i, layer_data in enumerate(
            data["layers"]
        ):

            self.layers[i].weights = (
                layer_data["weights"]
            )

            self.layers[i].biases = (
                layer_data["biases"]
            )


    def save(self, filename):

        data = self.get_data()

        with open(
            filename,
            "w"
        ) as file:

            json.dump(
                data,
                file,
                indent=4
            )


    def load(self, filename):

        with open(
            filename,
            "r"
        ) as file:

            data = json.load(
                file
            )

        self.set_data(
            data
        )
