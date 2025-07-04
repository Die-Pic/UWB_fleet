Formation algorithm
The user enters a desired_formation and a current_formation as sets of points (x, y).
The current_formation represents the global positions of the drones at the start of the simulation, while the desired_formation it's used to obtain the distances to which the drones should converge at runtime.

Algorithm:
1. At the start of the simulations the drones perform a routine to calculate the position of the other drones relative to their orientation system.
   One drone at a time performs a set of movements (minimum of 3) and measure the distances to the others at different instants, those measures are then used to obtain the positions of the other drones.
2. Each drone measures the distance to the others and then receives the missing distance from another drone (e.g. drone_1 calculates the distances to drone_2 and drone_3 and then receive the distance between drone_2 and drone_3 from drone_3), all the drones sync at this step.
3. Each drone then uses the distances to update the positions of the other drones (not needed the first time since the relative positions are calculated with the initial routine).
4. Each drone uses the locally calculated positions info and desired formation distances to calculate the matrix A and vector b (A represents the direction of the movement, b the amount of movement), using these matrices it calculates the velocity vector that is needed to converge to (or maintain) the formation.
5. After the movement repeat from (2.)

This algorithm is based on the paper "Formation control of mobile agents based on inter-agent distance dynamics".
