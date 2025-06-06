import numpy as np
import matplotlib.pyplot as plt


cmap = plt.get_cmap('tab10')
plotIteration = 0
color = 'blue'

def plot_positions(positions):
    global plotIteration, color

    x = positions[:, 0]
    y = positions[:, 1]
    plt.scatter(x, y, color=color)
    plt.plot(x, y, linestyle='--', color='gray')

    plotIteration += 1
    color = cmap(plotIteration%2)


def print_debug_info(positions, distances, movement=0, step=0):
    print("Step",step, "Positions:")
    print(positions)
    print(distances)
    print("Last movement:")
    print(movement)
