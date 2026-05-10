"""
Top Navigation Bar
==================
Displays project title, current video name, and processing status.
"""

from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy
from PyQt5.QtCore import Qt
from ui.widgets import StatusIndicator


class NavBar(QFrame):
    """Top navigation bar with project title and status indicator."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("navbar")
        self.setFixedHeight(56)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(16)
        
        # Project icon/title
        icon_label = QLabel("◉")
        icon_label.setStyleSheet("color: #ffffff; font-size: 22px; background: transparent;")
        layout.addWidget(icon_label)
        
        title = QLabel("ViBe Surveillance System")
        title.setStyleSheet("""
            color: #f8fafc; font-size: 18px; font-weight: bold;
            background: transparent;
        """)
        layout.addWidget(title)
        
        # Separator
        sep = QLabel("│")
        sep.setStyleSheet("color: #94a3b8; font-size: 18px; background: transparent;")
        layout.addWidget(sep)
        
        # Subtitle
        subtitle = QLabel("Moving Object Detection & Trajectory Tracking")
        subtitle.setStyleSheet("color: #94a3b8; font-size: 12px; background: transparent;")
        layout.addWidget(subtitle)
        
        layout.addStretch()
        
        # Video filename
        self.video_label = QLabel("No video loaded")
        self.video_label.setStyleSheet("color: #94a3b8; font-size: 12px; background: transparent;")
        layout.addWidget(self.video_label)
        
        # Status indicator
        self.status_indicator = StatusIndicator()
        layout.addWidget(self.status_indicator)
        
        # Status text
        self.status_text = QLabel("Idle")
        self.status_text.setStyleSheet("color: #94a3b8; font-size: 12px; font-weight: bold; background: transparent;")
        layout.addWidget(self.status_text)

    def set_video_name(self, name):
        """Update displayed video filename."""
        self.video_label.setText(f"📁 {name}")
        self.video_label.setStyleSheet("color: #ffffff; font-size: 12px; background: transparent;")

    def set_status(self, status):
        """Set processing status: 'running', 'paused', 'stopped', 'idle'."""
        self.status_indicator.set_status(status)
        labels = {
            'running': ('● Processing', '#10b981'),
            'paused': ('● Paused', '#f59e0b'),
            'stopped': ('● Stopped', '#ef4444'),
            'idle': ('● Idle', '#64748b'),
        }
        text, color = labels.get(status, ('● Idle', '#64748b'))
        self.status_text.setText(text)
        self.status_text.setStyleSheet(
            f"color: {color}; font-size: 12px; font-weight: bold; background: transparent;"
        )
