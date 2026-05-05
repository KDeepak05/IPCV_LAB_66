import argparse
import os
import random
from collections import defaultdict

import cv2
import numpy as np

DEFAULT_VIDEO = os.path.join("Dataset", "VIRAT_S_010204_05_000856_000890.mp4")

# -----------------------------
# VIBE (BALANCED)
# -----------------------------
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


# -----------------------------
# TRACKER (STABLE)
# -----------------------------
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


# -----------------------------
# MAIN PIPELINE
# -----------------------------

def get_video_path(input_path=None):
    if input_path:
        return input_path

    default_path = os.path.abspath(DEFAULT_VIDEO)
    if os.path.exists(default_path):
        return default_path

    dataset_dir = os.path.abspath("Dataset")
    if os.path.isdir(dataset_dir):
        for filename in os.listdir(dataset_dir):
            if filename.lower().endswith(".mp4"):
                return os.path.join(dataset_dir, filename)

    return default_path


def main(video_path):
    video_path = get_video_path(video_path)
    if not os.path.exists(video_path):
        print(f"Video not found: {video_path}")
        return

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Unable to open video: {video_path}")
        return

    width, height = 480, 270

    ret, frame = cap.read()
    if not ret:
        print(f"Error reading video: {video_path}")
        cap.release()
        return

    frame = cv2.resize(frame, (width, height))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    vibe = ViBe(gray)
    tracker = CentroidTracker()

    kernel = np.ones((3, 3), np.uint8)

    frame_skip = 2
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % frame_skip != 0:
            continue

        frame = cv2.resize(frame, (width, height))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        mask = vibe.segment(gray)
        mask = cv2.medianBlur(mask, 5)
        _, mask = cv2.threshold(mask, 200, 255, cv2.THRESH_BINARY)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        detections = []

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 700:
                continue

            x, y, w, h = cv2.boundingRect(cnt)
            if w > 180 and h > 180:
                continue
            if w < 20 or h < 20:
                continue

            ratio = w / float(h)
            if ratio < 0.3 or ratio > 2.5:
                continue

            cx, cy = x + w // 2, y + h // 2
            detections.append((cx, cy))
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        objects = tracker.update(detections)

        for obj_id, centroid in objects.items():
            if tracker.counts[obj_id] < 10:
                continue

            cv2.putText(frame, f"ID {obj_id}", centroid,
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.circle(frame, centroid, 4, (0, 0, 255), -1)

            pts = tracker.trajectories[obj_id]
            for i in range(1, len(pts)):
                cv2.line(frame, pts[i - 1], pts[i], (255, 0, 0), 2)

        cv2.imshow("Frame", frame)
        cv2.imshow("Mask", mask)

        if cv2.waitKey(1) & 0xFF == 27:
            break

        vibe.update(gray, mask)

    cap.release()
    cv2.destroyAllWindows()


# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Moving Object Detection and Trajectory Tracking using VIBE Background Extractor (NumPy)"
    )
    parser.add_argument(
        "--video",
        type=str,
        default=None,
        help="Path to the input video file. If omitted, a video from the Dataset folder is used."
    )
    args = parser.parse_args()
    main(args.video)
