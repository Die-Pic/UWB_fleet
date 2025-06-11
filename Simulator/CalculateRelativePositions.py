import numpy as np
from scipy.optimize import least_squares


# Distance equation between agent_i and agent_j in the frame of agent_i
def distance_eq(var, i, j, currDistances):
    return var[0]**2 + var[1]**2 - currDistances[i][j]**2

# Distance equation between agent_i and agent_j in the frame of ref_agent
def neighbors_distance_eq(var1, var2, i, j, currDistances):
    return (var1[0]-var2[0])**2 + (var1[1]-var2[1])**2 - currDistances[i][j]**2


# Compensate difference in numeration between vector of variables and matrices used
def get_matrix_coord(var_coord, ref_agent):
    if var_coord < ref_agent:
        matrix_coord = var_coord
    else:
        matrix_coord = var_coord + 1

    return matrix_coord


# Takes a matrix [N, 2] of positions at previous step, a matrix [N, N] of distances at current step, an index and a vector [2] ov movement of agent_i
# It returns a matrix [N, 2] of positions relative to the input index that in the return in (0, 0)
def calculate_relative_positions(prevPositions, currDistances, ref_agent, movement):

    # Transform prev positions into relative positions centered in agent_i
    offset = prevPositions[ref_agent].copy()
    prevPositions -= offset

    # Transform prev positions into the current frame for agent_i (old positions of the other agents in the coordinates of agent_i after it moved)
    prevPositions -= movement
    prevPositions[ref_agent] = [0, 0]

    # Solve system
    def eq_system(p):
        num_neighbors = int(p.shape[0]/2)
        scale = currDistances.max()**2
        ret = []

        # Equations for current distances and distance difference
        for i in range(num_neighbors):
            # Compensate difference in numeration between vector of variables and matrices used
            j = get_matrix_coord(i, ref_agent)

            ret.append(distance_eq(p[i*2:i*2+2], ref_agent, j, currDistances) / scale)

        for i in range(num_neighbors):
            for j in range (i+1, num_neighbors):
                if i != j:
                    agent_i = get_matrix_coord(i, ref_agent)
                    agent_j = get_matrix_coord(j, ref_agent)
                    ret.append(neighbors_distance_eq(p[i*2:i*2+2], p[j*2:j*2+2], agent_i, agent_j, currDistances) / scale)

        return ret

    initial_guess = tuple(prevPositions[np.arange(prevPositions.shape[0]) != ref_agent].flatten())
    new_positions = least_squares(
        eq_system,
        initial_guess,
        loss='soft_l1',
        f_scale=1.0,
        xtol=1e-12,
        ftol=1e-12,
        gtol=1e-12
    )

    # Manipulate vector of neighbors positions to obtain the matrix of the formation
    num_neighbors = int(new_positions.x.shape[0] / 2)
    new_positions = new_positions.x.reshape((num_neighbors, 2))
    new_positions = np.insert(new_positions, ref_agent, [0, 0], axis=0)

    return new_positions