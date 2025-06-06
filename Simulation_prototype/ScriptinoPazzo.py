import numpy as np
import pandas as pd
import RelativePositionUpdate as pu


desiredFormation = pd.read_csv("desiredFormation.csv", delimiter=";", header=None)
currFormation = pd.read_csv("startFormation.csv", delimiter=";", header=None)
desiredFormation_global = desiredFormation.to_numpy()
currFormation_global = currFormation.to_numpy()

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

def calculate_error(desired_d_sq, current_d):
    desired_d = np.sqrt(desired_d_sq.copy())
    error = 0.0

    for i in range(desired_d.shape[0]):
        for j in range(i,desired_d.shape[1]):
            error += (desired_d[i, j] - current_d[i, j])**2

    return error


# Calculate desired distances
desired_d_sq = squared_distances(desiredFormation_global)

# Initialize local view of the formation and movement for each agent
numAgents = currFormation_global.shape[0]
movement = np.zeros((numAgents, 2))
prevPositions_local = np.zeros((numAgents, numAgents, 2))
for i in range(numAgents):
    prevPositions_local[i] = currFormation_global.copy()

# Parameters of the system evolution
time = 10
stepTime_optimal = 0.0
parameter_k_optimal = 0.0

stepTime = 0.1
parameter_k = 0.01         # How fast the formation converge
error_min = 5000
error = 0.0
for stepTime in np.arange(0.1, 1.1, 0.1):
    for parameter_k in np.arange(0.01, 0.51, 0.01):

        numSteps = int(time / stepTime)
        for i in range(1,numSteps+1):
            # Each agent measures the relative distances and sends one measurement to another agent to complete the triangle
            current_d = pu.distances(currFormation_global)

            for j in range(numAgents):          # TODO Only works with 2 neighbors

                # Using the previous relative positions and the current distances each agent calculate the current relative distances (substitutes the prev with the updated)
                currPositions_local = pu.calculate_relative_positions(prevPositions_local[j], current_d, j, movement[j])
                prevPositions_local[j] = currPositions_local.copy()

                # Each agent calculates A direction matrix and b amount of movement
                A = calculate_A(currPositions_local, j)
                A_inv = np.linalg.inv(A)

                # Calculating b
                b = calculate_b(current_d, desired_d_sq, j)

                # And calculates the movement to do to maintain the formation
                velocity = (parameter_k / 4 * A_inv.dot(b)).T
                movement[j] = velocity * stepTime

            # Updating positions according to new speed in 1 second step
            currFormation_global += movement

        # Compute error
        current_d = pu.distances(currFormation_global)
        error = calculate_error(desired_d_sq, current_d)

        if error <= error_min:
            error_min = error
            stepTime_optimal = stepTime
            parameter_k_optimal = parameter_k

        parameter_k += 0.01

    stepTime += 0.1


print(parameter_k_optimal)
print(stepTime_optimal)