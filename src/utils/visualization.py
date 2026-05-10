"""
Visualization Utilities
=======================
Drawing functions for bounding boxes, trajectories, heatmaps, and overlays.
"""

import cv2
import numpy as np
from collections import deque

# Color palette for track IDs (BGR format)
TRACK_COLORS = [
    (0, 255, 255),   # Cyan
    (0, 255, 0),     # Green
    (255, 0, 255),   # Magenta
    (0, 165, 255),   # Orange
    (255, 255, 0),   # Cyan-ish
    (0, 0, 255),     # Red
    (255, 0, 0),     # Blue
    (0, 255, 128),   # Spring green
    (255, 128, 0),   # Light blue
    (128, 0, 255),   # Purple
]


def get_track_color(track_id):
    """Get a consistent color for a track ID."""
    return TRACK_COLORS[track_id % len(TRACK_COLORS)]


def draw_bounding_boxes(frame, tracks):
    """Draw bounding boxes and labels for all tracked objects."""
    result = frame.copy()
    for tid, track in tracks.items():
        if track.bbox is None:
            continue
        color = get_track_color(tid)
        x, y, w, h = track.bbox
        
        # Draw box with slightly thick border
        cv2.rectangle(result, (x, y), (x + w, y + h), color, 2)
        
        # Draw label background
        label = f"ID:{tid}"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(result, (x, y - th - 8), (x + tw + 8, y), color, -1)
        cv2.putText(result, label, (x + 4, y - 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
    return result


def draw_trajectories(frame, tracks, fade=True):
    """Draw motion trail lines for tracked objects with optional fading."""
    result = frame.copy()
    overlay = result.copy()
    
    for tid, track in tracks.items():
        path = list(track.path)
        if len(path) < 2:
            continue
        color = get_track_color(tid)
        
        for i in range(1, len(path)):
            if fade:
                alpha = i / len(path)
                thickness = max(1, int(3 * alpha))
            else:
                thickness = 2
            
            pt1 = (int(path[i - 1][0]), int(path[i - 1][1]))
            pt2 = (int(path[i][0]), int(path[i][1]))
            cv2.line(overlay, pt1, pt2, color, thickness, cv2.LINE_AA)
    
    cv2.addWeighted(overlay, 0.7, result, 0.3, 0, result)
    return result


def draw_centroids(frame, tracks):
    """Draw centroid markers for tracked objects."""
    result = frame.copy()
    for tid, track in tracks.items():
        color = get_track_color(tid)
        cx, cy = int(track.centroid[0]), int(track.centroid[1])
        cv2.circle(result, (cx, cy), 5, color, -1, cv2.LINE_AA)
        cv2.circle(result, (cx, cy), 7, (255, 255, 255), 1, cv2.LINE_AA)
    return result


def draw_direction_arrows(frame, tracks, scale=3.0):
    """Draw velocity direction arrows on tracked objects."""
    result = frame.copy()
    for tid, track in tracks.items():
        if track.get_speed() < 1.0:
            continue
        color = get_track_color(tid)
        cx, cy = int(track.centroid[0]), int(track.centroid[1])
        vx, vy = track.velocity
        end_x = int(cx + vx * scale)
        end_y = int(cy + vy * scale)
        cv2.arrowedLine(result, (cx, cy), (end_x, end_y), color, 2, cv2.LINE_AA, tipLength=0.3)
    return result


def generate_heatmap(accumulator, shape):
    """Generate a color heatmap from a motion accumulator array."""
    if accumulator is None:
        return np.zeros((*shape[:2], 3), dtype=np.uint8)
    
    # Normalize to 0-255
    norm = cv2.normalize(accumulator.astype(np.float32), None, 0, 255, cv2.NORM_MINMAX)
    norm = norm.astype(np.uint8)
    
    # Apply colormap
    heatmap = cv2.applyColorMap(norm, cv2.COLORMAP_JET)
    return heatmap


def draw_fps(frame, fps):
    """Draw FPS counter overlay on frame."""
    result = frame.copy()
    text = f"FPS: {fps:.1f}"
    cv2.putText(result, text, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA)
    return result


def colorize_mask(mask):
    """Convert a binary foreground mask to a colorized visualization."""
    colored = np.zeros((*mask.shape, 3), dtype=np.uint8)
    colored[mask > 0] = (0, 255, 255)  # Cyan for foreground
    return colored


def create_detection_view(frame, tracks):
    """Create the full detection visualization with boxes, trails, arrows, centroids."""
    result = frame.copy()
    result = draw_trajectories(result, tracks)
    result = draw_bounding_boxes(result, tracks)
    result = draw_centroids(result, tracks)
    result = draw_direction_arrows(result, tracks)
    return result
