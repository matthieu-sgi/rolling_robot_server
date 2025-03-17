import numpy as np
import queue
#FIXME: debug purpose
import time
import threading

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
    
    LIDAR_RESOLUTION = 0.8
    serial_protocol_translation = {
    "sa" : "start angle",
    "nbv" : "number of values",
    "X" : "value index with value",
    "ea" : "end angle"
    }

    def __init__(self, receiving_queue : queue.Queue):
        self.start_angle = None
        self.nb_value = None
        self.number_of_points = int(360 / LidarCloudPoint.LIDAR_RESOLUTION)
        print(f'number of points : {self.number_of_points}')
        self.points_distances = np.zeros(self.number_of_points, dtype=np.float32) # Number of value of one rotation
        self.points_angles = np.zeros(self.number_of_points, dtype=np.float32) # Number of value of one rotation
        self.nb_value = 12
        self.end_angle = None
        self.old_time = time.time()
        self.receiving_queue = receiving_queue
        # self.delta_angle = None
        #TODO: implement threading
        # self.start()
    
    def start(self) -> None:
        self.run = True
        self.thread = threading.Thread(target=self._ingest_thread)
        self.thread.start()

    def _ingest_thread(self) -> None:
        while self.run:
            data = self.receiving_queue.get(block=True)
            self.ingest_frame(data)

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
            #print(f'data : {data} | counter : {counter}')
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
                    #print(f'appending value : {value}')
                    self.pre_formatted_distances.append(float(value/1000.0))
                
            
            if counter == len(frame) -1 :
                if key != 'ea':
                    print("Incorrect frame")
                    return False
                else:
                    self.end_angle = float(value/100.0)

        return True
        
    def ingest_frame(self, frame: bytes):
        if frame == None:
            return
        frame = frame[:-1] # remove the '\n' at the end of frame
        data_array = frame.decode(encoding='ascii').split(' ')
        # print(data_array)
        self.pre_formatted_distances = []
        if self.check_frame_integrity_and_format(data_array):
            resolution = LidarCloudPoint.LIDAR_RESOLUTION

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
        # new_time = time.time()
        # print(new_time - self.old_time)
        # self.old_time = new_time