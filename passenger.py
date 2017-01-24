import numpy as np
import heapq as hp

class passenger(object):
    """
        Passenger Class
    """
    depart_time     = 0
    arrival_time    = 0
    num_boxes       = 0

    exit_time       = 0
    duration            = 0
    service_A_start     = 0
    service_B_start     = 0
    service_C_start     = 0
    service_D_start     = 0
    service_A_duration  = 0
    service_B_duration  = 0
    service_C_duration  = 0
    service_D_duration  = 0

    def __init__(self, depart_time, arrival_time, num_boxes):
        self.depart_time = depart_time
        self.arrival_time = arrival_time
        self.num_boxes = num_boxes

    def __str__(self):
        return str(self.depart_time) + "\t\t\t" + str(self.arrival_time) + "\t\t" + str(self.num_boxes)

