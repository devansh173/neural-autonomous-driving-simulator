import pygame
import json
import os

from car import Car


pygame.init()


# Settings

WIDTH = 1000
HEIGHT = 800

TRACK_NAME = "first"

TRACK_FOLDER = "tracks"


# Load

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


# Pygame

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT)
)

pygame.display.set_caption(
    TRACK_NAME
)

clock = pygame.time.Clock()


# Car

my_car = Car(
    100, # will always keep this starting position
    600,
    0,
    90,
    True
)


# Image

car_image = pygame.Surface(
    (30, 50),
    pygame.SRCALPHA
)

car_image.fill(
    (200, 50, 50)
)


# Loop

running = True


while running:

    # Events

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False


    # Input

    keys = pygame.key.get_pressed()

    forward = keys[pygame.K_w]
    backward = keys[pygame.K_s]

    left = keys[pygame.K_a]
    right = keys[pygame.K_d]


    # Update

    my_car.update(
        forward,
        backward,
        left,
        right
    )


    # Background

    screen.fill(
        (30, 120, 50)
    )


    # Track

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


    # Draw

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


    # Display

    pygame.display.flip()

    clock.tick(60)


pygame.quit()
