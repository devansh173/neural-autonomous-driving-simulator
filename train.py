import pygame
import copy
import json
import os

from neural_network import Neural_Network
from simulation import run_simulation


# --------------------------------
# Settings
# --------------------------------

POPULATION_SIZE = 10

ARCHITECTURE = [7, 8, 2]

CHECKPOINT_FILE = "training_checkpoint.json"

BEST_BRAIN_FILE = "best_brain.json"


MUTATION_RATE = 0.3

MUTATION_STRENGTH = 0.3


# --------------------------------
# Create Empty Agent
# --------------------------------

def create_agent(brain):

    return {

        "brain": brain,

        "car": None,

        "sensors": None,

        "previous_point": 0,

        "current_point": 0,

        "lap": 0,

        "distance": 0,

        "crashed": False

    }


# --------------------------------
# Create Initial Population
# --------------------------------

def create_population():

    population = []


    for i in range(
        POPULATION_SIZE
    ):

        brain = Neural_Network(
            ARCHITECTURE
        )


        population.append(
            create_agent(
                brain
            )
        )


    return population


# --------------------------------
# Create Next Generation
# --------------------------------

def create_next_generation(
    best_brain
):

    population = []


    # --------------------------------
    # Elite
    # --------------------------------

    elite_brain = copy.deepcopy(
        best_brain
    )


    population.append(
        create_agent(
            elite_brain
        )
    )


    # --------------------------------
    # Mutated Brains
    # --------------------------------

    for i in range(
        POPULATION_SIZE - 1
    ):

        brain = copy.deepcopy(
            best_brain
        )


        brain.mutate(

            mutation_rate=MUTATION_RATE,

            mutation_strength=MUTATION_STRENGTH

        )


        population.append(
            create_agent(
                brain
            )
        )


    return population


# --------------------------------
# Save Checkpoint
# --------------------------------

def save_checkpoint(
    population,
    generation,
    best_brain,
    best_distance
):

    data = {

        "generation": generation,

        "best_distance": best_distance,

        "best_brain": best_brain.get_data(),

        "population": []

    }


    for agent in population:

        data["population"].append(

            agent["brain"].get_data()

        )


    with open(
        CHECKPOINT_FILE,
        "w"
    ) as file:

        json.dump(

            data,

            file,

            indent=4

        )


# --------------------------------
# Load Checkpoint
# --------------------------------

def load_checkpoint():

    if not os.path.exists(
        CHECKPOINT_FILE
    ):

        return None


    with open(
        CHECKPOINT_FILE,
        "r"
    ) as file:

        data = json.load(
            file
        )


    population = []


    for brain_data in data["population"]:

        brain = Neural_Network(
            ARCHITECTURE
        )


        brain.set_data(
            brain_data
        )


        population.append(

            create_agent(
                brain
            )

        )


    best_brain = Neural_Network(
        ARCHITECTURE
    )


    best_brain.set_data(
        data["best_brain"]
    )


    generation = data["generation"]

    best_distance = data[
        "best_distance"
    ]


    return (
        population,
        generation,
        best_brain,
        best_distance
    )


# --------------------------------
# Pygame
# --------------------------------

pygame.init()


screen = pygame.display.set_mode(
    (1000, 800)
)


pygame.display.set_caption(
    "Neural Network Training"
)


clock = pygame.time.Clock()


font = pygame.font.Font(
    None,
    30
)


# --------------------------------
# Load / Create Training
# --------------------------------

checkpoint = load_checkpoint()


if checkpoint is None:

    print(
        "No checkpoint found."
    )


    population = create_population()

    generation = 1

    best_ever_brain = copy.deepcopy(
        population[0]["brain"]
    )

    best_ever_distance = float(
        "-inf"
    )


else:

    (
        population,
        generation,
        best_ever_brain,
        best_ever_distance
    ) = checkpoint


    print(
        "Checkpoint loaded."
    )


    print(
        "Resuming generation:",
        generation
    )


    print(
        "Best distance so far:",
        best_ever_distance
    )


# --------------------------------
# Training Loop
# --------------------------------

try:

    while True:

        print()
        print(
            "================================"
        )

        print(
            "Generation:",
            generation
        )

        print(
            "================================"
        )


        # --------------------------------
        # Run One Generation
        # --------------------------------

        best_car = run_simulation(

            population,

            screen,

            clock,

            font

        )


        current_best_distance = (
            best_car["distance"]
        )


        print()

        print(
            "Generation best:",
            current_best_distance
        )


        print(
            "Generation lap:",
            best_car["lap"]
        )


        # --------------------------------
        # Check Best Ever
        # --------------------------------

        if current_best_distance > best_ever_distance:

            best_ever_distance = (
                current_best_distance
            )


            best_ever_brain = copy.deepcopy(
                best_car["brain"]
            )


            print(
                "NEW BEST EVER!"
            )


            print(
                "Best distance:",
                best_ever_distance
            )


            # Save best brain immediately

            best_ever_brain.save(
                BEST_BRAIN_FILE
            )


        else:

            print(
                "Best ever:",
                best_ever_distance
            )


        # --------------------------------
        # Create Next Generation
        # --------------------------------

        population = create_next_generation(

            best_car["brain"]

        )


        generation += 1


        # --------------------------------
        # Save Checkpoint
        # --------------------------------

        save_checkpoint(

            population,

            generation,

            best_ever_brain,

            best_ever_distance

        )


        print(
            "Checkpoint saved."
        )


except KeyboardInterrupt:

    print()
    print(
        "================================"
    )

    print(
        "TRAINING STOPPED"
    )

    print(
        "================================"
    )

    print(
        "Generation:",
        generation
    )

    print(
        "Best distance:",
        best_ever_distance
    )


finally:

    pygame.quit()
