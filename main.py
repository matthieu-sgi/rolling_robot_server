import pygame
# from serial_client import SerialClient
from tcp_server import TcpServer
from lidar import LidarCloudPoint
from display import Window

# FIXME: time for debugging
import time

# serial_client = SerialClient()
tcp_server = TcpServer('', 3000)
cloud_point = LidarCloudPoint()
window = Window(cloud_point,1000,1000)

# serial_client.stop()
KEY_TO_MSG = {
    pygame.K_UP : "u",
    pygame.K_DOWN : "d",
    pygame.K_RIGHT : "r",
    pygame.K_LEFT : "l",
    pygame.K_SPACE : "t"
}

old_time = time.time()
while True:
    try:
        data_array = tcp_server.receive()
        print(data_array)
        # new_time = time.time()
        # print(new_time - old_time)
        # old_time = new_time
        cloud_point.ingest_frame(data_array)
        window.update_from_cloud_point()
        for event in pygame.event.get():
    
            # if event object type is QUIT
            # then quitting the pygame
            # and program both.
            if event.type == pygame.QUIT:
    
                # deactivates the pygame library
                pygame.quit()
    
                # quit the program.
                quit()
                serial_client.stop()
            if event.type == pygame.KEYDOWN:
                if event.key in KEY_TO_MSG.keys():
                    print(f'sending key : {KEY_TO_MSG[event.key]}')
                    serial_client.send_message(KEY_TO_MSG[event.key])

    except KeyboardInterrupt:
        pygame.quit()
        serial_client.stop()
        quit()