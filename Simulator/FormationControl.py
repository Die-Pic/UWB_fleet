import numpy as np
import math
from scipy.optimize import least_squares
from Simulator import Drone
from Simulator import Formation as frm
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


def obtain_relative_positions(drone: Drone, movement: float, number_of_movements: int):

    movements_list = calculate_movement_list(movement, number_of_movements)

    distances, routine_positions = apply_movements_get_distances_positions(drone, movements_list)

    # Solve the system to calculate relative positions
    def eq_system(p):
        num_agents = int(p.shape[0]/2)
        ret = []
        scale = distances.max()**2

        for i in range(num_agents):
            for j in range(number_of_movements):
                ret.append(((p[i*2] - routine_positions[j][0])**2 + (p[i*2+1] - routine_positions[j][1])**2 - distances[j][i]**2)/scale)

        return ret

    num_neighbors = drone.currPositions_global_ref.get_num_agents()-1
    initial_guess = np.zeros(num_neighbors*2)
    relative_positions = least_squares(
        eq_system,
        initial_guess,
        loss='soft_l1',
        f_scale=1.0,
        xtol=1e-12,
        ftol=1e-12,
        gtol=1e-12
    ).x

    relative_positions = relative_positions.reshape(-1, 2)
    zeros = np.zeros(2)
    relative_positions = np.insert(relative_positions, drone.id, zeros, axis=0)
    return relative_positions


def movement_step(formation: frm.Formation, drone_id: int, movement):
    formation.update_position(drone_id, movement)
    distances = formation.get_distances_with_id(drone_id)

    return np.delete(distances[drone_id], drone_id, axis=0)


def calculate_movement_list(movement: float, number_of_movements: int):
    movements_list = np.zeros((number_of_movements, 2))
    angle_increase = 360 / number_of_movements

    for i in range(number_of_movements):
        angle = math.radians(angle_increase * i)
        movements_list[i] = np.array([movement * math.cos(angle), movement * math.sin(angle)])

    return movements_list


def apply_movements_get_distances_positions(drone: Drone, movements_list):
    number_of_movements = movements_list.shape[0]
    num_neighbors = drone.currPositions_global_ref.get_num_agents() - 1

    distances = np.zeros((number_of_movements, num_neighbors))
    routine_positions = np.zeros((number_of_movements, 2))
    start_position = drone.currPositions_global_ref.get_position(drone.id)

    for i in range(number_of_movements):
        distances[i] = movement_step(drone.currPositions_global_ref, drone.id, movements_list[i])
        routine_positions[i] = drone.currPositions_global_ref.get_position(drone.id) - start_position

    return distances, routine_positions