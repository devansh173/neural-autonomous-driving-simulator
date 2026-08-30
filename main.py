import pygame
import json
import os
from neural_network import Neural_Network

from car import Car
from sensor import Sensor


pygame.init()

WIDTH = 1000
HEIGHT = 800

TRACK_NAME = "three"

TRACK_FOLDER = "tracks"

POPULATION_SIZE = 10

def load_track(name):

    filename = os.path.join(
        TRACK_FOLDER,
        name + ".json"
    )

    with open(filename, "r") as file:
        return json.load(file)


track = load_track(TRACK_NAME)

outer_points = track["outer"]
inner_points = track["inner"]

track_distances = [0]


for i in range(1, len(inner_points)):

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


screen = pygame.display.set_mode(
    (WIDTH, HEIGHT)
)

pygame.display.set_caption(
    TRACK_NAME
)

clock = pygame.time.Clock()

font = pygame.font.Font(
    None,
    30
)


car_image = pygame.Surface(
    (30, 50),
    pygame.SRCALPHA
)

car_image.fill(
    (200, 50, 50)
)



population = []


for i in range(POPULATION_SIZE):

    car = Car(
        100,
        600,
        0,
        90,
        True
    )

    brain = Neural_Network(
        [7, 8, 2]
    )

    sensors = {

        "S0": Sensor(0, 150),

        "S1": Sensor(30, 150),

        "S2": Sensor(-30, 150),

        "S3": Sensor(60, 150),

        "S4": Sensor(-60, 150),

        "S5": Sensor(110, 150),

        "S6": Sensor(-110, 150)
    }

    population.append({

        "car": car,

        "brain": brain,

        "sensors": sensors,

        "previous_point": 0,

        "current_point": 0,

        "lap": 0,

        "distance": 0,

        "crashed": False
    })



SEARCH_BACK = 20
SEARCH_FORWARD = 20




running = True


while running:


    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False



    for agent in population:

        car = agent["car"]

        brain = agent["brain"]

        sensors = agent["sensors"]



        if agent["crashed"]:

            continue




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


        for value in sensor_values:

            if value < 0.1:

                car.stop()

                car.kill()

                agent["crashed"] = True

                break


        if agent["crashed"]:

            continue



        car_position = pygame.math.Vector2(

            car.x_pos,

            car.y_pos
        )


        current_point = agent["current_point"]

        previous_point = agent["previous_point"]


        closest_index = current_point

        closest_distance = float("inf")


        # Search only nearby points

        start_index = max(

            0,

            current_point - SEARCH_BACK
        )


        end_index = min(

            len(inner_points),

            current_point + SEARCH_FORWARD + 1
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

            # print(
            #     "Car",
            #     population.index(agent),
            #     "Forward lap:",
            #     agent["lap"]
            # )


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

            # print(
            #     "Car",
            #     population.index(agent),
            #     "Reverse lap:",
            #     agent["lap"]
            # )


        agent["current_point"] = closest_index

        agent["previous_point"] = closest_index


        agent["distance"] = (

            agent["lap"] * track_length

            + track_distances[closest_index]
        )



        output = brain.forward(

            sensor_values
        )


        throttle = output[0]

        steer = output[1]



        car.update(

            throttle,

            steer
        )

    all_crashed = True
    best_car = max(
                population,
                key=lambda agent: agent["distance"]
            )
    best_distance=best_car["distance"]

    for agent in population:

        if not agent["crashed"]:
            all_crashed = False
            break


    if all_crashed:

        print("All cars crashed!")


        # Find best car

        best_car = max(
            population,
            key=lambda agent: agent["distance"]
        )


        print()
        print("================================")
        print("BEST CAR")
        print("================================")

        print(
            "Best distance:",
            best_car["distance"]
        )

        print(
            "Best lap:",
            best_car["lap"]
        )


        # Print weights and biases

        for i, layer in enumerate(
            best_car["brain"].layers
        ):

            print()
            print(
                "Layer",
                i + 1
            )

            print("Weights:")

            for weights in layer.weights:

                print(weights)


            print("Biases:")

            for bias in layer.bias:

                print(bias)


        print()
        print("================================")
        print("SIMULATION FINISHED")
        print("================================")


        break

    screen.fill(

        (30, 120, 50)
    )



    if len(outer_points) >= 2:

        pygame.draw.lines(

            screen,

            (255, 255, 255),

            False,

            outer_points,

            6
        )



    if len(inner_points) >= 2:

        pygame.draw.lines(

            screen,

            (255, 255, 255),

            False,

            inner_points,

            6
        )


    for index, agent in enumerate(population):

        car = agent["car"]

        sensors = agent["sensors"]



        for sensor in sensors.values():

            sensor.draw(

                screen,

                car.x_pos,

                car.y_pos
            )

        if agent is best_car:

            car_image.fill(

                (255, 255, 0)
            )

        elif agent["crashed"]:

            car_image.fill(

                (80, 80, 80)
            )

        else:

            car_image.fill(

                (200, 50, 50)
            )


 

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
        # Car Number
        # --------------------------------

        number_text = font.render(

            str(index),

            True,

            (255, 255, 255)
        )


        screen.blit(

            number_text,

            (

                car.x_pos - 5,

                car.y_pos - 45
            )
        )


 

    best_distance_text = font.render(

        f"Best Distance: {best_distance:.1f}",

        True,

        (255, 255, 255)
    )


    screen.blit(

        best_distance_text,

        (20, 20)
    )


    best_lap_text = font.render(

        f"Best Lap: {best_car['lap']}",

        True,

        (255, 255, 255)
    )


    screen.blit(

        best_lap_text,

        (20, 50)
    )


  

    y = 90


    for index, agent in enumerate(population):

        text = font.render(

            f"Car {index}: {agent['distance']:.1f}",

            True,

            (255, 255, 255)
        )


        screen.blit(

            text,

            (20, y)
        )


        y += 25




    pygame.display.flip()

    clock.tick(20)
    # print("best_car",best_car)
    # print("best_distance",best_distance)



pygame.quit()
