"""
Performance Evaluation Metrics
==============================
Calculates FPS, detection statistics, and generates report-ready graphs.
"""

import numpy as np
import time
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import deque


class PerformanceTracker:
    """Tracks per-frame performance metrics for the detection pipeline."""

    def __init__(self, window_size=100):
        self.window_size = window_size
        self.fps_history = deque(maxlen=window_size)
        self.object_count_history = deque(maxlen=window_size)
        self.processing_time_history = deque(maxlen=window_size)
        self.motion_intensity_history = deque(maxlen=window_size)
        self.frame_timestamps = deque(maxlen=window_size)
        
        self._last_time = None
        self.total_frames = 0
        self.total_detections = 0
        self.max_objects = 0
        self.start_time = time.time()

    def update(self, num_objects, processing_time, fg_mask=None):
        """Record metrics for one processed frame."""
        current_time = time.time()
        
        # Calculate FPS
        if self._last_time is not None:
            dt = current_time - self._last_time
            fps = 1.0 / dt if dt > 0 else 0
        else:
            fps = 0
        self._last_time = current_time
        
        # Calculate motion intensity (percentage of foreground pixels)
        motion_intensity = 0
        if fg_mask is not None:
            motion_intensity = (np.count_nonzero(fg_mask) / fg_mask.size) * 100
        
        # Store metrics
        self.fps_history.append(fps)
        self.object_count_history.append(num_objects)
        self.processing_time_history.append(processing_time * 1000)  # ms
        self.motion_intensity_history.append(motion_intensity)
        self.frame_timestamps.append(self.total_frames)
        
        self.total_frames += 1
        self.total_detections += num_objects
        self.max_objects = max(self.max_objects, num_objects)

    def get_current_fps(self):
        """Get current FPS (average of last 10 frames)."""
        if len(self.fps_history) < 2:
            return 0
        recent = list(self.fps_history)[-10:]
        return np.mean(recent)

    def get_avg_fps(self):
        """Get average FPS over entire session."""
        if len(self.fps_history) == 0:
            return 0
        return np.mean(list(self.fps_history))

    def get_current_object_count(self):
        """Get the most recent object count."""
        if len(self.object_count_history) == 0:
            return 0
        return self.object_count_history[-1]

    def get_motion_intensity(self):
        """Get current motion intensity percentage."""
        if len(self.motion_intensity_history) == 0:
            return 0
        return self.motion_intensity_history[-1]

    def get_avg_processing_time(self):
        """Get average processing time in ms."""
        if len(self.processing_time_history) == 0:
            return 0
        return np.mean(list(self.processing_time_history))

    def get_summary(self):
        """Get a summary dictionary of all metrics."""
        elapsed = time.time() - self.start_time
        return {
            'total_frames': self.total_frames,
            'avg_fps': self.get_avg_fps(),
            'current_fps': self.get_current_fps(),
            'total_detections': self.total_detections,
            'max_simultaneous': self.max_objects,
            'avg_processing_ms': self.get_avg_processing_time(),
            'elapsed_time': elapsed,
            'motion_intensity': self.get_motion_intensity(),
        }

    def generate_report_graphs(self, output_dir="outputs/graphs"):
        """Generate matplotlib charts for the report."""
        os.makedirs(output_dir, exist_ok=True)
        
        plt.style.use('dark_background')
        fig_color = '#0a0e17'
        accent = '#00e5ff'
        accent2 = '#7c3aed'
        
        frames = list(self.frame_timestamps)
        if len(frames) < 2:
            return []
        
        saved = []
        
        # 1. FPS vs Time
        fig, ax = plt.subplots(figsize=(10, 5), facecolor=fig_color)
        ax.set_facecolor(fig_color)
        ax.plot(frames, list(self.fps_history), color=accent, linewidth=1.5, alpha=0.9)
        ax.fill_between(frames, list(self.fps_history), alpha=0.2, color=accent)
        ax.set_xlabel('Frame', color='white', fontsize=12)
        ax.set_ylabel('FPS', color='white', fontsize=12)
        ax.set_title('FPS Performance Over Time', color='white', fontsize=14, fontweight='bold')
        ax.tick_params(colors='gray')
        ax.grid(alpha=0.15, color='gray')
        ax.spines['bottom'].set_color('gray')
        ax.spines['left'].set_color('gray')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        path1 = os.path.join(output_dir, 'fps_vs_time.png')
        fig.savefig(path1, dpi=150, bbox_inches='tight', facecolor=fig_color)
        plt.close(fig)
        saved.append(path1)
        
        # 2. Objects Detected vs Frames
        fig, ax = plt.subplots(figsize=(10, 5), facecolor=fig_color)
        ax.set_facecolor(fig_color)
        ax.plot(frames, list(self.object_count_history), color=accent2, linewidth=1.5)
        ax.fill_between(frames, list(self.object_count_history), alpha=0.2, color=accent2)
        ax.set_xlabel('Frame', color='white', fontsize=12)
        ax.set_ylabel('Objects Detected', color='white', fontsize=12)
        ax.set_title('Objects Detected Over Time', color='white', fontsize=14, fontweight='bold')
        ax.tick_params(colors='gray')
        ax.grid(alpha=0.15, color='gray')
        ax.spines['bottom'].set_color('gray')
        ax.spines['left'].set_color('gray')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        path2 = os.path.join(output_dir, 'objects_vs_frames.png')
        fig.savefig(path2, dpi=150, bbox_inches='tight', facecolor=fig_color)
        plt.close(fig)
        saved.append(path2)
        
        # 3. Motion Intensity
        fig, ax = plt.subplots(figsize=(10, 5), facecolor=fig_color)
        ax.set_facecolor(fig_color)
        ax.plot(frames, list(self.motion_intensity_history), color='#f59e0b', linewidth=1.5)
        ax.fill_between(frames, list(self.motion_intensity_history), alpha=0.2, color='#f59e0b')
        ax.set_xlabel('Frame', color='white', fontsize=12)
        ax.set_ylabel('Motion Intensity (%)', color='white', fontsize=12)
        ax.set_title('Motion Intensity Over Time', color='white', fontsize=14, fontweight='bold')
        ax.tick_params(colors='gray')
        ax.grid(alpha=0.15, color='gray')
        ax.spines['bottom'].set_color('gray')
        ax.spines['left'].set_color('gray')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        path3 = os.path.join(output_dir, 'motion_intensity.png')
        fig.savefig(path3, dpi=150, bbox_inches='tight', facecolor=fig_color)
        plt.close(fig)
        saved.append(path3)
        
        # 4. Processing Time
        fig, ax = plt.subplots(figsize=(10, 5), facecolor=fig_color)
        ax.set_facecolor(fig_color)
        ax.plot(frames, list(self.processing_time_history), color='#10b981', linewidth=1.5)
        ax.fill_between(frames, list(self.processing_time_history), alpha=0.2, color='#10b981')
        ax.set_xlabel('Frame', color='white', fontsize=12)
        ax.set_ylabel('Processing Time (ms)', color='white', fontsize=12)
        ax.set_title('Processing Time Per Frame', color='white', fontsize=14, fontweight='bold')
        ax.tick_params(colors='gray')
        ax.grid(alpha=0.15, color='gray')
        ax.spines['bottom'].set_color('gray')
        ax.spines['left'].set_color('gray')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        path4 = os.path.join(output_dir, 'processing_time.png')
        fig.savefig(path4, dpi=150, bbox_inches='tight', facecolor=fig_color)
        plt.close(fig)
        saved.append(path4)
        
        return saved

    def reset(self):
        """Reset all metrics."""
        self.fps_history.clear()
        self.object_count_history.clear()
        self.processing_time_history.clear()
        self.motion_intensity_history.clear()
        self.frame_timestamps.clear()
        self._last_time = None
        self.total_frames = 0
        self.total_detections = 0
        self.max_objects = 0
        self.start_time = time.time()


def calculate_iou(box1, box2):
    """Calculate Intersection over Union between two bounding boxes (x,y,w,h)."""
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2
    
    xi1 = max(x1, x2)
    yi1 = max(y1, y2)
    xi2 = min(x1 + w1, x2 + w2)
    yi2 = min(y1 + h1, y2 + h2)
    
    inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)
    union_area = w1 * h1 + w2 * h2 - inter_area
    
    return inter_area / union_area if union_area > 0 else 0
