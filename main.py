import pygame
import serial
import os
import math
import numpy as np
import time

LIDAR_RESOLUTION = 0.8
LIDAR_MAX_DIST = 5
serial_protocol_translation = {
    "sa" : "start angle",
    "nbv" : "number of values",
    "X" : "value index with value",
    "ea" : "end angle"
}
FPS = 30

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
        print(f'number of points : {self.number_of_points}')
        self.points_distances = np.zeros(self.number_of_points, dtype=np.float32) # Number of value of one rotation
        self.points_angles = np.zeros(self.number_of_points, dtype=np.float32) # Number of value of one rotation
        self.nb_value = 12
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
    
    def get_points_angle(self) -> np.ndarray:
        return self.points_angles

    def get_points_distances(self) -> np.ndarray:
        return self.points_distances
    
    def __next__(self):
        if self.current_index < self.number_of_points:
            r = self.points_distances[self.current_index]
            theta = self.points_angles[self.current_index]
            self.current_index += 1
            return (r, theta)
        raise StopIteration

    def check_frame_integrity_and_format(self, frame: list)-> bool:
        
        if len(frame) != 15:
            return False
        
        for counter, data in enumerate(frame):
            print(f'data : {data} | counter : {counter}')
            try:
                key, value = data.split(':')
            except ValueError:
                print("Frame not full")
                return False
            
            try:
                value = int(value)
            except ValueError:
                return False

            if counter == 0:
                if key != "sa":
                    print("Incorrect frame")
                    return False
                else:
                    self.start_angle = float(value/100.0)
            
            if counter == 1 :
                if key != "nbv":
                    print("Incorrect frame")
                    return False
            
            if counter < len(frame) -1 and counter > 1:
                if str(counter - 2) != key:
                    print("Incorrect frame")
                    # print(f"counter : {counter - 2} | key : {key}")
                    return False
                else:
                    print(f'appending value : {value}')
                    self.pre_formatted_distances.append(float(value/1000.0))
                
            
            if counter == len(frame) -1 :
                if key != 'ea':
                    print("Incorrect frame")
                    return False
                else:
                    self.end_angle = float(value/100.0)

        return True
        
    def ingest_frame(self, frame: bytes):
        frame = frame[:-1] # remove the '\n' at the end of frame
        data_array = frame.decode(encoding='ascii').split(' ')
        self.pre_formatted_distances = []
        print(data_array)
        if self.check_frame_integrity_and_format(data_array):
            # for data in data_array:
            #     try:
            #         key, value = data.split(':')
            #     except ValueError:
            #         print("Frame not full")
            #         return

            #     # value = int(value)
            #     try:
            #         value = int(value)
            #     except ValueError:
            #         continue

            #     if key == 'sa': # start angle
            #         self.start_angle = float(value/100.0)
            #     elif self.nb_value != None and key in [str(i) for i in range(0, self.nb_value)]: # distance
            #         print(f'distance : {value} | distance divided {float(value/1000.0)}')
            #         self.pre_formatted_distances.append(float(value/1000.0))
            #     elif key == 'ea': # end angle
            #         self.end_angle = float(value/100.0)

            resolution = LIDAR_RESOLUTION

            for i in range(self.nb_value):
                point_angle = self.start_angle + resolution*i
                if point_angle > 360:
                    point_angle -= 360
                
                index = int(np.round(point_angle / (resolution)))
                if index >= self.number_of_points:
                    index = self.number_of_points-1

                # print(f'point angle {self.pre_formatted_distances[i]} | index : {index}')
                try:
                    self.points_distances[index] = self.pre_formatted_distances[i]
                    self.points_angles[index] = point_angle
                except:
                    print(f' data array length : {len(data_array)}\ndata array: {data_array}')
                    print(f'index: {index}')
                    
                    print(f'distance len: {len(self.pre_formatted_distances)}')
                    
                    print(f'point angle: {point_angle}')
                    print(f'distance: {self.pre_formatted_distances[i]}')
class Window:

    def __init__(self, x_size : int = 400, y_size: int = 400):
        pygame.init()
        pygame.display.init()
        self.x_size = x_size
        self.y_size = y_size
        self.window = pygame.display.set_mode((self.x_size,self.y_size))
        # draw robot/lidar point
        self.cloud_point = None
        pygame.draw.circle(self.window, (0,0,255),(self.x_size/2,self.y_size/2), 10)
        self.last_update = time.time()
        self.update()

    def update(self):
        pygame.display.update()
    
    def update_from_cloud_point(self, cloud_point : LidarCloudPoint):

        for index in range(len(cloud_point)):
            cyl_coords = cloud_point[index]
            # print(cyl_coords)
            if self.cloud_point == None:
                self.cloud_point = [(0,0)] * len(cloud_point)
            else :
                pygame.draw.circle(self.window, (0,0,0), self.cloud_point[index], 3)
            coords = self.shift_and_transform_coords(cyl_coords=cyl_coords)
            # print(f'coords: {coords}')
            self.cloud_point[index] = coords
            # print(f' x: {coords[0]} y: {coords[1]}')
            # if (coords[0] > 5 or coords[0] < -5) and (coords[1] > 5 or coords[1] < -5):
            pygame.draw.circle(self.window, (0,0,255),(self.x_size/2,self.y_size/2), 10)
            pygame.draw.circle(self.window, (255,255,255), coords, 3)
        if time.time() - self.last_update  > (1.0/float(FPS)):
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

lidar_value = ''
max_lidar_value = 0
min_lidar_value = 1000

window = Window(1000,1000)
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
    # print(cloud_point.get_points_distances())
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