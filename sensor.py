import math
import pygame


class Sensor:

    def __init__(self, relative_angle, max_length=150):
        self.relative_angle = relative_angle
        self.max_length = max_length

        
        self.value = 1.0

        # Actual distance to wall
        self.distance = max_length

        # End point of the sensor
        self.end_x = 0
        self.end_y = 0

   

    def update(self, car_x, car_y, car_angle,
               outer_points, inner_points):

       

        world_angle = car_angle + self.relative_angle

        angle_rad = math.radians(world_angle)

       

        dx = math.cos(angle_rad)
        dy = -math.sin(angle_rad)

        

        max_x = car_x + dx * self.max_length
        max_y = car_y + dy * self.max_length

        
        closest_distance = self.max_length

     

        for i in range(len(outer_points) - 1):

            p1 = outer_points[i]
            p2 = outer_points[i + 1]

            distance = self.ray_segment_intersection(
                car_x,
                car_y,
                dx,
                dy,
                p1[0],
                p1[1],
                p2[0],
                p2[1]
            )

            if distance is not None:

                if distance < closest_distance:
                    closest_distance = distance

        

        for i in range(len(inner_points) - 1):

            p1 = inner_points[i]
            p2 = inner_points[i + 1]

            distance = self.ray_segment_intersection(
                car_x,
                car_y,
                dx,
                dy,
                p1[0],
                p1[1],
                p2[0],
                p2[1]
            )

            if distance is not None:

                if distance < closest_distance:
                    closest_distance = distance

        

        self.distance = closest_distance

        

        self.value = closest_distance / self.max_length
# Make absolutely sure it stays between 0 and 1

        self.value = max(
            0.0,
            min(1.0, self.value)
        )

      

        self.end_x = car_x + dx * closest_distance
        self.end_y = car_y + dy * closest_distance

        return self.value

    

    def ray_segment_intersection(
        self,
        ray_x,
        ray_y,
        ray_dx,
        ray_dy,
        x1,
        y1,
        x2,
        y2
    ):

        # Segment direction
        segment_dx = x2 - x1
        segment_dy = y2 - y1

        # Cross product
        denominator = (
            ray_dx * segment_dy
            - ray_dy * segment_dx
        )

        # Lines are parallel
        if abs(denominator) < 0.000001:
            return None

        # Distance along ray
        t = (
            (x1 - ray_x) * segment_dy
            - (y1 - ray_y) * segment_dx
        ) / denominator

        # Position along track segment
        u = (
            (x1 - ray_x) * ray_dy
            - (y1 - ray_y) * ray_dx
        ) / denominator

        

        if t >= 0 and 0 <= u <= 1:

            distance = t * math.sqrt(
                ray_dx ** 2 +
                ray_dy ** 2
            )

            if distance <= self.max_length:
                return distance

        return None

   
    def draw(self, screen, car_x, car_y):

      

        red = int(
            255 * (1 - self.value)
        )

        green = int(
            255 * self.value
        )

        color = (
            red,
            green,
            0
        )

        pygame.draw.line(
            screen,
            color,
            (car_x, car_y),
            (self.end_x, self.end_y),
            2
        )

        # Draw sensor endpoint

        pygame.draw.circle(
            screen,
            color,
            (
                int(self.end_x),
                int(self.end_y)
            ),
            4
        )

