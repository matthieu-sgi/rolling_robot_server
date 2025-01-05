import pygame
import serial
import os
pygame.init()
# pygame.display.init()
# display = pygame.display.set_mode((400,400))

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
    def __init__(self, start_angle : int, nb_value : int):
        self.start_angle = start_angle
        self.nb_value = nb_value
        self.points = []
    def 

lidar_value = ''
max_lidar_value = 0
min_lidar_value = 1000
while True:
    # next_byte = ser.read(1)#.decode('ascii')#.split('\r\n')
    next_byte = ser.readlines(1)#.decode('ascii')#.split('\r\n')
    print(next_byte)
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