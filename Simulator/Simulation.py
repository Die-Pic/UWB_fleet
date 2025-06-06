import simpy
import numpy as np
from Simulator import Drone as dr
from Simulator import Formation as frm



if __name__ == "__main__":
    # parameters
    time       = 15
    stepTime   = 1
    parameter_k= 0.5

    # Initialize formations
    desiredFormation = frm.Formation(np.array([[0.0, 0.0],
                                               [0.0,100.0],
                                               [100.0,0.0]]))
    currentFormation = frm.Formation(np.array([[15.5,10.3],
                                               [150.0,35.0],
                                               [100.3,110.8]]))
    currentFormation.plot_formation()
    desired_d_sq = desiredFormation.get_squared_distances()


    # SimPy environment
    env = simpy.Environment()

    # Store used to simulate the message passing between drones
    message_bus = simpy.FilterStore(env)

    # Create drones
    drones = []
    for i in range(currentFormation.get_num_agents()):
        d = dr.Drone(env,
                     drone_id=i,
                     max_speed=5,           # cm/s
                     message_bus=message_bus,
                     currPositions_global_ref=currentFormation,
                     desired_d_sq=desired_d_sq,
                     param_k=parameter_k,
                     timeStep=stepTime)
        drones.append(d)

    env.run(until=time)

    # Show plot and final distances
    currentFormation.show_plot()

    distances = currentFormation.get_distances()
    print(distances)