import pygame
import json
import os
from neural_network import Neural_Network

from car import Car
from sensor import Sensor


pygame.init()


# --------------------------------
# Settings
# --------------------------------

WIDTH = 1000
HEIGHT = 800

TRACK_NAME = "three"

TRACK_FOLDER = "tracks"


# --------------------------------
# Load Track
# --------------------------------

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


# --------------------------------
# Track Distance
# --------------------------------

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


# --------------------------------
# Pygame
# --------------------------------

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


# --------------------------------
# Car
# --------------------------------

my_car = Car(
    100,
    600,
    0,
    90,
    True
)


# --------------------------------
# Neural Network
# --------------------------------

brain = Neural_Network(
    [7, 8, 2]
)


# --------------------------------
# Car Image
# --------------------------------

car_image = pygame.Surface(
    (30, 50),
    pygame.SRCALPHA
)

car_image.fill(
    (200, 50, 50)
)


# --------------------------------
# Sensors
# --------------------------------

sensors = {

    "S0": Sensor(0, 150),

    "S1": Sensor(30, 150),

    "S2": Sensor(-30, 150),

    "S3": Sensor(60, 150),

    "S4": Sensor(-60, 150),

    "S5": Sensor(110, 150),

    "S6": Sensor(-110, 150)
}


# --------------------------------
# Track Progress
# --------------------------------

previous_point = 0

current_point = 0

lap = 0

distance_traveled = 0


# --------------------------------
# Search Settings
# --------------------------------

# Only search nearby points.

SEARCH_BACK = 20
SEARCH_FORWARD = 20


# --------------------------------
# Main Loop
# --------------------------------

running = True


while running:

    # --------------------------------
    # Events
    # --------------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False


    # --------------------------------
    # Sensors
    # --------------------------------

    for sensor in sensors.values():

        sensor.update(

            my_car.x_pos,

            my_car.y_pos,

            my_car.angle,

            outer_points,

            inner_points
        )


    # --------------------------------
    # Sensor Values
    # --------------------------------

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
    # Find Closest Track Point
    # --------------------------------

    car_position = pygame.math.Vector2(

        my_car.x_pos,

        my_car.y_pos
    )


    closest_index = current_point

    closest_distance = float("inf")


    # Search only around the previous point

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


    # --------------------------------
    # Detect Forward Lap
    # --------------------------------

    # Near the end of the track

    near_end = (

        previous_point
        > len(inner_points) * 0.8
    )


    # Now near the beginning

    near_start = (

        closest_index
        < len(inner_points) * 0.2
    )


    if near_end and near_start:

        lap += 1

        print(
            "Forward lap:",
            lap
        )


    # --------------------------------
    # Detect Reverse Lap
    # --------------------------------

    near_start_before = (

        previous_point
        < len(inner_points) * 0.2
    )


    near_end_now = (

        closest_index
        > len(inner_points) * 0.8
    )


    if near_start_before and near_end_now:

        lap -= 1

        print(
            "Reverse lap:",
            lap
        )


    # --------------------------------
    # Update Current Point
    # --------------------------------

    current_point = closest_index

    previous_point = closest_index


   

    distance_traveled = (

        lap * track_length

        + track_distances[current_point]
    )

    print(distance_traveled)
 

    crashed = False


    for value in sensor_values:

        if value < 0.1:

            my_car.stop()

            my_car.kill()

            crashed = True

            break


    # --------------------------------
    # Neural Network
    # --------------------------------

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
    # Draw Sensors
    # --------------------------------

    for sensor in sensors.values():

        sensor.draw(

            screen,

            my_car.x_pos,

            my_car.y_pos
        )


    # --------------------------------
    # Draw Car
    # --------------------------------

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


    # --------------------------------
    # Display Information
    # --------------------------------

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


    point_text = font.render(

        f"Track Point: {current_point}",

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


    screen.blit(

        point_text,

        (20, 80)
    )


    # --------------------------------
    # Display
    # --------------------------------

    pygame.display.flip()

    clock.tick(60)


pygame.quit()
