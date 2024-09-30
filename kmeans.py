import numpy as np

class KMeans:
    def __init__(self, data, k, method='random', centroids=None):
        """
        Initialize the KMeans object.
        Parameters:
        - data: The dataset as a NumPy array.
        - k: The number of clusters.
        - method: The method for initializing centroids ('random', 'farthest', 'kmeans++', or 'manual').
        - centroids: Manually selected centroids as a NumPy array, used when method is 'manual'.
        """
        self.data = data
        self.k = k
        self.method = method
        self.centroids = centroids if centroids is not None else self.initialize_centroids()
        self.clusters = None

    def initialize_centroids(self):
        """Initialize centroids based on the chosen method."""
        if self.method == 'random':
            indices = np.random.choice(range(len(self.data)), self.k, replace=False)
        elif self.method == 'farthest':
            indices = [np.random.randint(0, len(self.data))]
            for _ in range(1, self.k):
                dist = np.min(np.linalg.norm(self.data - self.data[indices, None], axis=2), axis=0)
                next_index = np.argmax(dist)
                indices.append(next_index)
        elif self.method == 'kmeans++':
            indices = [np.random.randint(0, len(self.data))]
            for _ in range(1, self.k):
                dist = np.min([np.linalg.norm(self.data - self.data[idx], axis=1)**2 for idx in indices], axis=0)
                probabilities = dist / dist.sum()
                next_index = np.random.choice(len(self.data), p=probabilities)
                indices.append(next_index)
        else:
            raise ValueError(f"Unsupported initialization method: {self.method}")
        
        return self.data[indices]

    def assign_clusters(self):
        """Assign each data point to the nearest centroid."""
        clusters = [[] for _ in range(self.k)]
        for idx, point in enumerate(self.data):
            # Compute distances from the point to all centroids
            distances = np.linalg.norm(self.centroids - point, axis=1)
            # Find the closest centroid
            closest_centroid = np.argmin(distances)
            clusters[closest_centroid].append(idx)
        return clusters

    def update_centroids(self, clusters):
        """Update centroids as the mean of assigned data points."""
        new_centroids = np.array([self.data[cluster].mean(axis=0) if cluster else self.centroids[i]
                                  for i, cluster in enumerate(clusters)])
        return new_centroids

    def fit(self, max_steps=100):
        """Run the KMeans algorithm until convergence or for a set number of steps."""
        steps = []

        for step in range(max_steps):
            # Assign points to nearest centroid
            clusters = self.assign_clusters()
            steps.append((self.centroids.copy(), clusters))

            # Calculate new centroids
            new_centroids = self.update_centroids(clusters)

            # Check for convergence
            if np.allclose(new_centroids, self.centroids, rtol=1e-6, atol=1e-6):
                break

            # Update centroids
            self.centroids = new_centroids

        self.clusters = clusters
        return steps

    def predict(self, point):
        """Predict the cluster for a given point."""
        distances = np.linalg.norm(self.centroids - point, axis=1)
        return np.argmin(distances)
