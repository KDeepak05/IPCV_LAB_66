"""
Helper Utilities
================
General-purpose utility functions for the application.
"""

import cv2
import numpy as np
import os
from datetime import datetime


def frame_to_qpixmap(frame):
    """Convert an OpenCV BGR frame to a QPixmap for display in PyQt5."""
    from PyQt5.QtGui import QImage, QPixmap
    
    if len(frame.shape) == 2:
        # Grayscale
        h, w = frame.shape
        bytes_per_line = w
        qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_Grayscale8)
    else:
        # BGR -> RGB
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
    
    return QPixmap.fromImage(qimg)


def save_screenshot(frame, output_dir="outputs/screenshots", prefix="screenshot"):
    """Save a frame as a PNG screenshot with timestamp."""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.png"
    filepath = os.path.join(output_dir, filename)
    cv2.imwrite(filepath, frame)
    return filepath


def timestamp_str():
    """Get current timestamp as a formatted string."""
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def format_duration(seconds):
    """Format seconds into MM:SS string."""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"


def ensure_dirs():
    """Ensure all required output directories exist."""
    dirs = [
        "dataset/virat", "dataset/campus",
        "outputs/videos", "outputs/screenshots", "outputs/graphs",
        "reports"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)


def resize_with_aspect(frame, max_width, max_height):
    """Resize frame to fit within max dimensions while keeping aspect ratio."""
    h, w = frame.shape[:2]
    scale = min(max_width / w, max_height / h)
    if scale >= 1.0:
        return frame
    new_w, new_h = int(w * scale), int(h * scale)
    return cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
