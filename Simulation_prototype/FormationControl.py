import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from Simulation_prototype import RelativePositionUpdate as pu
from Simulation_prototype import DebugFunctions as db

DEBUG = 0               # 0: only graphical plotting, 1: Initial and final position and movement, 2: Also position and movement for each tep
time = 20
stepTime = 1
parameter_k = 0.12      # How fast the formation converges


def squared_distances(positions):
    dim = positions.shape[0]
    dist = np.zeros((dim, dim))

    for i in range(dim):
        for j in range(dim):
            diff = positions[i] - positions[j]
            dist[i, j] = np.linalg.norm(diff) ** 2
    return dist

def calculate_A(relative_positions, ref_agent):
    A = np.delete(relative_positions.copy(), ref_agent, axis=0)
    return A


def calculate_b(current_d, desired_d_sq, ref_agent):
    b = current_d[ref_agent]**2 - desired_d_sq[ref_agent]
    b = np.delete(b, ref_agent, axis=0)
    b.reshape((-1, 1))
    return b




# Start simulation load data prom input files
desiredFormation_global = pd.read_csv("desiredFormation.csv", delimiter=";", header=None).to_numpy()
currPositions_global = pd.read_csv("startFormation2.csv", delimiter=";", header=None).to_numpy()

db.plot_positions(currPositions_global)
if DEBUG >= 1:
    current_d = pu.distances(currPositions_global)
    db.print_debug_info(currPositions_global, current_d)

# Calculate desired distances
desired_d_sq = squared_distances(desiredFormation_global)

# Initialize local view of the formation and movement for each agent
numAgents = currPositions_global.shape[0]
movement = np.zeros((numAgents, 2))
prevPositions_local = np.zeros((numAgents, numAgents, 2))
for i in range(numAgents):
    prevPositions_local[i] = currPositions_global.copy()

# Parameters of the system evolution
numSteps = int(time / stepTime)
for i in range(1,numSteps+1):
    #current_d_sq = squared_distances(currFormation_global)
    # Each agent measures the relative distances and sends one measurement to another agent to complete the triangle
    current_d = pu.distances(currPositions_global)

    for j in range(numAgents):          # TODO Only works with 2 neighbors

        # Using the previous relative positions and the current distances each agent calculate the current relative distances (substitutes the prev with the updated)
        currPositions_local = pu.calculate_relative_positions(prevPositions_local[j], current_d, j, movement[j])
        prevPositions_local[j] = currPositions_local.copy()

        # Each agent calculates A direction matrix and b amount of movement
        #A = np.zeros((2, 2))
        #A[0] = currFormation_global[(j + 1) % 3] - currFormation_global[j]
        #A[1] = currFormation_global[(j + 2) % 3] - currFormation_global[j]
        A = calculate_A(currPositions_local, j)

        A_inv = np.linalg.inv(A)

        # Calculating b
        #b = np.zeros((2, 1))
        #b[0][0] = current_d_sq[j][(j + 1) % 3] - desired_d_sq[j][(j + 1) % 3]
        #b[1][0] = current_d_sq[j][(j + 2) % 3] - desired_d_sq[j][(j + 2) % 3]
        b = calculate_b(current_d, desired_d_sq, j)

        # And calculates the movement to do to maintain the formation
        velocity = (parameter_k / 4 * A_inv.dot(b)).T
        movement[j] = velocity * stepTime

    # Updating positions according to new speed in 1 second step
    currPositions_global += movement
    db.plot_positions(currPositions_global)
    if DEBUG >= 2:
        current_d = pu.distances(currPositions_global)
        db.print_debug_info(currPositions_global, current_d, movement, numSteps)


if DEBUG >= 1:
    current_d = pu.distances(currPositions_global)
    db.print_debug_info(currPositions_global, current_d, movement, numSteps)

plt.xlabel("X")
plt.ylabel("Y")
plt.grid(True)
plt.axis('equal')
plt.show()
