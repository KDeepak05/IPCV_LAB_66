"""
Center Video Panel
==================
Tabbed view displaying: Live Detection, Original, Foreground Mask, Trajectories.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QSizePolicy)
from PyQt5.QtCore import Qt
from ui.widgets import VideoDisplayLabel


class VideoPanel(QWidget):
    """Center panel with tabbed video display."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 8, 8, 8)
        layout.setSpacing(0)
        
        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setObjectName("videoTabs")
        self.tabs.setDocumentMode(True)
        
        # Create 4 display panels
        self.detection_view = VideoDisplayLabel("Live Detection")
        self.original_view = VideoDisplayLabel("Original Feed")
        self.mask_view = VideoDisplayLabel("Foreground Mask")
        self.trajectory_view = VideoDisplayLabel("Trajectories")
        
        # The VideoDisplayLabel adds background, we want it to be seamless in the tab
        for view in [self.detection_view, self.original_view, self.mask_view, self.trajectory_view]:
            view.setStyleSheet("""
                QLabel {
                    background: #1e293b;
                    border: none;
                    border-radius: 0px 0px 8px 8px;
                    color: #64748b;
                    font-size: 13px;
                }
            """)
        
        # Add tabs
        self.tabs.addTab(self.detection_view, "🎯 Live Detection")
        self.tabs.addTab(self.original_view, "📹 Original")
        self.tabs.addTab(self.mask_view, "🎭 Mask")
        self.tabs.addTab(self.trajectory_view, "📍 Trajectories")
        
        layout.addWidget(self.tabs)
        
        # Keep track of latest frames for active tab updates
        self._latest_frames = {
            0: None, # detection
            1: None, # original
            2: None, # mask
            3: None  # trajectory
        }
        
        self.tabs.currentChanged.connect(self._on_tab_changed)

    def _on_tab_changed(self, index):
        """Force a refresh of the newly active tab if paused."""
        frame = self._latest_frames.get(index)
        if frame:
            if index == 0:
                self.detection_view.set_frame(frame)
            elif index == 1:
                self.original_view.set_frame(frame)
            elif index == 2:
                self.mask_view.set_frame(frame)
            elif index == 3:
                self.trajectory_view.set_frame(frame)

    def update_frames(self, original, mask, detection, trajectory):
        """Store latest frames and update only the active tab for performance."""
        self._latest_frames[1] = original
        self._latest_frames[2] = mask
        self._latest_frames[0] = detection
        self._latest_frames[3] = trajectory
        
        self._on_tab_changed(self.tabs.currentIndex())

    def show_preview(self, pixmap):
        """Show an initial preview frame across all tabs."""
        self._latest_frames[1] = pixmap
        self._latest_frames[2] = pixmap
        self._latest_frames[0] = pixmap
        self._latest_frames[3] = pixmap
        self._on_tab_changed(self.tabs.currentIndex())

    def clear_all(self):
        """Clear all video displays."""
        for view in [self.original_view, self.mask_view,
                     self.detection_view, self.trajectory_view]:
            view.clear()
            view.setText(view._title)
