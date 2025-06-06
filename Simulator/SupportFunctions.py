import numpy as np

def squared_distances(positions):
    n = positions.shape[0]
    D = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            diff = positions[i] - positions[j]
            D[i, j] = np.linalg.norm(diff)**2
    return D

# It takes a matrix [N, 2] of positions and returns a matrix [N, N] of distances
def distances(positions):
    dim = positions.shape[0]
    dist = np.zeros((dim, dim))

    for i in range(dim):
        for j in range(i+1, dim):
            distance = np.linalg.norm(positions[i] - positions[j])
            noise = np.random.uniform(-10, 5)
            dist[i, j] = distance + noise
            dist[j, i] = distance + noise       # Ensure symmetry
    return dist

def distances_plot(positions):
    dim = positions.shape[0]
    dist = np.zeros((dim, dim))

    for i in range(dim):
        for j in range(i+1, dim):
            distance = np.linalg.norm(positions[i] - positions[j])
            dist[i, j] = distance
            dist[j, i] = distance           # Ensure symmetry
    return dist

def calculate_A(relative_positions, ref_agent):
    # remove the row corresponding to the reference agent
    return np.delete(relative_positions, ref_agent, axis=0)

def calculate_b(current_d, desired_d_sq, ref_agent):
    b = current_d[ref_agent]**2 - desired_d_sq[ref_agent]
    b = np.delete(b, ref_agent, axis=0)
    return b.reshape((-1, 1))

def limit_vector_length(v, max_length):
    scale = 1
    module = np.linalg.norm(v)

    if module > max_length:
        scale = max_length / module

    return v.copy() * scale