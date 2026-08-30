import pygame
import json
import os

from car import Car
from sensor import Sensor


WIDTH = 1000
HEIGHT = 800

TRACK_NAME = "three"

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


def create_sensors():

    return {

        "S0": Sensor(0, 150),

        "S1": Sensor(30, 150),

        "S2": Sensor(-30, 150),

        "S3": Sensor(60, 150),

        "S4": Sensor(-60, 150),

        "S5": Sensor(110, 150),

        "S6": Sensor(-110, 150)

    }


def create_car():

    return Car(
        100,
        600,
        0,
        90,
        True
    )


def reset_agent(agent):

    agent["car"] = create_car()

    agent["sensors"] = create_sensors()

    agent["previous_point"] = 0

    agent["current_point"] = 0

    agent["lap"] = 0

    agent["distance"] = 0

    agent["crashed"] = False


def run_simulation(
    population,
    screen,
    clock,
    font
):

    # --------------------------------
    # Load Track
    # --------------------------------

    track = load_track(
        TRACK_NAME
    )

    outer_points = track["outer"]

    inner_points = track["inner"]


    # --------------------------------
    # Track Distance
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
    # Reset Cars
    # --------------------------------

    for agent in population:

        reset_agent(
            agent
        )


    # --------------------------------
    # Car Images
    # --------------------------------

    colors = [

        (200, 50, 50),
        (50, 50, 200),
        (50, 200, 50),
        (200, 200, 50),
        (200, 50, 200),
        (50, 200, 200),
        (255, 120, 50),
        (150, 50, 255),
        (255, 100, 150),
        (100, 255, 100)

    ]


    car_images = []


    for color in colors:

        image = pygame.Surface(
            (20, 35),
            pygame.SRCALPHA
        )

        image.fill(
            color
        )

        car_images.append(
            image
        )


    # --------------------------------
    # Simulation
    # --------------------------------

    running = True


    while running:

        # --------------------------------
        # Events
        # --------------------------------

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                raise SystemExit


        # --------------------------------
        # Update Cars
        # --------------------------------

        for index, agent in enumerate(
            population
        ):

            if agent["crashed"]:

                continue


            car = agent["car"]

            sensors = agent["sensors"]


            # --------------------------------
            # Sensors
            # --------------------------------

            for sensor in sensors.values():

                sensor.update(

                    car.x_pos,

                    car.y_pos,

                    car.angle,

                    outer_points,

                    inner_points

                )


            sensor_values = [

                sensors["S0"].value,

                sensors["S1"].value,

                sensors["S2"].value,

                sensors["S3"].value,

                sensors["S4"].value,

                sensors["S5"].value,

                sensors["S6"].value

            ]


            # --------------------------------
            # Find Track Point
            # --------------------------------

            car_position = pygame.math.Vector2(

                car.x_pos,

                car.y_pos

            )


            current_point = agent[
                "current_point"
            ]


            closest_index = current_point

            closest_distance = float(
                "inf"
            )


            start_index = max(

                0,

                current_point - SEARCH_BACK

            )


            end_index = min(

                len(inner_points),

                current_point +
                SEARCH_FORWARD +
                1

            )


            for i in range(
                start_index,
                end_index
            ):

                track_point = pygame.math.Vector2(
                    inner_points[i]
                )


                distance = car_position.distance_to(
                    track_point
                )


                if distance < closest_distance:

                    closest_distance = distance

                    closest_index = i


            # --------------------------------
            # Lap Detection
            # --------------------------------

            previous_point = agent[
                "previous_point"
            ]


            near_end = (

                previous_point
                > len(inner_points) * 0.8

            )


            near_start = (

                closest_index
                < len(inner_points) * 0.2

            )


            if near_end and near_start:

                agent["lap"] += 1


            near_start_before = (

                previous_point
                < len(inner_points) * 0.2

            )


            near_end_now = (

                closest_index
                > len(inner_points) * 0.8

            )


            if near_start_before and near_end_now:

                agent["lap"] -= 1


            agent["current_point"] = (
                closest_index
            )

            agent["previous_point"] = (
                closest_index
            )


            # --------------------------------
            # Distance
            # --------------------------------

            agent["distance"] = (

                agent["lap"] *
                track_length

                +

                track_distances[
                    closest_index
                ]

            )


            # --------------------------------
            # Crash
            # --------------------------------

            crashed = False


            for value in sensor_values:

                if value < 0.1:

                    car.stop()

                    car.kill()

                    agent["crashed"] = True

                    crashed = True

                    break


            if crashed:

                continue


            # --------------------------------
            # Neural Network
            # --------------------------------

            output = agent[
                "brain"
            ].forward(
                sensor_values
            )


            throttle = output[0]

            steer = output[1]


            # --------------------------------
            # Car Update
            # --------------------------------

            car.update(
                throttle,
                steer
            )


        # --------------------------------
        # Check All Crashed
        # --------------------------------

        all_crashed = True


        for agent in population:

            if not agent["crashed"]:

                all_crashed = False

                break


        if all_crashed:

            break


        # --------------------------------
        # Draw Background
        # --------------------------------

        screen.fill(
            (30, 120, 50)
        )


        # --------------------------------
        # Draw Outer Track
        # --------------------------------

        if len(outer_points) >= 2:

            pygame.draw.lines(

                screen,

                (255, 255, 255),

                False,

                outer_points,

                6

            )


        # --------------------------------
        # Draw Inner Track
        # --------------------------------

        if len(inner_points) >= 2:

            pygame.draw.lines(

                screen,

                (255, 255, 255),

                False,

                inner_points,

                6

            )


        # --------------------------------
        # Draw Cars
        # --------------------------------

        for index, agent in enumerate(
            population
        ):

            if agent["crashed"]:

                continue


            car = agent["car"]


            rotated_car = pygame.transform.rotate(

                car_images[index],

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
        # Find Current Best
        # --------------------------------

        best = max(

            population,

            key=lambda agent:
            agent["distance"]

        )


        distance_text = font.render(

            f"Best Distance: {best['distance']:.1f}",

            True,

            (255, 255, 255)

        )


        lap_text = font.render(

            f"Lap: {best['lap']}",

            True,

            (255, 255, 255)

        )


        screen.blit(

            distance_text,

            (20, 20)

        )


        screen.blit(

            lap_text,

            (20, 50)

        )


        pygame.display.flip()

        clock.tick(60)


    # --------------------------------
    # Return Best Car
    # --------------------------------

    best_car = max(

        population,

        key=lambda agent:
        agent["distance"]

    )


    return best_car
