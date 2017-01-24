import numpy as np
import heapq as hp
import random as rand
import passenger as ps
import matplotlib.pyplot as plt

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

    # print("Jump! Jump! Jump!")
    # Priority queue rebalance
    # if len(jqueue_list) > 0:
    #     print(len(jqueue_list))
    if len(outside_queue) > 0:
        jqueue_list.extend(outside_queue)
    j_priority_queue = hp.nsmallest(len(jqueue_list), jqueue_list, key=lambda s: s.duration)
    # if len(j_priority_queue) > 0:
        # print(len(j_priority_queue))
    queue[0:0] = j_priority_queue
    return queue

def if_all_working(officer):
    # Tell whether existing at least one officer free
    for i in list(range(0, len(officer), 1)):
        if officer[i] is None:
            return False, i
    return True, -1

def serve_MMS(officer, queue, clock, mean_A, stage_B=-1, cnt_milimeter=-1, cnt_x_ray=-1, tagtime_per_box=-1):
    # Serve the passenger with the M/M/s System Principle
    while True:
        if len(queue) == 0:
            return
        state, index = if_all_working(officer)
        if state is True:
            break
        else:
            if stage_B == -1:
                queue[0].service_A_start = clock
                queue[0].service_A_duration = reject_zero(round(data_generator(mean_A, 1, single=1)))
            else:
                queue[0].service_B_start = clock
                mu_mili = data_generator(mean_A, 1, single=1)
                mu_x_ray = data_generator(stage_B, 1, single=1)
                mu_tagtime = 0
                for i in range(queue[0].num_boxes):
                    mu_tagtime += data_generator(tagtime_per_box, 1, single=1)

                mu_B = reject_zero(
                    round(max(mu_mili / cnt_milimeter, (queue[0].num_boxes * mu_x_ray) / cnt_x_ray) + mu_tagtime))
                # print(mu_B)
                queue[0].service_B_duration = mu_B
            officer[index] = queue[0]
            queue.remove(queue[0])

# @ 插队还没有加入
def stageA(clock, arrival_list_precheck, stageA_precheck, stageA_precheck_officer, stageB_precheck, mean_A, time_limit):
    # Run the stage-A operation, arrival_list_precheck is increasing for each sublist
    # Basic Workflow here: Check Serve => New Arrival => Check Jump Queue Case => Serve New
    # print("In Stage A")
    # Check the Current Served Passenger status:
    for i in list(range(0, len(stageA_precheck_officer), 1)):
        if stageA_precheck_officer[i] is not None:
            j = stageA_precheck_officer[i]
            i_A_end = j.service_A_start + j.service_A_duration
            # print("======> i_A_end: " + str(i_A_end))
            # print("======> depart_time: " + str(j.depart_time))
            if i_A_end < clock:
                print("Clock Counting Wrong!")
                return
            if i_A_end == clock:
                # print("Enter B: " + str(i_A_end))
                stageB_precheck.append(stageA_precheck_officer[i])
                stageA_precheck_officer[i] = None

    # Add the newly arrivals to stageA_precheck at clock:
    test_cnt = 0
    outside_queue = []
    for j in arrival_list_precheck[:]:
        if j.arrival_time == clock:
            # 插队加在这里
            test_cnt += 1
            j.duration = j.depart_time - j.arrival_time
            if j.duration <= time_limit:
                outside_queue.append(j)
            else:
                stageA_precheck.append(j)
            arrival_list_precheck.remove(j)
            # print("!!!!!!!!!!!!!!!!!Someone come!!!!")
        if j.arrival_time > clock:
            break

    # Check the Jump Queue case:
    stageA_precheck = jqueue(stageA_precheck, clock, time_limit, outside_queue)

    # stageA_precheck needs to maintain a working status for each officer, and figure out a way how to deal with the randomly generated service time
    # Serve coming passengers in stage A at clock:
    serve_MMS(stageA_precheck_officer, stageA_precheck, clock, mean_A)
    return test_cnt

def stageB(clock, stageB_precheck, stageB_precheck_pane, mean_C, mean_D, total_time_scale, p_unsafe_rate_precheck, Milimeter_scan_time, X_ray_scan_time, cnt_milimeter, cnt_x_ray, tagtime_per_box):
    # Run the stage-B operation
    # Basic Workflow: Check Serve => Serve New
    # print("In Stage B")
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
                if j.exit_time <= total_time_scale and j.exit_time <= j.depart_time:
                    finish_list.append(j.exit_time - j.arrival_time)
                stageB_precheck_pane[i] = None

    # Serve coming passengers in stage B at clock:
    serve_MMS(stageB_precheck_pane, stageB_precheck, clock, Milimeter_scan_time, X_ray_scan_time, cnt_milimeter, cnt_x_ray, tagtime_per_box)

    return finish_list



