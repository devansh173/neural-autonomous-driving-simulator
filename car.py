import math


class Car:
    def __init__(self, x_pos, y_pos, speed, angle, is_alive):
        self.x_pos = x_pos
        self.y_pos = y_pos

        self.speed = speed
        self.angle = angle

        self.is_alive = is_alive

        self.max_speed = 4
        self.acceleration = 0.10
        self.friction = 0.08
        self.brake_power = 0.20

        self.max_steering = 2.5

    def update(self, throttle, steer):

        if not self.is_alive:
            return

        # -----------------
        # THROTTLE
        # -----------------

        if throttle > 0:
            self.speed += self.acceleration * throttle

            if self.speed > self.max_speed:
                self.speed = self.max_speed

        elif throttle < 0:
            self.speed += self.acceleration * throttle

            if self.speed < -self.max_speed / 2:
                self.speed = -self.max_speed / 2

        else:
            # friction
            if self.speed > 0:
                self.speed -= self.friction

                if self.speed < 0:
                    self.speed = 0

            elif self.speed < 0:
                self.speed += self.friction

                if self.speed > 0:
                    self.speed = 0

        # -----------------
        # STEERING
        # -----------------

        speed_ratio = abs(self.speed) / self.max_speed

        steering = self.max_steering * speed_ratio * steer

        self.angle -= steering

        # -----------------
        # MOVEMENT
        # -----------------

        angle_rad = math.radians(self.angle)

        self.x_pos += math.cos(angle_rad) * self.speed
        self.y_pos -= math.sin(angle_rad) * self.speed

    def stop(self):
        self.speed = 0

    def kill(self):
        self.is_alive = False

    def get_state(self):
        return {
            "x_pos": self.x_pos,
            "y_pos": self.y_pos,
            "speed": self.speed,
            "angle": self.angle,
            "is_alive": self.is_alive
        }
