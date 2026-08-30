import pygame
import json
import os

from neural_network import Neural_Network

from car import Car
from sensor import Sensor


# --------------------------------
# Settings
# --------------------------------

WIDTH = 1000
HEIGHT = 800

TRACK_NAME = "three"

TRACK_FOLDER = "tracks"

CHECKPOINT_FILE = (
    "training_checkpoint.json"
)


# --------------------------------
# Load track
# --------------------------------

def load_track(name):

    filename = os.path.join(

        TRACK_FOLDER,

        name + ".json"
    )


    with open(
        filename,
        "r"
    ) as file:

        return json.load(
            file
        )


# --------------------------------
# Load trained brain
#
# FIX: "architecture" lives at the top
# level of the checkpoint (alongside
# "generation" and "best_brain"), not
# inside best_brain itself. We build the
# Neural_Network using that architecture,
# then load the saved weights/biases via
# set_data().
# --------------------------------

def load_brain():

    if not os.path.exists(
        CHECKPOINT_FILE
    ):

        raise FileNotFoundError(

            "training_checkpoint.json "
            "does not exist. "
            "Run train.py first."
        )


    with open(
        CHECKPOINT_FILE,
        "r"
    ) as file:

        data = json.load(
            file
        )


    brain = Neural_Network(
        data["architecture"]
    )


    brain.set_data(
        data["best_brain"]
    )


    print(
        "Loaded generation:",
        data["generation"]
    )


    return brain


# --------------------------------
# Pygame
# --------------------------------

pygame.init()


screen = pygame.display.set_mode(

    (WIDTH, HEIGHT)
)


pygame.display.set_caption(

    "Trained Self Driving Car"
)


clock = pygame.time.Clock()


font = pygame.font.Font(
    None,
    30
)


# --------------------------------
# Load track
# --------------------------------

track = load_track(
    TRACK_NAME
)


outer_points = track[
    "outer"
]


inner_points = track[
    "inner"
]


# --------------------------------
# Load brain
# --------------------------------

brain = load_brain()


# --------------------------------
# Create car
# --------------------------------

my_car = Car(

    100,

    600,

    0,

    90,

    True
)


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
# Sensors
# --------------------------------

sensors = {

    "S0": Sensor(
        0,
        150
    ),

    "S1": Sensor(
        30,
        150
    ),

    "S2": Sensor(
        -30,
        150
    ),

    "S3": Sensor(
        60,
        150
    ),

    "S4": Sensor(
        -60,
        150
    ),

    "S5": Sensor(
        110,
        150
    ),

    "S6": Sensor(
        -110,
        150
    )
}


# --------------------------------
# Running
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
    # Sensor values
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
    # Crash
    # --------------------------------

    crashed = False


    for value in sensor_values:

        if value < 0.1:

            my_car.stop()

            my_car.kill()

            crashed = True

            break


    # --------------------------------
    # Neural network
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
    # Draw background
    # --------------------------------

    screen.fill(

        (30, 120, 50)
    )


    # --------------------------------
    # Outer track
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
    # Inner track
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
    # Sensors
    # --------------------------------

    for sensor in sensors.values():

        sensor.draw(

            screen,

            my_car.x_pos,

            my_car.y_pos
        )


    # --------------------------------
    # Car
    # --------------------------------

    if my_car.is_alive:

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
    # Status
    # --------------------------------

    if my_car.is_alive:

        status = "ALIVE"

    else:

        status = "CRASHED"


    status_text = font.render(

        status,

        True,

        (255, 255, 255)
    )


    screen.blit(

        status_text,

        (20, 20)
    )


    # --------------------------------
    # Output
    # --------------------------------

    if my_car.is_alive:

        output = brain.forward(
            sensor_values
        )


        output_text = font.render(

            f"Throttle: {output[0]:.2f} "
            f"Steer: {output[1]:.2f}",

            True,

            (255, 255, 255)
        )


        screen.blit(

            output_text,

            (20, 50)
        )


    pygame.display.flip()

    clock.tick(60)


pygame.quit()