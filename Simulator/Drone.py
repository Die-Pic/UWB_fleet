import simpy
import numpy as np
from Simulator import SupportFunctions as sf
from Simulator import FormationControl as fc
from Simulator import Formation as frm


class Drone:
    def __init__(self, env: simpy.Environment,
                 drone_id: int,
                 max_speed: float,
                 currPositions_global_ref: frm.Formation,
                 message_bus: simpy.FilterStore,
                 desired_d_sq: np.ndarray,
                 param_k: float,
                 timeStep: float):

        # Environment for simpy
        self.env = env

        # Local parameters
        self.id = drone_id
        self.max_speed = max_speed
        self.message_bus = message_bus
        self.desired_d_sq = desired_d_sq
        self.k = param_k
        self.timeStep = timeStep

        # Reference to global positions to calculate current distances and apply the movement
        self.currPositions_global_ref = currPositions_global_ref

        # Local view of the position of the other agents
        self.currPositions_local = currPositions_global_ref.get_positions() - currPositions_global_ref.get_positions()[drone_id]
        self.prevPositions_local = self.currPositions_local.copy()

        # Movement for a step
        self.movement = np.zeros(2)

        # Start to run in the environment
        self.process = env.process(self.run())


    def run(self):
        while True:
            # Measure distances form others agents and send/receive the distance between the 2 it can't measure locally
            current_d = self.currPositions_global_ref.get_distances_with_id_with_noise(self.id)

            send_message, recv_condition = create_message(self.id, current_d)           # TODO only works with 2 neighbors
            yield self.message_bus.put(send_message)

            recv_message = yield self.message_bus.get(recv_condition)
            update_distance(current_d, recv_message)

            yield self.env.timeout(0)  # Sync to ensure everyone calculates current_d before moving


            # Step of the formation control algorithm
            velocity = fc.formation_control_iteration(self, current_d)

            velocity = sf.limit_vector_length(velocity, self.max_speed)
            self.movement = velocity.flatten() * self.timeStep


            # Update global position with its own movement and advance time
            self.currPositions_global_ref.update_position(self.id, self.movement)
            yield self.env.timeout(self.timeStep)


            # Plot
            if self.id == 0:
                self.currPositions_global_ref.plot_formation()


def create_message(drone_id, distances):
    num_drones = distances.shape[0]
    next_id = (drone_id + 1) % num_drones
    payload = distances[drone_id][next_id]

    def select_msg(msg):
        return msg[0] == next_id

    return (drone_id, payload), select_msg


def update_distance(distances, message):
    num_drones = distances.shape[0]
    sender_id = message[0]
    next_sender_id = (sender_id + 1) % num_drones
    distance = message[1]

    distances[sender_id][next_sender_id] = distance
    distances[next_sender_id][sender_id] = distance     # Maintain symmetry