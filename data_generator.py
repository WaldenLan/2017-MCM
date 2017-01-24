import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import numpy as np
import math

# inter-arrival time:	l = []

def exp_distrib(lamda, lower, upper):
    # What is the unit of of the x-axis time we get
    sample = np.random.exponential(1/lamda)
    return sample


size = 1000
lamda = 1/9.18947
lower, upper = 0.001, 100
sample = []
for i in range(size):
	tmp = exp_distrib(lamda, lower, upper)
	sample.append(tmp)

def get_histogram(dataset, title, xlabel):
    plt.hist(dataset, bins=20, normed=1, edgecolor='white')
    plt.title(title + " Distribution")
    plt.xlabel(xlabel)
    plt.ylabel("Probability density")  # pdf = n/(Total*bin_scale)
    plt.grid(True)
    plt.show()

# get_histogram(sample, "Title", "Waiting Time [s]")


def plot_row_function(k, color):
    row = np.arange(0.01, k, 0.001)
    L_q_part1 = (row ** (k + 1)) / (k * math.factorial(k) * ((1 - row / k)** 2))
    L_q_part2 = 0
    for n in range(k):
        L_q_part2_tmp = (row ** n) / math.factorial(n) + (row ** k) / (math.factorial(k) * (1 - row / k))
        L_q_part2 += L_q_part2_tmp
    L_q = L_q_part1 * (1 / L_q_part2)
    label = "$k=" + str(k) + "$"
    plt.plot(row, L_q, color=color, linewidth=2, label=label)

def plot_row_function_list(k, color):
    for i in list(range(0, len(k), 1)):
        plot_row_function(k[i], color[i])
    plt.xlabel("$\lambda/\mu$")
    plt.ylabel("Length of Queue")
    plt.ylim(0, 20)
    # plt.axis([-6, 6, -10, 10])
    plt.grid(True)
    plt.legend(loc="upper left")
    plt.show()

k = [3, 4, 5, 6, 7, 8, 9, 10]
color = ["blue", "green", "black", "yellow", "red", "pink", "orange", "purple"]
plot_row_function_list(k, color)




