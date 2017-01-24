import matplotlib.pyplot as plt
import numpy as np
import math

from sympy import *
from scipy.special import gamma

# Function in Stage A
def steady_state_prob(lamda, mu, n):
    frac = lamda / mu
    if n == 0:
        return 1- frac
    else:
        return math.pow(frac, n) * (1-frac)

def exp_distrib(x, k, mu):
    if k == 0:
        return 0

    part_1 = (mu**k) * (x**(k-1)) * exp(-mu * x)
    part_2 = math.factorial(k-1)
    return part_1/part_2

def get_integral(x, k, mu, power):
    x = Symbol('x')
    y = exp_distrib(x, k, mu) * (x**power)
    return integrate(y, (x, 0, oo))

def get_variance(mu, lamda):
    x = Symbol('x')
    iteration = 1000
    result = 0
    for i in range(iteration):
        integral_1 = get_integral(x, i, mu, 2)
        integral_2 = get_integral(x, i, mu, 1)
        integrap_diff = integral_1 - integral_2**2
        result += steady_state_prob(lamda, mu, i) * integrap_diff
    return result

# Function in Stage B
def get_service_rate(n1, n2, mu1, mu2, k):
    """
    :param n1: # of milimeter in one module
    :param n2: # of x-ray in one module
    :param mu1: rate of milimeter
    :param mu2: rate of x-ray
    :param k: average number of boxes to carry item
    :return: service rate
    """
    milimeter = n1 * mu1
    x_ray = (n2 * mu2)/ k
    # print("milimeter: "+str(milimeter))
    # print("x_ray: "+str(x_ray))
    return min(milimeter, x_ray)

# Function to get the waiting time info
def get_waitime_info(mu, lamda):
    mean = 1 / (mu - lamda)
    print("Mean:\t\t" + str(mean))
    variance = get_variance(mu, lamda)
    print("Variance:\t" + str(variance))
    stand_dev = math.sqrt(variance)
    print("Standard Dev:\t" + str(stand_dev))
    return mean, variance, stand_dev


# Run the Simulation
"""
    lamda:                          arrival rate of the passengers in Stage A & B
    mu:                             service rate of an officer in Stage A
    k_people_in_system:             number of people in the system
    k_average_box:                  average number of boxes to carry item
    officer_cnt:                    number of officers in Stage A
"""
# Given Data (Fetch from Minitab with exponential regression)
# Unit: [s] seconds
TSA_precheck_arrival_time   = 9.18947
Regular_arrival_time        = 12.94478
ID_check_mean_service_time  = 11.226875
Milimeter_scan_time         = 11.6372
X_ray_scan_time             = 6.64846
Fetch_scanned_items_time    = 28.62069

# Features we apply
cnt_officer_precheck        = 2
cnt_officer_regular         = 5
ratio_regular_over_precheck = 3
cnt_milimeter   = 1
cnt_x_ray       = 1

p_precheck_rate         = 0.45
p_unsafe_rate_precheck  = 0.02
p_unsafe_rate_regular   = 0.05
lamda_precheck_A    = 1 / (TSA_precheck_arrival_time * cnt_officer_precheck)
lamda_regular       = 1 / (Regular_arrival_time * cnt_officer_regular)
lamda_precheck_B    = lamda_precheck_A/ratio_regular_over_precheck

mu_milimeter    = 1/Milimeter_scan_time
mu_x_ray        = 1/X_ray_scan_time
k_average_box_precheck  = 2
k_average_box_regular   = 4

mu_A            = 1/ID_check_mean_service_time
mu_B_precheck   = get_service_rate(cnt_milimeter, cnt_x_ray, mu_milimeter, mu_x_ray, k_average_box_precheck)
mu_B_regular    = get_service_rate(cnt_milimeter, cnt_x_ray, mu_milimeter, mu_x_ray, k_average_box_regular)

# Calculation and the output result
print("Stage A:")
print("Precheck-Passenger Info [Waiting Time]:")
mean_A_precheck, variance_A_precheck, stand_dev_A_precheck = get_waitime_info(mu_A, lamda_precheck_A)
print("Regular-Passenger Info [Waiting Time]:")
mean_A_regular, variance_A_regular, stand_dev_A_regular = get_waitime_info(mu_A, lamda_regular)

print("=============================================================")
print("Stage B:")
print("Precheck-Passenger Info [Waiting Time]:")
mean_B_precheck, variance_B_precheck, stand_dev_B_precheck = get_waitime_info(mu_B_precheck, lamda_precheck_B)
print("Regular-Passenger Info [Waiting Time]:")
mean_B_regular, variance_B_regular, stand_dev_B_regular = get_waitime_info(mu_B_regular, lamda_regular)


# Stage C & D:
# mean = 1/lamda
mean_C        = 30
variance_C    = mean_C**2
mean_D        = 60/0.29
variance_D    = mean_D**2

print("=============================================================")
print("Stage C:")
print("Mean [Waiting Time]: " + str(mean_C))
print("Variance [Waiting Time]: " + str(variance_C))
print("Standard Dev: " + str(mean_C))
print("=============================================================")
print("Stage D:")
print("Mean [Waiting Time]: " + str(mean_D))
print("Variance [Waiting Time]: " + str(variance_D))
print("Standard Dev: " + str(mean_D))

print("=============================================================")
print("Final Result:")

# Test:
# mean_B_precheck = 1/(mu_B_precheck - lamda_precheck_B)
# print("Mean_precheck_B:\t\t" + str(mean_B_precheck))
# mean_B_regular = 1/(mu_B_regular - lamda_regular)
# print("Mean_regular_B:\t\t" + str(mean_B_regular))
#
# res = mean_B_precheck * 0.45 + mean_B_regular * 0.55
# print(res)

# RETURN: The weighted mean/variance value for waiting time
def get_final_criteria(mean_A_precheck, mean_A_regular, mean_B_precheck, mean_B_regular, mean_C, mean_D, p_regular, p_regular_safe, p_precheck_safe):
    term_1 = p_regular * p_regular_safe * (mean_A_regular + mean_B_regular + mean_C)
    term_2 = p_regular * (1-p_regular_safe) * (mean_A_regular + mean_B_regular + mean_D)
    term_3 = (1-p_regular) * p_precheck_safe * (mean_A_precheck + mean_B_precheck + mean_C)
    term_4 = (1-p_regular) * (1-p_precheck_safe) * (mean_A_precheck + mean_B_precheck + mean_D)
    return term_1 + term_2 + term_3 + term_4


final_mean = get_final_criteria(mean_A_precheck, mean_A_regular, mean_B_precheck, mean_B_regular, mean_C, mean_D, 1-p_precheck_rate, 1-p_unsafe_rate_regular, 1-p_unsafe_rate_precheck)
final_variance = get_final_criteria(variance_A_precheck, variance_A_regular, variance_B_precheck, variance_B_regular, variance_C, variance_D, 1-p_precheck_rate, 1-p_unsafe_rate_regular, 1-p_unsafe_rate_precheck)
final_standard_dev = get_final_criteria(stand_dev_A_precheck, stand_dev_A_regular, stand_dev_B_precheck, stand_dev_B_regular, mean_C, mean_D, 1-p_precheck_rate, 1-p_unsafe_rate_regular, 1-p_unsafe_rate_precheck)
print("Final Mean:\t\t" + str(final_mean))
print("Fianl Variance:\t" + str(final_variance))
print("Standard Dev:\t" + str(final_standard_dev))