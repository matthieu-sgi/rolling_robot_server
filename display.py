import pygame
import os
import time
import math


LIDAR_MAX_DIST = 5


class Window:

    def __init__(self, cloud_point, x_size : int = 400, y_size: int = 400, fps :int = 30):
        pygame.init()
        pygame.display.init()
        self.x_size = x_size
        self.y_size = y_size
        self.window = pygame.display.set_mode((self.x_size,self.y_size))
        # draw robot/lidar point
        self.cloud_point = cloud_point
        self.display_points = [(0,0)] * len(self.cloud_point)
        pygame.draw.circle(self.window, (0,0,255),(self.x_size/2,self.y_size/2), 10)
        self.last_update = time.time()
        self.fps = fps
        self.update()

    def update(self):
        pygame.display.update()
    
    def update_from_cloud_point(self):
        if self.cloud_point == None:
            return
        # print(self.cloud_point)
        for index in range(len(self.cloud_point)):
            cyl_coords = self.cloud_point[index]
            pygame.draw.circle(self.window, (0,0,0), self.display_points[index], 3)
            coords = self.shift_and_transform_coords(cyl_coords=cyl_coords)
            # print(f'coords: {coords}')
            self.display_points[index] = coords
            # print(f' x: {coords[0]} y: {coords[1]}')
            # if (coords[0] > 5 or coords[0] < -5) and (coords[1] > 5 or coords[1] < -5):
            pygame.draw.circle(self.window, (0,0,255),(self.x_size/2,self.y_size/2), 10)
            pygame.draw.circle(self.window, (255,255,255), coords, 3)
        if time.time() - self.last_update  > (1.0/float(self.fps)):
            self.update()
            self.last_update = time.time()

    def shift_and_transform_coords(self, cyl_coords: tuple):
        # print(f'r cyl :{cyl_coords[0]}')
        x, y = self.cylindrical_coords_to_cartesian(cyl_coords)
        # print(f'x: {x}')
        resized_x = (x*self.x_size)/LIDAR_MAX_DIST
        shifted_x = resized_x + (self.x_size/2)

        resized_y = (y*self.y_size)/LIDAR_MAX_DIST
        shifted_y = resized_y + (self.y_size/2)
        # print(f'shifted_x : {shifted_x}')
        return(int(shifted_x),int(shifted_y))

    def cylindrical_coords_to_cartesian(self, cyl_coords : tuple):
        theta = math.radians(cyl_coords[1])
        r = cyl_coords[0]
        return (r*math.cos(theta), r*math.sin(theta))
