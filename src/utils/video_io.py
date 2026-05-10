"""
Video I/O Utilities
===================
Wrappers around OpenCV VideoCapture and VideoWriter for clean video handling.
"""

import cv2
import os


class VideoReader:
    """Wrapper around cv2.VideoCapture with metadata extraction."""

    def __init__(self, video_path):
        self.path = video_path
        self.cap = None
        self.fps = 0
        self.width = 0
        self.height = 0
        self.frame_count = 0
        self.current_frame = 0
        self._open(video_path)

    def _open(self, path):
        """Open video file and extract metadata."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Video file not found: {path}")
        
        self.cap = cv2.VideoCapture(path)
        if not self.cap.isOpened():
            raise IOError(f"Cannot open video: {path}")
        
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    def read(self):
        """Read next frame. Returns (success, frame)."""
        if self.cap is None:
            return False, None
        ret, frame = self.cap.read()
        if ret:
            self.current_frame += 1
        return ret, frame

    def seek(self, frame_number):
        """Seek to a specific frame number."""
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            self.current_frame = frame_number

    def get_progress(self):
        """Get current progress as a fraction (0.0 to 1.0)."""
        if self.frame_count <= 0:
            return 0.0
        return self.current_frame / self.frame_count

    def get_info(self):
        """Get video metadata as a dictionary."""
        return {
            'path': self.path,
            'filename': os.path.basename(self.path),
            'fps': self.fps,
            'width': self.width,
            'height': self.height,
            'frame_count': self.frame_count,
            'duration': self.frame_count / self.fps if self.fps > 0 else 0
        }

    def release(self):
        """Release the video capture object."""
        if self.cap:
            self.cap.release()
            self.cap = None

    def __del__(self):
        self.release()


class VideoWriter:
    """Wrapper around cv2.VideoWriter for saving processed videos."""

    def __init__(self, output_path, fps=30.0, width=640, height=480, codec='mp4v'):
        self.path = output_path
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        fourcc = cv2.VideoWriter_fourcc(*codec)
        self.writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        self.frame_count = 0

    def write(self, frame):
        """Write a frame to the output video."""
        if self.writer and self.writer.isOpened():
            self.writer.write(frame)
            self.frame_count += 1

    def release(self):
        """Release the video writer."""
        if self.writer:
            self.writer.release()
            self.writer = None

    def __del__(self):
        self.release()
