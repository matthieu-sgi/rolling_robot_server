import pygame
import serial
import os
import math
import numpy as np

LIDAR_RESOLUTION = 0.8
LIDAR_MAX_DIST = 12000
serial_protocol_translation = {
    "sa" : "start angle",
    "nbv" : "number of values",
    "X" : "value index with value",
    "ea" : "end angle"
}

files = os.listdir('/dev')
port = ""
for devices in files:
    if devices.startswith('ttyACM'):
        port = f'/dev/{devices}'
print(port)
ser = serial.Serial(
    port=port,
    baudrate=230400,
    bytesize=8,
    parity=serial.PARITY_NONE,
    stopbits=1
)

class LidarPoint:
    def __init__(self, angle:int, distance : int):
        self._angle = angle
        self._distance = distance

    @property
    def angle(self):
        return self._angle

    @property
    def distance(self):
        return self._distance

class LidarCloudPoint:
    def __init__(self,):
        self.start_angle = None
        self.nb_value = None
        self.number_of_points = int(360 / LIDAR_RESOLUTION)
        self.points_distances = np.zeros(self.number_of_points) # Number of value of one rotation
        self.points_angles = np.zeros(self.number_of_points) # Number of value of one rotation
        self.nb_value = None
        self.end_angle = None
        
        # self.delta_angle = None

    def __getitem__(self, index: int) -> tuple:
        return (self.points_distances[index], self.points_angles[index])
    
    def __setitem__(self, index: int, value: tuple) -> None:
        self.points_distances[index] = value[0]
        self.points_angles[index] = value[1]

    def __len__(self) -> int:
        return self.number_of_points

    def __iter__(self) -> tuple:
        self.current_index = 0
        return self
    
    def __next__(self):
        if self.current_index < self.number_of_points:
            r = self.points_distances[self.current_index]
            theta = self.points_angles[self.current_index]
            self.current_index += 1
            return (r, theta)
        raise StopIteration


    def ingest_frame(self, frame: bytes):
        frame = frame[:-1] # remove the '\n' at the end of frame
        data_array = frame.decode(encoding='ascii').split(' ')
        distances = []
        print(data_array)
        if data_array[0].split(':')[0] == "sa": #checking if we have a complete frame
            for data in data_array:
                try:
                    key, value = data.split(':')
                except ValueError:
                    print("Frame not full")
                    return

                value = int(value)
                if key == 'sa': # start angle
                    self.start_angle = value
                elif key == 'nbv': # number of values
                    self.nb_value = value
                elif self.nb_value != None and key in [str(i) for i in range(0, self.nb_value)]: # distance
                    distances.append(value)
                elif key == 'ea': # end angle
                    self.end_angle = value

            resolution = LIDAR_RESOLUTION

            for i in range(self.nb_value):
                point_angle = self.start_angle + resolution*i
                if point_angle > 36000:
                    point_angle -= 36000
                
                index = int(np.round(point_angle / (resolution * 100)))
                if index>= self.nb_value:
                    index = self.nb_value-1

                self.points_distances[index] = distances[i]
                self.points_angles[index] = point_angle

class Window:

    def __init__(self, x_size : int = 400, y_size: int = 400):
        pygame.init()
        pygame.display.init()
        self.x_size = x_size
        self.y_size = y_size
        self.window = pygame.display.set_mode((self.x_size,self.y_size))
        # draw robot/lidar point
        pygame.draw.circle(self.window, (255,255,255),(self.x_size/2,self.y_size/2), 10)
        self.update()

    def update(self):
        pygame.display.update()
    
    def update_from_cloud_point(self, cloud_point : LidarCloudPoint):

        for r, theta in cloud_point:
            x, y = self.shift_and_transform_coords(r=r,theta=theta)
            pygame.draw.circle(self.window, (255,255,255), (x,y), 3)
        self.update()

    def shift_and_transform_coords(self, r, theta):
        x, y = self.cylindrical_coords_to_cartesian(r, theta)

        resized_x = (x*self.x_size)/LIDAR_MAX_DIST
        shifted_x = resized_x + (self.x_size/2)

        resized_y = (y*self.y_size)/LIDAR_MAX_DIST
        shifted_y = resized_y + (self.y_size/2)

        return(shifted_x,shifted_y)

    def cylindrical_coords_to_cartesian(self, theta, r):
        return (r*math.cos(theta), r*math.sin(theta))

lidar_value = ''
max_lidar_value = 0
min_lidar_value = 1000

window = Window(400,400)
# window.window.fill((0,0,0))
# pygame.draw.rect(window.window,(255,255,255),(200,150,100,50))
# window.update()
cloud_point = LidarCloudPoint()

while True:
    # next_byte = ser.read(1)#.decode('ascii')#.split('\r\n')
    # next_frame = ser.readlines(1)#.decode('ascii')#.split('\r\n')
    next_frame = ser.read_until(b"\n")#.decode('ascii')#.split('\r\n')
    # print(next_frame)
    cloud_point.ingest_frame(next_frame)
    window.update_from_cloud_point(cloud_point=cloud_point)

    # print(f'start_angle {cloud_point.start_angle}')
    # print(f'end_angle {cloud_point.end_angle}')
    # print(f'points {cloud_point.points}')
    # print(f'nb value {cloud_point.nb_value}')
    # if next_byte == b'2c':
        # break
    # if next_byte != '\n' and next_byte != '\r':
    #     lidar_value += next_byte
    # else:
    #     lidar_value = ''
    # if lidar_value != '':
    #     print(lidar_value)
    # break
    # display.fill((255,255,255))
    # # iterate over the list of Event objects
    # # that was returned by pygame.event.get() method.
    # for event in pygame.event.get():
 
    #     # if event object type is QUIT
    #     # then quitting the pygame
    #     # and program both.
    #     if event.type == pygame.QUIT:
 
    #         # deactivates the pygame library
    #         pygame.quit()
 
    #         # quit the program.
    #         quit()
 
    #     # Draws the surface object to the screen.
    #     pygame.display.update()
    ...