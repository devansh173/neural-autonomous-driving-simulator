import pygame
import json
import os

from car import Car
from sensor import Sensor


WIDTH = 1000
HEIGHT = 800

TRACK_NAME = "log"

TRACK_FOLDER = "tracks"

SEARCH_BACK = 20
SEARCH_FORWARD = 20


def load_track(name):

    filename = os.path.join(
        TRACK_FOLDER,
        name + ".json"
    )

    with open(
        filename,
        "r"
    ) as file:

        return json.load(file)


def run_simulation(
    population,
    show_simulation=True
):

    pygame.init()


    # --------------------------------
    # Load track
    # --------------------------------

    track = load_track(
        TRACK_NAME
    )

    outer_points = track["outer"]

    inner_points = track["inner"]


    # --------------------------------
    # Track distance
    # --------------------------------

    track_distances = [0]


    for i in range(
        1,
        len(inner_points)
    ):

        point_a = pygame.math.Vector2(
            inner_points[i - 1]
        )

        point_b = pygame.math.Vector2(
            inner_points[i]
        )

        distance = point_a.distance_to(
            point_b
        )

        track_distances.append(
            track_distances[-1] + distance
        )


    track_length = track_distances[-1]


    # --------------------------------
    # Pygame
    # --------------------------------

    screen = None
    clock = None
    font = None


    if show_simulation:

        screen = pygame.display.set_mode(
            (WIDTH, HEIGHT)
        )

        pygame.display.set_caption(
            TRACK_NAME + " - Training"
        )

        clock = pygame.time.Clock()

        font = pygame.font.Font(
            None,
            30
        )

        button_font = pygame.font.Font(
            None,
            24
        )


    # --------------------------------
    # Stop & Save button (top right)
    #
    # Clicking this ends the current
    # generation early -- as if every
    # car had crashed -- so whatever
    # progress exists right now gets
    # ranked and saved normally. This
    # is different from closing the
    # window (the X button), which
    # still discards the in-progress
    # generation.
    # --------------------------------

    stop_button_rect = pygame.Rect(
        WIDTH - 150,
        10,
        140,
        40
    )


    # --------------------------------
    # Create cars
    # --------------------------------

    cars = []


    for i in range(
        len(population)
    ):

        car = Car(
            100,
            600,
            0,
            90,
            True
        )

        cars.append(
            car
        )


    # --------------------------------
    # Create sensors
    # --------------------------------

    sensors = []


    for i in range(
        len(population)
    ):

        car_sensors = {

            "S0": Sensor(0, 150),

            "S1": Sensor(30, 150),

            "S2": Sensor(-30, 150),

            "S3": Sensor(60, 150),

            "S4": Sensor(-60, 150),

            "S5": Sensor(110, 150),

            "S6": Sensor(-110, 150)
        }

        sensors.append(
            car_sensors
        )


    # --------------------------------
    # Progress
    # --------------------------------

    current_points = [
        0
        for i in population
    ]

    previous_points = [
        0
        for i in population
    ]

    laps = [
        0
        for i in population
    ]

    max_distances = [
        0
        for i in population
    ]


    # --------------------------------
    # Prevent repeated lap detection
    # --------------------------------

    forward_lap_lock = [
        False
        for i in population
    ]

    reverse_lap_lock = [
        False
        for i in population
    ]


    # --------------------------------
    # Car image
    # --------------------------------

    car_image = pygame.Surface(
        (20, 35),
        pygame.SRCALPHA
    )

    car_image.fill(
        (200, 50, 50)
    )


    # --------------------------------
    # Simulation
    # --------------------------------

    running = True

    user_stopped = False


    while running:

        # --------------------------------
        # Events
        # --------------------------------

        if show_simulation:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:

                    running = False

                    user_stopped = True


                if event.type == pygame.MOUSEBUTTONDOWN:

                    if stop_button_rect.collidepoint(
                        event.pos
                    ):

                        print()
                        print(
                            "Stop & Save pressed - "
                            "ending generation early "
                            "and saving progress."
                        )

                        running = False

                        # NOTE: user_stopped stays False
                        # here on purpose, so this is
                        # treated as a completed
                        # generation below (ranked and
                        # saved), not an abort.


        # --------------------------------
        # Update every car
        # --------------------------------

        for car_index in range(
            len(cars)
        ):

            car = cars[
                car_index
            ]


            if not car.is_alive:

                continue


            # --------------------------------
            # Update sensors
            # --------------------------------

            for sensor in sensors[
                car_index
            ].values():

                sensor.update(

                    car.x_pos,

                    car.y_pos,

                    car.angle,

                    outer_points,

                    inner_points
                )


            # --------------------------------
            # Sensor values
            # --------------------------------

            sensor_values = [

                sensors[car_index]["S0"].value,

                sensors[car_index]["S1"].value,

                sensors[car_index]["S2"].value,

                sensors[car_index]["S3"].value,

                sensors[car_index]["S4"].value,

                sensors[car_index]["S5"].value,

                sensors[car_index]["S6"].value
            ]


            # --------------------------------
            # Find closest track point
            # --------------------------------

            car_position = pygame.math.Vector2(

                car.x_pos,

                car.y_pos
            )


            closest_index = current_points[
                car_index
            ]

            closest_distance = float(
                "inf"
            )


            # Search around current position
            #
            # This also wraps around the track.

            for offset in range(
                -SEARCH_BACK,
                SEARCH_FORWARD + 1
            ):

                index = (
                    current_points[car_index]
                    + offset
                ) % len(inner_points)


                track_point = pygame.math.Vector2(
                    inner_points[index]
                )


                distance = car_position.distance_to(
                    track_point
                )


                if distance < closest_distance:

                    closest_distance = distance

                    closest_index = index


            previous = previous_points[
                car_index
            ]


            # --------------------------------
            # Forward lap detection
            # --------------------------------

            near_end = (

                previous
                > len(inner_points) * 0.8
            )


            near_start = (

                closest_index
                < len(inner_points) * 0.2
            )


            if near_end and near_start:

                if not forward_lap_lock[
                    car_index
                ]:

                    laps[car_index] += 1

                    forward_lap_lock[
                        car_index
                    ] = True

                    reverse_lap_lock[
                        car_index
                    ] = False

                    print(
                        f"Car {car_index} "
                        f"forward lap: "
                        f"{laps[car_index]}"
                    )


            # --------------------------------
            # Release forward lock
            # --------------------------------

            if closest_index > (
                len(inner_points) * 0.3
            ):

                forward_lap_lock[
                    car_index
                ] = False


            # --------------------------------
            # Reverse lap detection
            # --------------------------------

            near_start_before = (

                previous
                < len(inner_points) * 0.2
            )


            near_end_now = (

                closest_index
                > len(inner_points) * 0.8
            )


            if (
                near_start_before
                and near_end_now
            ):

                if not reverse_lap_lock[
                    car_index
                ]:

                    laps[car_index] -= 1

                    reverse_lap_lock[
                        car_index
                    ] = True

                    forward_lap_lock[
                        car_index
                    ] = False

                    print(
                        f"Car {car_index} "
                        f"reverse lap: "
                        f"{laps[car_index]}"
                    )


            # --------------------------------
            # Release reverse lock
            # --------------------------------

            if closest_index < (
                len(inner_points) * 0.7
            ):

                reverse_lap_lock[
                    car_index
                ] = False


            # --------------------------------
            # Save progress
            # --------------------------------

            current_points[
                car_index
            ] = closest_index


            previous_points[
                car_index
            ] = closest_index


            # --------------------------------
            # Calculate current distance
            # --------------------------------

            current_distance = (

                laps[car_index]
                * track_length

                + track_distances[
                    closest_index
                ]
            )


            # --------------------------------
            # IMPORTANT:
            #
            # Fitness NEVER decreases
            # --------------------------------

            if current_distance > max_distances[
                car_index
            ]:

                max_distances[
                    car_index
                ] = current_distance


            # --------------------------------
            # Crash detection
            # --------------------------------

            crashed = False


            for value in sensor_values:

                if value < 0.1:

                    car.stop()

                    car.kill()

                    crashed = True

                    break


            # --------------------------------
            # Neural network
            # --------------------------------

            if not crashed:

                output = population[
                    car_index
                ].forward(
                    sensor_values
                )


                throttle = output[0]

                steer = output[1]


                car.update(
                    throttle,
                    steer
                )


        # --------------------------------
        # Count alive cars
        # --------------------------------

        alive_cars = 0


        for car in cars:

            if car.is_alive:

                alive_cars += 1


        # --------------------------------
        # Stop when everyone crashes
        # --------------------------------

        if alive_cars == 0:

            running = False


        # --------------------------------
        # Draw
        # --------------------------------

        if show_simulation:

            screen.fill(
                (30, 120, 50)
            )


            # Outer

            if len(outer_points) >= 2:

                pygame.draw.lines(

                    screen,

                    (255, 255, 255),

                    False,

                    outer_points,

                    6
                )


            # Inner

            if len(inner_points) >= 2:

                pygame.draw.lines(

                    screen,

                    (255, 255, 255),

                    False,

                    inner_points,

                    6
                )


            # Cars

            for car_index in range(
                len(cars)
            ):

                car = cars[
                    car_index
                ]


                if not car.is_alive:

                    continue


                # Sensors

                for sensor in sensors[
                    car_index
                ].values():

                    sensor.draw(

                        screen,

                        car.x_pos,

                        car.y_pos
                    )


                # Car

                rotated_car = pygame.transform.rotate(

                    car_image,

                    car.angle - 90
                )


                car_rect = rotated_car.get_rect(

                    center=(

                        car.x_pos,

                        car.y_pos
                    )
                )


                screen.blit(

                    rotated_car,

                    car_rect
                )


            # --------------------------------
            # Best car
            # --------------------------------

            best_index = max_distances.index(
                max(max_distances)
            )


            best_distance = max_distances[
                best_index
            ]


            best_lap = laps[
                best_index
            ]


            # --------------------------------
            # Text
            # --------------------------------

            best_text = font.render(

                f"Best Distance: "
                f"{best_distance:.1f}",

                True,

                (255, 255, 255)
            )


            alive_text = font.render(

                f"Cars Alive: "
                f"{alive_cars}",

                True,

                (255, 255, 255)
            )


            lap_text = font.render(

                f"Best Lap: "
                f"{best_lap}",

                True,

                (255, 255, 255)
            )


            screen.blit(
                best_text,
                (20, 20)
            )

            screen.blit(
                alive_text,
                (20, 50)
            )

            screen.blit(
                lap_text,
                (20, 80)
            )


            # --------------------------------
            # Stop & Save button
            # --------------------------------

            pygame.draw.rect(
                screen,
                (180, 40, 40),
                stop_button_rect,
                border_radius=6
            )

            stop_text = button_font.render(
                "Stop & Save",
                True,
                (255, 255, 255)
            )

            stop_text_rect = stop_text.get_rect(
                center=stop_button_rect.center
            )

            screen.blit(
                stop_text,
                stop_text_rect
            )


            pygame.display.flip()

            clock.tick(60)


    # --------------------------------
    # User closed window
    # --------------------------------

    if user_stopped:

        pygame.quit()

        return None


    # --------------------------------
    # Find best car (just for the printout)
    # --------------------------------

    best_index = max_distances.index(
        max(max_distances)
    )


    best_distance = max_distances[
        best_index
    ]


    best_lap = laps[
        best_index
    ]


    print()
    print(
        "================================"
    )

    print(
        "GENERATION COMPLETE"
    )

    print(
        "================================"
    )

    print(
        "Best car:",
        best_index
    )

    print(
        "Best distance:",
        best_distance
    )

    print(
        "Best lap:",
        best_lap
    )

    print(
        "================================"
    )


    # --------------------------------
    # Do NOT pygame.quit() here
    #
    # train.py needs to run another
    # generation.
    # --------------------------------

    # --------------------------------
    # CHANGE: return the WHOLE population
    # plus everyone's distance/laps, not
    # just the single best brain. train.py
    # now picks multiple elites and does
    # crossover between them, so it needs
    # to rank the full population itself.
    # --------------------------------

    return (
        population,
        max_distances,
        laps
    )