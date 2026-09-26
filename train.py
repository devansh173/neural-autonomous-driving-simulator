import os
import json
import random

from neural_network import Neural_Network

from simulation import run_simulation


# --------------------------------
# Settings
# --------------------------------

POPULATION_SIZE = 10

ARCHITECTURE = [7, 8, 2]

ELITE_COUNT = 3

MUTATION_RATE = 0.10

BASE_MUTATION_STRENGTH = 0.30

MAX_MUTATION_STRENGTH = 1.20

MUTATION_BOOST_FACTOR = 1.50

STAGNATION_LIMIT = 4

# Minimum extra distance to count as a
# "real" improvement (avoids treating
# tiny floating point noise as progress).

IMPROVEMENT_THRESHOLD = 1.0

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
#
# Keeps the top elites unchanged, then
# fills the rest of the population by
# crossbreeding two random elites and
# mutating the result. This gives more
# genetic diversity than mutating a
# single best brain over and over.
# --------------------------------

def create_next_population(
    elites,
    mutation_strength
):

    population = []


    # --------------------------------
    # Keep elites unchanged
    # --------------------------------

    for elite in elites:

        population.append(
            elite.copy()
        )


    # --------------------------------
    # Breed + mutate the rest
    # --------------------------------

    while len(population) < POPULATION_SIZE:

        if len(elites) >= 2:

            parent_a = random.choice(elites)

            parent_b = random.choice(elites)

            child = parent_a.crossover(
                parent_b
            )

        else:

            child = elites[0].copy()


        child.mutate(
            mutation_rate=MUTATION_RATE,
            mutation_strength=mutation_strength
        )


        population.append(
            child
        )


    return population


# --------------------------------
# Save checkpoint
# --------------------------------

def save_checkpoint(
    generation,
    elites,
    best_distance,
    stagnation,
    mutation_strength
):

    data = {

        "generation": generation,

        "architecture": ARCHITECTURE,

        # "best_brain" is kept for
        # backward compatibility with
        # run_trained.py, which only
        # needs the single best brain.

        "best_brain": elites[0].get_data(),

        "elites": [
            elite.get_data()
            for elite in elites
        ],

        "best_distance": best_distance,

        "stagnation": stagnation,

        "mutation_strength": mutation_strength
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

        best_distance_record = 0

        stagnation = 0

        mutation_strength = BASE_MUTATION_STRENGTH


    # --------------------------------
    # Resume training
    # --------------------------------

    else:

        last_generation = checkpoint[
            "generation"
        ]


        # Older checkpoints (before this
        # update) only saved a single
        # "best_brain" and no "elites"
        # list. Fall back gracefully.

        elite_data_list = checkpoint.get(
            "elites",
            [checkpoint["best_brain"]]
        )

        elites = []

        for elite_data in elite_data_list:

            brain = Neural_Network(
                ARCHITECTURE
            )

            brain.set_data(
                elite_data
            )

            elites.append(
                brain
            )


        best_distance_record = checkpoint.get(
            "best_distance",
            0
        )

        stagnation = checkpoint.get(
            "stagnation",
            0
        )

        mutation_strength = checkpoint.get(
            "mutation_strength",
            BASE_MUTATION_STRENGTH
        )


        print(
            "Checkpoint found."
        )

        print(
            "Last completed generation:",
            last_generation
        )


        generation = (
            last_generation + 1
        )


        population = (
            create_next_population(
                elites,
                mutation_strength
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
            "Mutation strength:",
            round(mutation_strength, 3)
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

        population_result = result[0]

        max_distances = result[1]

        laps = result[2]


        # --------------------------------
        # Rank the whole population by
        # distance, best first.
        # --------------------------------

        ranked_indices = sorted(

            range(len(population_result)),

            key=lambda i: max_distances[i],

            reverse=True
        )


        elites = [

            population_result[i]

            for i in ranked_indices[:ELITE_COUNT]
        ]


        best_index = ranked_indices[0]

        best_distance = max_distances[
            best_index
        ]

        best_lap = laps[
            best_index
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
        # Adaptive mutation:
        #
        # If this generation set a real
        # new record, reset mutation
        # strength back to base and clear
        # the stagnation counter.
        #
        # Otherwise, count it as a
        # stagnant generation. After
        # STAGNATION_LIMIT stagnant
        # generations in a row, boost
        # mutation strength to help the
        # population escape the local
        # optimum it's stuck at.
        # --------------------------------

        if best_distance > (
            best_distance_record + IMPROVEMENT_THRESHOLD
        ):

            best_distance_record = best_distance

            stagnation = 0

            mutation_strength = BASE_MUTATION_STRENGTH

            print(
                "New record! Mutation strength "
                "reset to",
                round(mutation_strength, 3)
            )

        else:

            stagnation += 1

            print(
                "No improvement for",
                stagnation,
                "generation(s)."
            )

            if stagnation >= STAGNATION_LIMIT:

                mutation_strength = min(

                    mutation_strength * MUTATION_BOOST_FACTOR,

                    MAX_MUTATION_STRENGTH
                )

                stagnation = 0

                print(
                    "Stuck - boosting mutation "
                    "strength to",
                    round(mutation_strength, 3)
                )


        # --------------------------------
        # Save best brain / elites
        # --------------------------------

        save_checkpoint(

            generation,

            elites,

            best_distance_record,

            stagnation,

            mutation_strength
        )


        # --------------------------------
        # Create next population
        # --------------------------------

        population = (
            create_next_population(
                elites,
                mutation_strength
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