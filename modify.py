import numpy as np
import heapq as hp
import random as rand
import passenger as ps

def reject_zero(l):
    if l == 0:
        return 1
    else:
        return l

def exp_distrib_generator(mean, lower_bound):
    # Generate the simulation data based on the exponential distribution
    # lamda:        arrival/service rate
    # lower_bound:  -1 if not needed
    sample = np.random.exponential(mean)

    if lower_bound != -1 and sample < lower_bound:
        return exp_distrib_generator(lamda, lower_bound)
    else:
        return sample


def data_generator(mean, size, lower_bound=-1, single=0):
    if single == 1:
        return exp_distrib_generator(mean, lower_bound)
    l = []
    for i in range(size):
        tmp = exp_distrib_generator(mean, lower_bound)
        l.append(tmp)
    return l


def init_queue_list(cnt, officer=-1):
    # Initialize the queue
    total_queue = []
    if officer == -1:
        for i in range(cnt):
            tmp = []
            total_queue.append(tmp)
    else:
        for i in range(cnt):
            tmp = None
            total_queue.append(tmp)
    return total_queue


def enqueue_shortest(total_queue, passgr):
    if len(total_queue) <= 0:
        print("Nothing in the queue!")
        return
    shortest = total_queue[0]
    for i in list(range(1, len(total_queue), 1)):
        if len(total_queue[i]) < len(shortest):
            shortest = total_queue[i]
    shortest.append(passgr)


# @Remember to add the case when the jqueue person is outside the queue
def jqueue(queue, clock, time_limit, outside_queue):
    # Rebalance the queue [one queue without queue exchange] with the jumping queue mechanism
    jqueue_list = []
    for i in queue:
        i.duration = i.depart_time - clock
        if i.duration <= time_limit:
            jqueue_list.append(i)

    for i in jqueue_list:
        queue.remove(i)

    # Priority queue rebalance
    jqueue_list.extend(outside_queue)
    j_priority_queue = hp.nsmallest(len(jqueue_list), jqueue_list, key=lambda s: s.duration)
    queue[0:0] = j_priority_queue
    return queue

# @ 插队还没有加入
def stageA(clock, arrival_list_precheck, stageA_precheck, stageA_precheck_officer, stageB_precheck, mean_A):
    # Run the stage-A operation, arrival_list_precheck is increasing for each sublist
    # Basic Workflow here: Check Serve => New Arrival => Serve New
    print("In Stage A")
    # Check the Current Served Passenger status:
    for i in list(range(0, len(stageA_precheck_officer), 1)):
        if stageA_precheck_officer[i] is not None:
            j = stageA_precheck_officer[i]
            i_A_end = j.service_A_start + j.service_A_duration
            print("======> i_A_end: " + str(i_A_end))
            print("======> depart_time: " + str(j.depart_time))
            if i_A_end < clock:
                print("Clock Counting Wrong!")
                return
            if i_A_end == clock:
                print("Enter B: " + str(i_A_end))
                enqueue_shortest(stageB_precheck, stageA_precheck_officer[i])
                stageA_precheck_officer[i] = None

    # Add the newly arrivals to stageA_precheck at clock:
    test_cnt = 0
    for i in list(range(0, len(arrival_list_precheck), 1)):
        for j in arrival_list_precheck[i][:]:
            if j.arrival_time == clock: # add the case when <= since the arrival time may be the same
                # 插队加在这里
                stageA_precheck[i].append(j)
                arrival_list_precheck[i].remove(j)
                print("!!!!!!!!!!!!!!!!!Someone come!!!!")
                test_cnt += 1
                # break
            if j.arrival_time > clock:
                break

    # stageA_precheck needs to maintain a working status for each officer, and figure out a way how to deal with the randomly generated service time
    # Serve coming passengers in stage A at clock:
    for i in list(range(0, len(stageA_precheck), 1)):
        if len(stageA_precheck[i]) > 0 and stageA_precheck_officer[i] is None:
            stageA_precheck_officer[i] = stageA_precheck[i][0]
            stageA_precheck_officer[i].service_A_start = clock
            stageA_precheck_officer[i].service_A_duration = reject_zero(round(data_generator(mean_A, 1, single=1)))
            print("Duration_A: " + str(stageA_precheck_officer[i].service_A_duration))
            stageA_precheck[i].remove(stageA_precheck[i][0])
    return test_cnt


