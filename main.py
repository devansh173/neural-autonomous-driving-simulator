import pygame
import json
import os
from neural_network import Neural_Network

from car import Car
from sensor import Sensor


pygame.init()


WIDTH = 1000
HEIGHT = 800

TRACK_NAME = "first"

TRACK_FOLDER = "tracks"


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

    distance = point_a.distance_to(point_b)

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


my_car = Car(
    100,
    600,
    0,
    90,
    True
)


brain = Neural_Network([7, 8, 2])


car_image = pygame.Surface(
    (30, 50),
    pygame.SRCALPHA
)

car_image.fill(
    (200, 50, 50)
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


furthest_point = 0

previous_point = 0

lap = 0

distance_traveled = 0


running = True


while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False


    for sensor in sensors.values():

        sensor.update(
            my_car.x_pos,
            my_car.y_pos,
            my_car.angle,
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


    car_position = pygame.math.Vector2(
        my_car.x_pos,
        my_car.y_pos
    )


    closest_index = 0

    closest_distance = float("inf")


    for i, point in enumerate(inner_points):

        track_point = pygame.math.Vector2(
            point
        )

        distance = car_position.distance_to(
            track_point
        )

        if distance < closest_distance:

            closest_distance = distance

            closest_index = i


    if previous_point > len(inner_points) * 0.8:

        if closest_index < len(inner_points) * 0.2:

            lap += 1

            furthest_point = closest_index

            print("Lap:", lap)


    if closest_index > furthest_point:

        furthest_point = closest_index


    previous_point = closest_index


    distance_traveled = (
        lap * track_length
        + track_distances[furthest_point]
    )
    print("distance traveled",distance_traveled)


    crashed = False


    for value in sensor_values:

        if value < 0.1:

            

            my_car.stop()

            my_car.kill()

            crashed = True

            break


    if not crashed:

        output = brain.forward(
            sensor_values
        )

        throttle = output[0]

        steer = output[1]

        my_car.update(
            throttle,
            steer
        )


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


    for sensor in sensors.values():

        sensor.draw(
            screen,
            my_car.x_pos,
            my_car.y_pos
        )


    rotated_car = pygame.transform.rotate(
        car_image,
        my_car.angle - 90
    )


    car_rect = rotated_car.get_rect(
        center=(
            my_car.x_pos,
            my_car.y_pos
        )
    )


    screen.blit(
        rotated_car,
        car_rect
    )


    font = pygame.font.Font(
        None,
        30
    )


    distance_text = font.render(
        f"Distance: {distance_traveled:.1f}",
        True,
        (255, 255, 255)
    )


    lap_text = font.render(
        f"Lap: {lap}",
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


pygame.quit()