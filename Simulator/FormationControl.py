import numpy as np
from Simulator import Drone
from Simulator import SupportFunctions as sf
from Simulator import CalculateRelativePositions as rp

def calculate_velocity(drone_id, relative_positions, distances, desired_distances, k):
    A = sf.calculate_A(relative_positions, drone_id)
    b = sf.calculate_b(distances, desired_distances, drone_id)

    epsilon = 0.1       # Epsilon and linalg solve used to mitigate the problem of near singular matrices due to noise
    x = np.linalg.solve(A.T @ A + epsilon * np.eye(A.shape[1]), A.T @ b)
    velocity = (k / 4 * x).T

    return velocity

def formation_control_iteration(drone: Drone, distances):
    # Calculate the new relative positions and update prev
    drone.currPositions_local = rp.calculate_relative_positions(drone.prevPositions_local,
                                                                distances,
                                                                drone.id,
                                                                drone.movement)
    drone.prevPositions_local = drone.currPositions_local.copy()

    # Calculate movement (take into account max speed of the drone)
    velocity = calculate_velocity(drone.id,
                                  drone.currPositions_local,
                                  distances,
                                  drone.desired_d_sq,
                                  drone.k)

    velocity = sf.limit_vector_length(velocity, drone.max_speed)

    return velocity