# @arrival_list_precheck stores the list of object passenger
def airport(arrival_list_precheck, arrival_list_regular, num_hour, time_limit, total_passenger, cnt_officer_precheck, cnt_officer_regular, cnt_pane_precheck, ratio_regular_over_precheck, mean_A, mean_C, mean_D, p_unsafe_rate_precheck, p_unsafe_rate_regular, Milimeter_scan_time, X_ray_scan_time, cnt_milimeter, cnt_x_ray, tagtime_per_box):
    # The outer function to run the simulation
    # arrival_list_precheck:
    # [[], [], ...]:    [precheck_officer_1, ..._2, ......] 每一个precheck_officer都对应一个arrival list
    clock = 0
    cnt_finished_passenger = 0
    total_time_scale = num_hour * 3600      # Unit [s] Seconds for all the time variable involved here

    # Initialize all the queues
    stageA_precheck = []
    stageA_regular  = []
    stageB_precheck = []
    stageB_regular  = []

    # Initialize all the officer working status
    stageA_precheck_officer = init_queue_list(cnt_officer_precheck, 1)
    stageA_regular_officer = init_queue_list(cnt_officer_regular, 1)
    stageB_precheck_pane = init_queue_list(cnt_pane_precheck, 1)
    stageB_regular_pane = init_queue_list(cnt_pane_precheck * ratio_regular_over_precheck, 1)

    # print("In Airport")

    final_finish_list = []
    ttt = 0
    while True:
        # print("===> Clock: " + str(clock))
        if cnt_finished_passenger == total_passenger or clock == total_time_scale:
            break;
        test_cnt_precheck = stageA(clock, arrival_list_precheck, stageA_precheck, stageA_precheck_officer, stageB_precheck, mean_A/cnt_officer_precheck, time_limit)
        test_cnt_regular = stageA(clock, arrival_list_regular, stageA_regular, stageA_regular_officer, stageB_regular, mean_A/cnt_officer_regular, time_limit)
        finish_list_precheck = stageB(clock, stageB_precheck, stageB_precheck_pane, mean_C, mean_D, total_time_scale, p_unsafe_rate_precheck, Milimeter_scan_time/cnt_pane_precheck, X_ray_scan_time/cnt_pane_precheck, cnt_milimeter, cnt_x_ray, tagtime_per_box)
        finish_list_regular = stageB(clock, stageB_regular, stageB_regular_pane, mean_C, mean_D, total_time_scale, p_unsafe_rate_regular, Milimeter_scan_time/(cnt_pane_precheck*ratio_regular_over_precheck), X_ray_scan_time/(cnt_pane_precheck*ratio_regular_over_precheck), cnt_milimeter, cnt_x_ray, tagtime_per_box)
        clock += 1
        final_finish_list.append(finish_list_precheck)
        final_finish_list.append(finish_list_regular)
        cnt_finished_passenger += (len(finish_list_precheck) + len(finish_list_regular))
        ttt += (test_cnt_precheck + test_cnt_regular)

    # print(cnt_finished_passenger)
    # length_precheck = 0
    # for i in stageB_precheck:
    #     length_precheck += len(i)
    # length_regular = 0
    # for i in stageB_regular:
    #     length_regular += len(i)

    # print(length_precheck)
    # print(length_regular)
    # print(ttt)
    return final_finish_list, cnt_finished_passenger


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
    # l = init_queue_list(cnt_officer)
    l = []
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
        l.append(tmp_passgr)
        # enqueue_shortest(l, tmp_passgr)

    l = hp.nsmallest(len(l), l, key=lambda s: s.arrival_time)
    return l


# Auxiliary function to print all passenger info in the list l
def print_all(l):
    for i in list(range(0, len(l), 1)):
        for j in list(range(0, len(l[i]), 1)):
            print(l[i][j], end=";\t")
        print()


def get_histogram(dataset, title, xlabel):
    plt.hist(dataset, bins=30, normed=1, edgecolor='white')
    plt.title(title + " Distribution")
    plt.xlabel(xlabel)
    plt.ylabel("Probability density")  # pdf = n/(Total*bin_scale)
    plt.grid(True)
    plt.show()


