import random
import numpy as np


class ViBe:
    def __init__(self, frame, num_samples=20, min_matches=3, radius=18, subsampling_factor=16):
        self.num_samples = num_samples
        self.min_matches = min_matches
        self.radius = radius
        self.subsampling_factor = subsampling_factor

        self.height, self.width = frame.shape
        self.samples = np.zeros((self.height, self.width, num_samples), dtype=np.uint8)

        for i in range(num_samples):
            rand_y = np.clip(np.arange(self.height) + np.random.randint(-1, 2, self.height), 0, self.height - 1)
            rand_x = np.clip(np.arange(self.width) + np.random.randint(-1, 2, self.width), 0, self.width - 1)
            self.samples[:, :, i] = frame[rand_y[:, None], rand_x]

    def segment(self, frame):
        diff = np.abs(self.samples - frame[:, :, None])
        matches = np.sum(diff < self.radius, axis=2)
        return (matches < self.min_matches).astype(np.uint8) * 255

    def update(self, frame, mask):
        for y in range(0, self.height, 2):
            for x in range(0, self.width, 2):
                if mask[y, x] == 0:
                    if random.randint(0, self.subsampling_factor - 1) == 0:
                        idx = random.randint(0, self.num_samples - 1)
                        self.samples[y, x, idx] = frame[y, x]

                    if random.randint(0, self.subsampling_factor - 1) == 0:
                        ny = np.clip(y + random.randint(-1, 1), 0, self.height - 1)
                        nx = np.clip(x + random.randint(-1, 1), 0, self.width - 1)
                        idx = random.randint(0, self.num_samples - 1)
                        self.samples[ny, nx, idx] = frame[y, x]