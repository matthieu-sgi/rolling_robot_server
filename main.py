import pygame
import serial
import os
import math

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
        self.points = []
        self.nb_value = None
        self.end_angle = None
        # self.delta_angle = None

    def __getitem__(self, index: int):
        return self.points[index]
    
    def __setitem__(self, index: int, value: LidarPoint):
        self.points[index] = value
    
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

            delta_angle = None
            if self.start_angle > self.end_angle:
                delta_angle = (36000 - self.start_angle) + self.end_angle
            else:
                delta_angle = self.end_angle - self.start_angle

            resolution = delta_angle / self.nb_value

            for i in range(self.nb_value):
                point_angle = self.start_angle + resolution*i
                if point_angle > 36000:
                    point_angle -= 36000
                self.points.append(LidarPoint(angle=point_angle, distance=distances[i]))

class Window:

    def __init__(self, x_size : int, y_size: int):
        pygame.init()
        pygame.display.init()
        self.x_size = x_size
        self.y_size = y_size
        self.window = pygame.display.set_mode((self.x_size,self.y_size))

    def update(self):
        pygame.display.update()
    

    def cylindrical_coords_to_cartesian(self, theta, r):
        return (r*math.cos(theta), r*math.sin(theta))

lidar_value = ''
max_lidar_value = 0
min_lidar_value = 1000

window = Window(200,400)

while True:
    # next_byte = ser.read(1)#.decode('ascii')#.split('\r\n')
    # next_frame = ser.readlines(1)#.decode('ascii')#.split('\r\n')
    next_frame = ser.read_until(b"\n")#.decode('ascii')#.split('\r\n')
    cloud_point = LidarCloudPoint()
    cloud_point.ingest_frame(next_frame)


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