def stageB(clock, stageB_precheck, stageB_precheck_pane, mean_C, mean_D, total_time_scale, mean_B, p_unsafe_rate_precheck, Milimeter_scan_time, X_ray_scan_time, cnt_milimeter, cnt_x_ray):
    # Run the stage-B operation
    # Basic Workflow: Check Serve => Serve New
    print("In Stage B")
    #  Check the Current Served Passenger status:
    finish_list = []
    for i in list(range(0, len(stageB_precheck_pane), 1)):
        if stageB_precheck_pane[i] is not None:
            j = stageB_precheck_pane[i]
            i_B_end = j.service_B_start + j.service_B_duration
            if i_B_end < clock:
                print("Clock Counting Wrong!")
                return
            if i_B_end == clock:
                random_safe_rate = rand.random()
                safe = (random_safe_rate > p_unsafe_rate_precheck)
                if safe is True:
                    j.service_C_start = clock
                    j.service_C_duration = reject_zero(round(data_generator(mean_C, 1, single=1)))
                    j.exit_time = j.service_C_start + j.service_C_duration
                else:
                    j.service_D_start = clock
                    j.service_D_duration = reject_zero(round(data_generator(mean_D, 1, single=1)))
                    j.exit_time = j.service_D_start + j.service_D_duration

                # !!!!!! total_time_scale is the finish time for the simulation, and we reject those who finish the safety check part excess this time
                if j.exit_time <= total_time_scale:
                    finish_list.append(j.exit_time - j.arrival_time)
                stageB_precheck_pane[i] = None

    # Serve coming passengers in stage B at clock:
    for i in list(range(0, len(stageB_precheck), 1)):
        if len(stageB_precheck[i]) > 0 and stageB_precheck_pane[i] is None:
            stageB_precheck_pane[i] = stageB_precheck[i][0]
            stageB_precheck_pane[i].service_B_start = clock
            mu_mili = data_generator(Milimeter_scan_time, 1, single=1)
            mu_x_ray = data_generator(X_ray_scan_time, 1, single=1)
            mu_B = reject_zero(round(min(cnt_milimeter*mu_mili, (cnt_x_ray*mu_x_ray)/stageB_precheck_pane[i].num_boxes)))
            print(mu_B)
            stageB_precheck_pane[i].service_B_duration = mu_B
            stageB_precheck[i].remove(stageB_precheck[i][0])

    return finish_list



# @arrival_list_precheck stores the list of object passenger
def airport(arrival_list_precheck, arrival_list_regular, num_hour, time_limit, total_passenger, cnt_officer_precheck, cnt_officer_regular, cnt_pane_precheck, ratio_regular_over_precheck, mean_A, mean_B_precheck, mean_B_regular, mean_C, mean_D, p_unsafe_rate_precheck, p_unsafe_rate_regular, Milimeter_scan_time, X_ray_scan_time, cnt_milimeter, cnt_x_ray):
    # The outer function to run the simulation
    # arrival_list_precheck:
    # [[], [], ...]:    [precheck_officer_1, ..._2, ......] 每一个precheck_officer都对应一个arrival list
    clock = 0
    cnt_finished_passenger = 0
    total_time_scale = num_hour * 3600      # Unit [s] Seconds for all the time variable involved here

    # Initialize all the queues
    stageA_precheck = init_queue_list(cnt_officer_precheck)
    stageA_regular  = init_queue_list(cnt_officer_regular)
    stageB_precheck = init_queue_list(cnt_pane_precheck)
    stageB_regular  = init_queue_list(cnt_pane_precheck * ratio_regular_over_precheck)

    # Initialize all the officer working status
    stageA_precheck_officer = init_queue_list(cnt_officer_precheck, 1)
    stageA_regular_officer = init_queue_list(cnt_officer_regular, 1)
    stageB_precheck_pane = init_queue_list(cnt_pane_precheck, 1)
    stageB_regular_pane = init_queue_list(cnt_pane_precheck * ratio_regular_over_precheck, 1)

    print("In Airport")

    final_finish_list = []
    ttt = 0
    while True:
        print("===> Clock: " + str(clock))
        if cnt_finished_passenger == total_passenger or clock == total_time_scale:
            break;
        test_cnt_precheck = stageA(clock, arrival_list_precheck, stageA_precheck, stageA_precheck_officer, stageB_precheck, mean_A)
        test_cnt_regular = stageA(clock, arrival_list_regular, stageA_regular, stageA_regular_officer, stageB_regular, mean_A)
        finish_list_precheck = stageB(clock, stageB_precheck, stageB_precheck_pane, mean_C, mean_D, total_time_scale, mean_B_precheck, p_unsafe_rate_precheck, Milimeter_scan_time, X_ray_scan_time, cnt_milimeter, cnt_x_ray)
        finish_list_regular = stageB(clock, stageB_regular, stageB_regular_pane, mean_C, mean_D, total_time_scale, mean_B_regular, p_unsafe_rate_regular, Milimeter_scan_time, X_ray_scan_time, cnt_milimeter, cnt_x_ray)
        clock += 1
        final_finish_list.append(finish_list_precheck)
        final_finish_list.append(finish_list_regular)
        cnt_finished_passenger += (len(finish_list_precheck) + len(finish_list_regular))
        ttt += (test_cnt_precheck + test_cnt_regular)

    # print(cnt_finished_passenger)
    length_precheck = 0
    for i in stageB_precheck:
        length_precheck += len(i)
    length_regular = 0
    for i in stageB_regular:
        length_regular += len(i)

    print(length_precheck)
    print(length_regular)
    print(ttt)
    return final_finish_list


