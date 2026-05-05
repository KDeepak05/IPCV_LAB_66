import argparse
import os
import cv2
import numpy as np

from tracker import CentroidTracker
from utils import get_video_path
from vibe import ViBe


# -----------------------------
# MAIN PIPELINE
# -----------------------------

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
