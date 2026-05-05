from collections import defaultdict
import numpy as np


class CentroidTracker:
    def __init__(self, max_distance=30, max_disappeared=20):
        self.next_id = 0
        self.objects = {}
        self.disappeared = {}
        self.trajectories = defaultdict(list)
        self.counts = defaultdict(int)

        self.max_distance = max_distance
        self.max_disappeared = max_disappeared

    def register(self, centroid):
        self.objects[self.next_id] = centroid
        self.disappeared[self.next_id] = 0
        self.trajectories[self.next_id].append(centroid)
        self.counts[self.next_id] = 1
        self.next_id += 1

    def deregister(self, obj_id):
        del self.objects[obj_id]
        del self.disappeared[obj_id]
        if obj_id in self.trajectories:
            del self.trajectories[obj_id]
        if obj_id in self.counts:
            del self.counts[obj_id]

    def update(self, detections):
        if len(detections) == 0:
            for obj_id in list(self.disappeared.keys()):
                self.disappeared[obj_id] += 1
                if self.disappeared[obj_id] > self.max_disappeared:
                    self.deregister(obj_id)
            return self.objects

        if len(self.objects) == 0:
            for det in detections:
                self.register(det)
            return self.objects

        obj_ids = list(self.objects.keys())
        obj_centroids = list(self.objects.values())

        D = np.linalg.norm(
            np.array(obj_centroids)[:, None] - np.array(detections),
            axis=2
        )

        rows = D.min(axis=1).argsort()
        cols = D.argmin(axis=1)[rows]

        used_rows, used_cols = set(), set()

        for row, col in zip(rows, cols):
            if row in used_rows or col in used_cols:
                continue
            if D[row, col] > self.max_distance:
                continue

            obj_id = obj_ids[row]
            self.objects[obj_id] = detections[col]
            self.disappeared[obj_id] = 0
            self.trajectories[obj_id].append(detections[col])
            self.counts[obj_id] += 1

            used_rows.add(row)
            used_cols.add(col)

        unused_rows = set(range(len(obj_centroids))) - used_rows
        for row in unused_rows:
            obj_id = obj_ids[row]
            self.disappeared[obj_id] += 1
            if self.disappeared[obj_id] > self.max_disappeared:
                self.deregister(obj_id)

        unused_cols = set(range(len(detections))) - used_cols
        for col in unused_cols:
            self.register(detections[col])

        return self.objects