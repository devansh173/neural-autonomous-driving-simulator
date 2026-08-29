import pygame
import json
import os


pygame.init()


# Settings

WIDTH = 1000
HEIGHT = 800

BACKGROUND_COLOR = (30, 120, 50)

OUTER_COLOR = (255, 255, 255)
INNER_COLOR = (255, 255, 255)

POINT_DISTANCE = 5


# Pygame

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Track Editor")

clock = pygame.time.Clock()

font = pygame.font.Font(None, 30)


# Folder

TRACK_FOLDER = "tracks"

os.makedirs(
    TRACK_FOLDER,
    exist_ok=True
)


# Track Data

outer_points = []
inner_points = []

# Mode
# 0 = outer
# 1 = inner
draw_mode = 0


# Track Name

track_name = ""

typing_name = False


# Add Point

def add_point(points, position):

    if len(points) == 0:

        points.append(position)
        return

    last_point = points[-1]

    distance = pygame.math.Vector2(
        position
    ).distance_to(last_point)

    if distance >= POINT_DISTANCE:

        points.append(position)


# Save Track

def save_track():

    if track_name == "":
        print("Enter a track name first.")
        return

    if len(outer_points) < 2:
        print("Outer track line is too short.")
        return

    if len(inner_points) < 2:
        print("Inner track line is too short.")
        return

    track_data = {

        "name": track_name,

        "outer": outer_points,

        "inner": inner_points
    }

    filename = os.path.join(
        TRACK_FOLDER,
        track_name + ".json"
    )

    with open(filename, "w") as file:

        json.dump(
            track_data,
            file,
            indent=4
        )

    print(
        f"Track saved: {filename}"
    )


# Reset

def reset_track():

    global draw_mode
    global track_name

    outer_points.clear()
    inner_points.clear()

    draw_mode = 0

    track_name = ""

    print("Track reset.")


# Main Loop

running = True


while running:

    # Events

    for event in pygame.event.get():

        # Quit

        if event.type == pygame.QUIT:

            running = False


        # Keyboard

        if event.type == pygame.KEYDOWN:

            # Enter

            if event.key == pygame.K_RETURN:

                if typing_name:

                    typing_name = False

                elif draw_mode == 0:

                    if len(outer_points) >= 2:

                        draw_mode = 1

                        print(
                            "Now draw the INNER line."
                        )

                elif draw_mode == 1:

                    if len(inner_points) >= 2:

                        draw_mode = 2

                        print(
                            "Track drawing finished."
                        )


            # Name

            if event.key == pygame.K_n:

                typing_name = True

                track_name = ""


            # Save

            if event.key == pygame.K_s:

                if not typing_name:

                    save_track()


            # Reset

            if event.key == pygame.K_r:

                if not typing_name:

                    reset_track()


            # Text Input

            if typing_name:

                if event.key == pygame.K_BACKSPACE:

                    track_name = track_name[:-1]

                elif event.key not in (
                    pygame.K_RETURN,
                    pygame.K_ESCAPE
                ):

                    character = event.unicode

                    if character.isalnum() or character in (
                        "_",
                        "-"
                    ):

                        track_name += character


        # Mouse

        if not typing_name:

            if event.type == pygame.MOUSEMOTION:

                # Left Button

                if pygame.mouse.get_pressed()[0]:

                    position = pygame.mouse.get_pos()


                    # Outer

                    if draw_mode == 0:

                        add_point(
                            outer_points,
                            position
                        )


                    # Inner

                    elif draw_mode == 1:

                        add_point(
                            inner_points,
                            position
                        )


    # Draw

    screen.fill(
        BACKGROUND_COLOR
    )


    # Outer Line

    if len(outer_points) >= 2:

        pygame.draw.lines(
            screen,
            OUTER_COLOR,
            False,
            outer_points,
            6
        )


    # Inner Line

    if len(inner_points) >= 2:

        pygame.draw.lines(
            screen,
            INNER_COLOR,
            False,
            inner_points,
            6
        )


    # UI

    if typing_name:

        title = font.render(
            "Enter track name:",
            True,
            (255, 255, 255)
        )

        screen.blit(
            title,
            (20, 20)
        )

        name_text = font.render(
            track_name + "_",
            True,
            (255, 255, 0)
        )

        screen.blit(
            name_text,
            (20, 55)
        )

        instruction = font.render(
            "ENTER = confirm",
            True,
            (255, 255, 255)
        )

        screen.blit(
            instruction,
            (20, 90)
        )


    elif draw_mode == 0:

        title = font.render(
            "DRAW OUTER TRACK",
            True,
            (255, 255, 255)
        )

        screen.blit(
            title,
            (20, 20)
        )

        instruction = font.render(
            "Hold LEFT MOUSE and draw the OUTER line",
            True,
            (255, 255, 255)
        )

        screen.blit(
            instruction,
            (20, 55)
        )

        instruction = font.render(
            "ENTER = Inner line",
            True,
            (255, 255, 255)
        )

        screen.blit(
            instruction,
            (20, 90)
        )


    elif draw_mode == 1:

        title = font.render(
            "DRAW INNER TRACK",
            True,
            (255, 255, 255)
        )

        screen.blit(
            title,
            (20, 20)
        )

        instruction = font.render(
            "Hold LEFT MOUSE and draw the INNER line",
            True,
            (255, 255, 255)
        )

        screen.blit(
            instruction,
            (20, 55)
        )

        instruction = font.render(
            "ENTER = Finish track",
            True,
            (255, 255, 255)
        )

        screen.blit(
            instruction,
            (20, 90)
        )


    else:

        title = font.render(
            "TRACK FINISHED",
            True,
            (255, 255, 255)
        )

        screen.blit(
            title,
            (20, 20)
        )

        instruction = font.render(
            f"Track: {track_name}",
            True,
            (255, 255, 255)
        )

        screen.blit(
            instruction,
            (20, 55)
        )

        instruction = font.render(
            "N = Rename   S = Save   R = Reset",
            True,
            (255, 255, 255)
        )

        screen.blit(
            instruction,
            (20, 90)
        )


    # Display

    pygame.display.flip()

    clock.tick(60)


pygame.quit()
