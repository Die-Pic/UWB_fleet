import simpy
import numpy as np
from Simulator import Drone as dr
from Simulator import Formation as frm
from Simulator import FormationControl as fc



if __name__ == "__main__":
    # parameters
    time       = 15
    stepTime   = 1
    parameter_k= 0.5

    # Initialize formations
    currentFormation = frm.Formation(np.array([[0.0, 0.0],
                                               [100.0, 0.0],
                                               [0.0, 100.0]]))

    # SimPy environment
    env = simpy.Environment()

    # Store used to simulate the message passing between drones
    message_bus = simpy.FilterStore(env)

    # Create drones
    d = dr.Drone(env,
                 drone_id=0,
                 max_speed=5,           # cm/s
                 message_bus=message_bus,
                 currPositions_global_ref=currentFormation,
                 desired_d_sq=currentFormation.get_squared_distances(),
                 param_k=parameter_k,
                 timeStep=stepTime)

    relative_positions = fc.obtain_relative_positions(d, 30.0, 4)
    print(relative_positions)