def overall_mean_variance(iteration, TSA_precheck_arrival_time, Regular_arrival_time, num_flight, flight_gap_time, total_passenger, p_precheck_rate, k_average_box_precheck, k_average_box_regular, cnt_officer_precheck, cnt_officer_regular, num_hour, time_limit, cnt_pane_precheck, ratio_regular_over_precheck, mean_A, mean_C, mean_D, p_unsafe_rate_precheck, p_unsafe_rate_regular, Milimeter_scan_time, X_ray_scan_time, cnt_milimeter, cnt_x_ray, tagtime_per_box):
    mean_list = []
    variance_list = []
    ttt_list = []
    for i in range(iteration):
        print("Current-iteration #: " + str(i))
        arrival_list_precheck = get_arrival_list(TSA_precheck_arrival_time, num_flight, flight_gap_time,
                                                 total_passenger * p_precheck_rate, k_average_box_precheck,
                                                 cnt_officer_precheck, num_hour)
        arrival_list_regular = get_arrival_list(Regular_arrival_time, num_flight, flight_gap_time,
                                                total_passenger * (1 - p_precheck_rate), k_average_box_regular,
                                                cnt_officer_regular, num_hour)
        # print_all(arrival_list_precheck)

        # Run the Simulation
        result_list, ttt = airport(arrival_list_precheck, arrival_list_regular, num_hour, time_limit, total_passenger,
                              cnt_officer_precheck, cnt_officer_regular, cnt_pane_precheck, ratio_regular_over_precheck,
                              mean_A, mean_C, mean_D, p_unsafe_rate_precheck, p_unsafe_rate_regular,
                              Milimeter_scan_time, X_ray_scan_time, cnt_milimeter, cnt_x_ray, tagtime_per_box)
        ttt_list.append(ttt/total_passenger)
        # Merge all the sublists:
        result = [x for j in result_list for x in j]
        # print("Finish Amount: " + str(len(result)))
        # print(result)
        # print(max(result))
        if iteration == 1:
            title, xlabel = str(total_passenger) + " Passengers Waiting Time", "Waiting Time [s]"
            get_histogram(result, title, xlabel)

        mean, variance = get_mean_variance(result)
        mean_list.append(mean)
        variance_list.append(variance)

    mean, variance, ttt = get_mean_variance(mean_list), get_mean_variance(variance_list), get_mean_variance(ttt_list)
    print("====================================================================================")
    print("# Total Iteration: " + str(iteration))
    print("Final Mean: " + str(mean[0]))
    print("Final Variance: " + str(variance[0]))
    print("Final PASS Rate: " + str(ttt[0]*100) + "%")


# Global Parameters Declaration
num_hour = 12               # hours
total_passenger = 3000
time_limit = 20 * 60        # seconds
flight_gap_time = 0.5       # hours
num_flight = num_hour/flight_gap_time

TSA_precheck_arrival_time   = 9.18947
Regular_arrival_time        = 12.94478
mean_A                      = 11.226875
Milimeter_scan_time         = 11.6372
X_ray_scan_time             = 6.64846
Fetch_scanned_items_time    = 28.62069

mean_C                      = 30
mean_D                      = 60/0.29
cnt_officer_precheck        = 2
cnt_officer_regular         = 5
ratio_regular_over_precheck = 3
cnt_pane_precheck           = 1
cnt_milimeter               = 1
cnt_x_ray                   = 1
p_precheck_rate             = 0.45
p_unsafe_rate_precheck      = 0.02
p_unsafe_rate_regular       = 0.05
k_average_box_precheck      = 2
k_average_box_regular       = 4

# New Feature:
tagtime_per_box             = 1.3
k_average_box_precheck      = 3
k_average_box_regular       = 3
cnt_milimeter               = 3
cnt_x_ray                   = 5

iteration = 10
overall_mean_variance(iteration, TSA_precheck_arrival_time, Regular_arrival_time, num_flight, flight_gap_time, total_passenger, p_precheck_rate, k_average_box_precheck, k_average_box_regular, cnt_officer_precheck, cnt_officer_regular, num_hour, time_limit, cnt_pane_precheck, ratio_regular_over_precheck, mean_A, mean_C, mean_D, p_unsafe_rate_precheck, p_unsafe_rate_regular, Milimeter_scan_time, X_ray_scan_time, cnt_milimeter, cnt_x_ray, tagtime_per_box)

