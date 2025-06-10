import numpy as np
import matplotlib.pyplot as plt

class Formation:
    def __init__(self,
                 formation: np.ndarray):

        # Formation attributes
        self.currentFormation = formation.copy()
        self.previousFormation = formation.copy()

        # Plotting attributes
        self.cmap = plt.get_cmap('tab10')
        self.plotIteration = 0
        self.color = 'blue'


    def get_positions(self):
        return self.currentFormation.copy()

    def get_position(self, drone_id: int):
        return self.currentFormation[drone_id].copy()


    def get_num_agents(self):
        return self.currentFormation.shape[0]


    def update_position(self, drone_id, movement):
        self.currentFormation[drone_id] += movement


    def get_distances(self):
        dim = self.get_num_agents()
        dist = np.zeros((dim, dim))

        for i in range(dim):
            for j in range(i + 1, dim):
                distance = np.linalg.norm(self.currentFormation[i] - self.currentFormation[j])
                dist[i, j] = distance
                dist[j, i] = distance   # Ensure symmetry
        return dist


    def get_distances_with_id(self, drone_id: int):
        dim = self.get_num_agents()
        dist = np.zeros((dim, dim))

        for i in range(dim):
            distance = np.linalg.norm(self.currentFormation[i] - self.currentFormation[drone_id])
            dist[i, drone_id] = distance
            dist[drone_id, i] = distance    # Ensure symmetry
        return dist


    def get_distances_with_noise(self):
        dim = self.get_num_agents()
        dist = np.zeros((dim, dim))

        for i in range(dim):
            for j in range(i + 1, dim):
                distance = np.linalg.norm(self.currentFormation[i] - self.currentFormation[j])
                noise = np.random.uniform(-10, 5)
                dist[i, j] = distance + noise
                dist[j, i] = distance + noise   # Ensure symmetry
        return dist


    def get_distances_with_id_with_noise(self, drone_id: int):
        dim = self.get_num_agents()
        dist = np.zeros((dim, dim))

        for i in range(dim):
            distance = np.linalg.norm(self.currentFormation[i] - self.currentFormation[drone_id])
            noise = np.random.uniform(-10, 5)
            dist[i, drone_id] = distance + noise
            dist[drone_id, i] = distance + noise    # Ensure symmetry
        return dist


    def get_squared_distances(self):
        dist = self.get_distances()
        return dist**2


    def plot_formation(self):
        x = self.currentFormation[:, 0]
        y = self.currentFormation[:, 1]
        plt.scatter(x, y, color=self.color)
        plt.plot(x, y, linestyle='--', color='gray')

        self.plotIteration += 1
        self.color = self.cmap(self.plotIteration % 2)


    def show_plot(self):
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.grid(True)
        plt.axis("equal")
        plt.show()