def get_mean_variance(total_waiting_time_list):
    # Get the mean & variance value for the waiting time overall all the passengers
    numpy_arr = np.array(total_waiting_time_list)
    mean = np.mean(numpy_arr)
    variance = np.var(numpy_arr)
    return mean, variance

def get_rand_int_range(lower, upper):
    tmp_arrival_time = rand.randint(round(lower * 3600), round(upper * 3600))
    return tmp_arrival_time

def reject_sample_arrival_time(depart_time, total_time_scale):
    tmp_arrival_time = 0
    choice = rand.random()
    if choice < 0.84:
        tmp_arrival_time = get_rand_int_range(0.5, 2)
    elif choice >= 0.84 and choice < 0.9:
        tmp_arrival_time = get_rand_int_range(2, 2.5)
    elif choice >= 0.9 and choice < 0.95:
        tmp_arrival_time = get_rand_int_range(2.5, 3)
    else:
        tmp_arrival_time = get_rand_int_range(0, 0.5)

    if depart_time - tmp_arrival_time < 0:
        return reject_sample_arrival_time(depart_time, total_time_scale)
    else:
        return tmp_arrival_time


# 给定原先的arrival rate，按什么方式把客流排进cnt个队列 【按人少的排进去】
# 航班起飞时间的分布
def get_arrival_list(mean_arrival_time, num_flight, flight_gap_time, total_passenger, mean_num_boxes, cnt_officer, num_hour):
    l = init_queue_list(cnt_officer)
    arrival_time = 0
    total_time_scale = num_hour * 3600
    for i in range(round(total_passenger)):
        flight_id   = rand.randint(1, num_flight)
        depart_time = flight_id * (round(flight_gap_time*3600))

        # Reject Sampling
        tmp_arrival_time = reject_sample_arrival_time(depart_time, total_time_scale)
        arrival_time = depart_time - tmp_arrival_time

        num_boxes = reject_zero(round(data_generator(mean_num_boxes, 1, single=1)))
        tmp_passgr = ps.passenger(depart_time, arrival_time, num_boxes)
        enqueue_shortest(l, tmp_passgr)

    for i in list(range(0, len(l), 1)):
        l[i] = hp.nsmallest(len(l[i]), l[i], key=lambda s: s.arrival_time)
    return l

# Auxiliary function to print all passenger info in the list l
def print_all(l):
    for i in list(range(0, len(l), 1)):
        for j in list(range(0, len(l[i]), 1)):
            print(l[i][j], end=";\t")
        print()


# Global Parameters Declaration
num_hour = 12            # hours
total_passenger = 5000
time_limit = 20 * 60        # seconds
flight_gap_time = 0.5       # hours
num_flight = num_hour/flight_gap_time

TSA_precheck_arrival_time   = 9.18947
Regular_arrival_time        = 12.94478
mean_num_boxes              = 3
mean_A  = 11.226875
Milimeter_scan_time         = 11.6372
X_ray_scan_time             = 6.64846
Fetch_scanned_items_time    = 28.62069

cnt_officer_precheck        = 2
cnt_officer_regular         = 5
ratio_regular_over_precheck = 3
cnt_pane_precheck           = 1
cnt_milimeter   = 1
cnt_x_ray       = 1

p_precheck_rate         = 0.45
p_unsafe_rate_precheck  = 0.02
p_unsafe_rate_regular   = 0.05

arrival_list_precheck = get_arrival_list(TSA_precheck_arrival_time, num_flight, flight_gap_time, total_passenger*p_precheck_rate, mean_num_boxes, cnt_officer_precheck, num_hour)
arrival_list_regular = get_arrival_list(Regular_arrival_time, num_flight, flight_gap_time, total_passenger*(1-p_precheck_rate), mean_num_boxes, cnt_officer_regular, num_hour)
# print_all(arrival_list_precheck)

k_average_box_precheck  = 2
k_average_box_regular   = 4

mean_C        = 30
variance_C    = mean_C**2
mean_D        = 60/0.29
variance_D    = mean_D**2

mean_B_precheck = 17.522744667037923
mean_B_regular = 28.829509786879964

# Run the Simulation
result_list = airport(arrival_list_precheck, arrival_list_regular, num_hour, time_limit, total_passenger, cnt_officer_precheck, cnt_officer_regular, cnt_pane_precheck, ratio_regular_over_precheck, mean_A, mean_B_precheck, mean_B_regular, mean_C, mean_D, p_unsafe_rate_precheck, p_unsafe_rate_regular, Milimeter_scan_time, X_ray_scan_time, cnt_milimeter, cnt_x_ray)
# Merge all the sublists:
result = [x for j in result_list for x in j]
print("Finish Amount: " + str(len(result)))
print(result)
mean, variance = get_mean_variance(result)
print("Final Mean: " + str(mean))
print("Final Variance: " + str(variance))