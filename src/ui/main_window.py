"""
Main Application Window
========================
Integrates all UI panels and connects them to the processing pipeline.
Runs video processing in a background QThread for smooth UI.
"""

import os
import sys
import time
import cv2
import numpy as np

from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                              QFileDialog, QMessageBox, QApplication)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QImage

from ui.styles import MAIN_STYLESHEET
from ui.navbar import NavBar
from ui.sidebar import Sidebar
from ui.video_panel import VideoPanel
from ui.analytics_panel import AnalyticsPanel
from utils.helpers import frame_to_qpixmap, save_screenshot, ensure_dirs
from utils.visualization import (colorize_mask, create_detection_view,
                                  draw_trajectories, draw_centroids,
                                  draw_direction_arrows, draw_bounding_boxes,
                                  generate_heatmap)


class ProcessingThread(QThread):
    """Background thread for video processing pipeline."""
    
    # Signals to update UI
    frame_ready = pyqtSignal(np.ndarray, np.ndarray, np.ndarray, np.ndarray)
    metrics_ready = pyqtSignal(float, int, float, float, int)
    log_message = pyqtSignal(str)
    progress_update = pyqtSignal(float)
    processing_finished = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, video_path, preprocessor, vibe, detector, tracker, perf_tracker):
        super().__init__()
        self.video_path = video_path
        self.preprocessor = preprocessor
        self.vibe = vibe
        self.detector = detector
        self.tracker = tracker
        self.perf_tracker = perf_tracker
        
        self._running = True
        self._paused = False
        self.save_video = False
        self.video_writer = None
        self.heatmap_accumulator = None

    def run(self):
        """Main processing loop."""
        from utils.video_io import VideoReader, VideoWriter
        
        try:
            reader = VideoReader(self.video_path)
            self.log_message.emit(f"Loaded: {reader.get_info()['filename']} "
                                  f"({reader.width}x{reader.height} @ {reader.fps:.1f}fps)")
            
            # Reset algorithms
            self.vibe.reset()
            self.tracker.reset()
            self.perf_tracker.reset()
            self.heatmap_accumulator = None
            
            # Setup video writer if saving
            if self.save_video:
                out_path = os.path.join("outputs", "videos",
                    f"output_{int(time.time())}.mp4")
                self.video_writer = VideoWriter(out_path, reader.fps, 640, 480)
                self.log_message.emit(f"Recording to: {out_path}")
            
            frame_count = 0
            
            while self._running:
                # Handle pause
                while self._paused and self._running:
                    self.msleep(100)
                
                if not self._running:
                    break
                
                ret, frame = reader.read()
                if not ret:
                    break
                
                start_time = time.time()
                
                # Step 1: Preprocess
                processed = self.preprocessor.process(frame)
                
                # Step 2: ViBe background subtraction
                fg_mask = self.vibe.apply(processed)
                
                # Step 3: Detect objects
                detections, cleaned_mask = self.detector.detect(fg_mask)
                
                # Step 4: Track objects
                tracks = self.tracker.update(detections)
                
                processing_time = time.time() - start_time
                
                # Step 5: Update metrics
                self.perf_tracker.update(len(detections), processing_time, fg_mask)
                
                # Step 6: Create visualizations
                # Resize original for display
                display_frame = cv2.resize(processed, (640, 480))
                
                # Colorized mask
                mask_colored = colorize_mask(cleaned_mask)
                if mask_colored.shape[:2] != (480, 640):
                    mask_colored = cv2.resize(mask_colored, (640, 480))
                
                # Detection view (boxes + labels)
                detection_frame = display_frame.copy()
                detection_frame = draw_bounding_boxes(detection_frame, tracks)
                detection_frame = draw_centroids(detection_frame, tracks)
                
                # Trajectory view (trails + arrows)
                trajectory_frame = display_frame.copy()
                trajectory_frame = draw_trajectories(trajectory_frame, tracks)
                trajectory_frame = draw_direction_arrows(trajectory_frame, tracks)
                trajectory_frame = draw_centroids(trajectory_frame, tracks)
                
                # Update heatmap accumulator
                if self.heatmap_accumulator is None:
                    self.heatmap_accumulator = np.zeros(fg_mask.shape[:2], dtype=np.float32)
                if cleaned_mask.shape == self.heatmap_accumulator.shape:
                    self.heatmap_accumulator += (cleaned_mask.astype(np.float32) / 255.0)
                
                # Save frame if recording
                if self.video_writer:
                    combined = create_detection_view(display_frame, tracks)
                    self.video_writer.write(combined)
                
                # Emit signals
                self.frame_ready.emit(display_frame, mask_colored,
                                      detection_frame, trajectory_frame)
                
                fps = self.perf_tracker.get_current_fps()
                motion = self.perf_tracker.get_motion_intensity()
                self.metrics_ready.emit(fps, len(tracks), motion,
                                        processing_time * 1000,
                                        self.perf_tracker.total_frames)
                
                # Log significant events
                if frame_count == 0:
                    self.log_message.emit("ViBe model initialized from first frame")
                if len(detections) > 0 and frame_count % 30 == 0:
                    self.log_message.emit(f"Tracking {len(tracks)} objects")
                
                # Progress
                progress = reader.get_progress() * 100
                self.progress_update.emit(progress)
                
                frame_count += 1
                
                # Small delay to prevent UI overload
                self.msleep(1)
            
            # Cleanup
            reader.release()
            if self.video_writer:
                self.video_writer.release()
                self.log_message.emit("Video saved successfully")
            
            self.log_message.emit(f"Processing complete. {frame_count} frames processed.")
            self.processing_finished.emit()
            
        except Exception as e:
            self.error_occurred.emit(str(e))

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False

    def stop(self):
        self._running = False
        self._paused = False


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ViBe Surveillance System — Moving Object Detection & Trajectory Tracking")
        self.setMinimumSize(1200, 700)
        self.setStyleSheet(MAIN_STYLESHEET)
        
        ensure_dirs()
        
        # Initialize processing components
        from core.vibe import ViBe
        from core.preprocessor import Preprocessor
        from core.detector import ObjectDetector
        from core.tracker import CentroidTracker
        from evaluation.metrics import PerformanceTracker
        
        self.vibe = ViBe()
        self.preprocessor = Preprocessor()
        self.detector = ObjectDetector()
        self.tracker = CentroidTracker()
        self.perf_tracker = PerformanceTracker()
        
        self.processing_thread = None
        self.video_path = None
        self.is_paused = False
        
        # Store current frames for screenshots
        self._current_frames = {}
        
        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        """Construct the UI layout."""
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Top navbar
        self.navbar = NavBar()
        main_layout.addWidget(self.navbar)
        
        # Content area: sidebar + video + analytics
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Left sidebar
        self.sidebar = Sidebar()
        content_layout.addWidget(self.sidebar)
        
        # Center video panel
        self.video_panel = VideoPanel()
        content_layout.addWidget(self.video_panel, stretch=1)
        
        # Right analytics panel
        self.analytics = AnalyticsPanel()
        content_layout.addWidget(self.analytics)
        
        main_layout.addLayout(content_layout)

    def _connect_signals(self):
        """Wire up all UI signals to handlers."""
        self.sidebar.upload_clicked.connect(self._on_upload)
        self.sidebar.start_clicked.connect(self._on_start)
        self.sidebar.pause_clicked.connect(self._on_pause)
        self.sidebar.stop_clicked.connect(self._on_stop)
        self.sidebar.save_clicked.connect(self._on_save)
        self.sidebar.screenshot_clicked.connect(self._on_screenshot)
        self.sidebar.export_graphs_clicked.connect(self._on_export_graphs)
        self.sidebar.sensitivity_changed.connect(self._on_sensitivity_change)
        self.sidebar.trail_length_changed.connect(self._on_trail_change)
        self.sidebar.preprocessing_changed.connect(self._on_preprocessing_change)

    def _on_upload(self):
        """Handle video file upload."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Video File", "dataset",
            "Video Files (*.mp4 *.avi *.mkv *.mov *.wmv);;All Files (*)"
        )
        if path:
            self.video_path = path
            filename = os.path.basename(path)
            self.navbar.set_video_name(filename)
            self.sidebar.set_video_loaded(True)
            self.analytics.add_log_entry(f"Video loaded: {filename}")
            self.analytics.set_system_status("Video Loaded — Ready", '#ffffff')
            
            # Extract first frame for immediate preview
            try:
                cap = cv2.VideoCapture(path)
                ret, frame = cap.read()
                if ret:
                    processed = self.preprocessor.process(frame)
                    display_frame = cv2.resize(processed, (640, 480))
                    self.video_panel.show_preview(frame_to_qpixmap(display_frame))
                cap.release()
            except Exception as e:
                self.analytics.add_log_entry(f"Preview error: {e}")

    def _on_start(self):
        """Start video processing."""
        if not self.video_path:
            QMessageBox.warning(self, "No Video", "Please upload a video first.")
            return
        
        if self.processing_thread and self.processing_thread.isRunning():
            return
        
        # Reset state
        self.vibe.reset()
        self.tracker.reset()
        self.perf_tracker.reset()
        self.analytics.clear_all()
        self.is_paused = False
        
        # Create and start processing thread
        self.processing_thread = ProcessingThread(
            self.video_path, self.preprocessor, self.vibe,
            self.detector, self.tracker, self.perf_tracker
        )
        
        self.processing_thread.frame_ready.connect(self._on_frame_ready)
        self.processing_thread.metrics_ready.connect(self._on_metrics_ready)
        self.processing_thread.log_message.connect(self.analytics.add_log_entry)
        self.processing_thread.progress_update.connect(self.sidebar.set_progress)
        self.processing_thread.processing_finished.connect(self._on_processing_done)
        self.processing_thread.error_occurred.connect(self._on_error)
        
        self.processing_thread.start()
        
        self.sidebar.set_processing_state(True)
        self.navbar.set_status('running')
        self.analytics.set_system_status("Processing...", '#10b981')
        self.analytics.add_log_entry("Detection started")

    def _on_pause(self):
        """Toggle pause/resume."""
        if not self.processing_thread:
            return
        
        if self.is_paused:
            self.processing_thread.resume()
            self.is_paused = False
            self.navbar.set_status('running')
            self.analytics.set_system_status("Processing...", '#10b981')
            self.sidebar.btn_pause.setText("⏸ Pause")
            self.analytics.add_log_entry("Resumed processing")
        else:
            self.processing_thread.pause()
            self.is_paused = True
            self.navbar.set_status('paused')
            self.analytics.set_system_status("Paused", '#f59e0b')
            self.sidebar.btn_pause.setText("▶ Resume")
            self.analytics.add_log_entry("Processing paused")

    def _on_stop(self):
        """Stop video processing."""
        if self.processing_thread:
            self.processing_thread.stop()
            self.processing_thread.wait(3000)
            self.processing_thread = None
        
        self.sidebar.set_processing_state(False)
        self.sidebar.btn_pause.setText("⏸ Pause")
        self.sidebar.set_video_loaded(True)
        self.navbar.set_status('stopped')
        self.analytics.set_system_status("Stopped", '#ef4444')
        self.analytics.add_log_entry("Processing stopped by user")
        self.is_paused = False

    def _on_save(self):
        """Toggle video recording."""
        if self.processing_thread:
            self.processing_thread.save_video = not self.processing_thread.save_video
            if self.processing_thread.save_video:
                self.sidebar.btn_save.setText("🔴")
                self.sidebar.btn_save.setStyleSheet("color: #ef4444;")
                self.analytics.add_log_entry("Video recording started")
            else:
                self.sidebar.btn_save.setText("💾")
                self.sidebar.btn_save.setStyleSheet("")
                self.analytics.add_log_entry("Video recording stopped")

    def _on_screenshot(self):
        """Save screenshot of current detection view."""
        if 'detection' in self._current_frames:
            path = save_screenshot(self._current_frames['detection'])
            self.analytics.add_log_entry(f"Screenshot saved: {os.path.basename(path)}")

    def _on_export_graphs(self):
        """Export performance graphs."""
        saved = self.perf_tracker.generate_report_graphs()
        if saved:
            self.analytics.add_log_entry(f"Exported {len(saved)} graphs to outputs/graphs/")
        else:
            self.analytics.add_log_entry("Not enough data to generate graphs")

    def _on_sensitivity_change(self, value):
        """Update detection sensitivity."""
        self.detector.min_area = value

    def _on_trail_change(self, value):
        """Update trajectory trail length."""
        self.tracker.max_history = value

    def _on_preprocessing_change(self, settings):
        """Update preprocessing pipeline settings."""
        self.preprocessor.enable_resize = settings.get('resize', True)
        self.preprocessor.enable_gaussian = settings.get('gaussian', True)
        self.preprocessor.enable_median = settings.get('median', False)
        self.preprocessor.enable_clahe = settings.get('clahe', True)

    def _on_frame_ready(self, original, mask, detection, trajectory):
        """Handle processed frames from the background thread."""
        self._current_frames = {
            'original': original,
            'mask': mask,
            'detection': detection,
            'trajectory': trajectory,
        }
        
        self.video_panel.update_frames(
            frame_to_qpixmap(original),
            frame_to_qpixmap(mask),
            frame_to_qpixmap(detection),
            frame_to_qpixmap(trajectory)
        )

    def _on_metrics_ready(self, fps, num_objects, motion, proc_time, total_frames):
        """Handle metrics update from the background thread."""
        self.analytics.update_metrics(fps, num_objects, motion, proc_time, total_frames)

    def _on_processing_done(self):
        """Handle processing completion."""
        self.sidebar.set_processing_state(False)
        self.sidebar.set_video_loaded(True)
        self.sidebar.set_progress(100)
        self.navbar.set_status('idle')
        self.analytics.set_system_status("Complete", '#ffffff')
        self.analytics.add_log_entry("Processing finished successfully")
        
        # Auto-export graphs
        saved = self.perf_tracker.generate_report_graphs()
        if saved:
            self.analytics.add_log_entry(f"Auto-exported {len(saved)} performance graphs")

    def _on_error(self, error_msg):
        """Handle processing errors."""
        self.sidebar.set_processing_state(False)
        self.navbar.set_status('stopped')
        self.analytics.set_system_status(f"Error: {error_msg}", '#ef4444')
        self.analytics.add_log_entry(f"ERROR: {error_msg}")
        QMessageBox.critical(self, "Processing Error", error_msg)

    def closeEvent(self, event):
        """Clean up on window close."""
        if self.processing_thread and self.processing_thread.isRunning():
            self.processing_thread.stop()
            self.processing_thread.wait(2000)
        event.accept()
