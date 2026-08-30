import os
import json

from neural_network import Neural_Network

from simulation import run_simulation


# --------------------------------
# Settings
# --------------------------------

POPULATION_SIZE = 10

ARCHITECTURE = [7, 8, 2]

MUTATION_RATE = 0.10

MUTATION_STRENGTH = 0.30

CHECKPOINT_FILE = (
    "training_checkpoint.json"
)


# --------------------------------
# Create random population
# --------------------------------

def create_random_population():

    population = []


    for i in range(
        POPULATION_SIZE
    ):

        brain = Neural_Network(
            ARCHITECTURE
        )

        population.append(
            brain
        )


    return population


# --------------------------------
# Create next population
# --------------------------------

def create_next_population(
    best_brain
):

    population = []


    # --------------------------------
    # Keep best brain unchanged
    # --------------------------------

    population.append(
        best_brain.copy()
    )


    # --------------------------------
    # Create mutated children
    # --------------------------------

    while len(population) < POPULATION_SIZE:

        brain = best_brain.copy()


        brain.mutate(

            mutation_rate=MUTATION_RATE,

            mutation_strength=MUTATION_STRENGTH
        )


        population.append(
            brain
        )


    return population


# --------------------------------
# Save checkpoint
#
# FIX: this now saves "architecture" at
# the top level, since that's what
# load_checkpoint() (and run.py) actually
# check for. Before, only "generation" and
# "best_brain" were saved, so
# load_checkpoint() could never validate
# the file and always fell back to a fresh
# random population -- that's why your
# cars looked random after every restart.
# --------------------------------

def save_checkpoint(
    generation,
    best_brain
):

    data = {

        "generation": generation,

        "architecture": ARCHITECTURE,

        "best_brain": best_brain.get_data()
    }


    with open(
        CHECKPOINT_FILE,
        "w"
    ) as file:

        json.dump(

            data,

            file,

            indent=4
        )


    print()
    print(
        "Checkpoint saved."
    )


# --------------------------------
# Load checkpoint
#
# FIX: checks the keys that are actually
# saved ("architecture", "best_brain")
# instead of "population", which never
# existed in the saved file.
# --------------------------------

def load_checkpoint():

    if not os.path.exists(CHECKPOINT_FILE):
        return None

    try:

        with open(CHECKPOINT_FILE, "r") as file:
            checkpoint = json.load(file)

        if "architecture" not in checkpoint:
            print("Old checkpoint format detected.")
            print("Starting training from a new population.")
            return None

        if "best_brain" not in checkpoint:
            print("Invalid checkpoint.")
            print("Starting training from a new population.")
            return None

        if checkpoint["architecture"] != ARCHITECTURE:
            print("Checkpoint architecture does not match.")
            print("Starting training from a new population.")
            return None

        print(
            "Checkpoint loaded. "
            f"Generation: {checkpoint.get('generation', 0)}"
        )

        return checkpoint

    except (json.JSONDecodeError, KeyError, TypeError):

        print("Checkpoint is corrupted or incompatible.")
        print("Starting training from a new population.")

        return None


# --------------------------------
# Main
# --------------------------------

def main():

    checkpoint = load_checkpoint()


    # --------------------------------
    # New training
    # --------------------------------

    if checkpoint is None:

        print(
            "No checkpoint found."
        )

        print(
            "Creating random population..."
        )


        generation = 0

        population = (
            create_random_population()
        )


    # --------------------------------
    # Resume training
    #
    # FIX: checkpoint is a dict (from
    # load_checkpoint), not a tuple, so we
    # read it by key instead of by index.
    # We also have to rebuild an actual
    # Neural_Network object from the saved
    # weights/biases via set_data() --
    # the old code tried to treat raw
    # checkpoint data as if it were already
    # a brain object.
    # --------------------------------

    else:

        last_generation = checkpoint[
            "generation"
        ]

        best_brain = Neural_Network(
            ARCHITECTURE
        )

        best_brain.set_data(
            checkpoint["best_brain"]
        )


        print(
            "Checkpoint found."
        )

        print(
            "Last completed generation:",
            last_generation
        )


        # The saved brain belongs to
        # the last completed generation.
        #
        # So the new population is
        # generation + 1.

        generation = (
            last_generation + 1
        )


        population = (
            create_next_population(
                best_brain
            )
        )


    # --------------------------------
    # Training loop
    # --------------------------------

    while True:

        print()
        print(
            "================================"
        )

        print(
            "STARTING GENERATION",
            generation
        )

        print(
            "================================"
        )


        result = run_simulation(

            population,

            show_simulation=True
        )


        # --------------------------------
        # User stopped simulation
        # --------------------------------

        if result is None:

            print()
            print(
                "Training stopped."
            )

            print(
                "The previous completed "
                "generation is saved."
            )

            break


        # --------------------------------
        # Get result
        # --------------------------------

        best_brain = result[
            0
        ]

        best_distance = result[
            1
        ]

        best_lap = result[
            2
        ]


        print()
        print(
            "Best distance:",
            best_distance
        )

        print(
            "Best lap:",
            best_lap
        )


        # --------------------------------
        # Save best brain
        # --------------------------------

        save_checkpoint(

            generation,

            best_brain
        )


        # --------------------------------
        # Create next population
        # --------------------------------

        population = (
            create_next_population(
                best_brain
            )
        )


        # --------------------------------
        # Next generation
        # --------------------------------

        generation += 1


# --------------------------------
# Start
# --------------------------------

if __name__ == "__main__":

    main()