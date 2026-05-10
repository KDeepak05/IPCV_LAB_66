"""
Custom Widgets
==============
Reusable custom PyQt5 widgets: GlowButton, StatCard, StatusIndicator.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QFrame, QSizePolicy, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, pyqtProperty, QSize
from PyQt5.QtGui import QColor, QPainter, QPen, QFont


class ModernButton(QPushButton):
    """Modern flat button with clean hover effects."""

    def __init__(self, text="", parent=None, primary=False, danger=False):
        super().__init__(text, parent)
        if primary:
            self.setObjectName("primaryBtn")
        elif danger:
            self.setObjectName("dangerBtn")
        
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(36)


class SimpleStat(QWidget):
    """Minimalist metric display."""

    def __init__(self, title="Metric", value="0", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)
        
        # Value
        self.value_label = QLabel(str(value))
        self.value_label.setStyleSheet("color: #f8fafc; font-size: 18px; font-weight: bold;")
        self.value_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.value_label)
        
        # Title
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #94a3b8; font-size: 10px; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px;")
        self.title_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.title_label)

    def set_value(self, value):
        """Update the displayed value."""
        self.value_label.setText(str(value))

    def set_color(self, color_hex):
        """Change the value text color."""
        self.value_label.setStyleSheet(f"color: {color_hex}; font-size: 18px; font-weight: bold;")


class StatusIndicator(QWidget):
    """Animated status dot indicator (green/yellow/red)."""

    STATUS_COLORS = {
        'running': QColor(16, 185, 129),    # Green
        'paused': QColor(245, 158, 11),     # Orange/Yellow
        'stopped': QColor(239, 68, 68),     # Red
        'idle': QColor(100, 116, 139),      # Gray
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(14, 14)
        self._status = 'idle'
        self._opacity = 1.0
        self._pulse_dir = -1
        
        # Pulse animation timer
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._pulse)
        self._timer.start(50)

    def set_status(self, status):
        """Set status: 'running', 'paused', 'stopped', 'idle'."""
        self._status = status

    def _pulse(self):
        """Animate the pulse effect for running state."""
        if self._status == 'running':
            self._opacity += self._pulse_dir * 0.04
            if self._opacity <= 0.3:
                self._pulse_dir = 1
            elif self._opacity >= 1.0:
                self._pulse_dir = -1
        else:
            self._opacity = 1.0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        color = self.STATUS_COLORS.get(self._status, self.STATUS_COLORS['idle'])
        color.setAlphaF(self._opacity)
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(2, 2, 10, 10)


class VideoDisplayLabel(QLabel):
    """QLabel optimized for video frame display with title overlay."""

    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setObjectName("videoLabel")
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(200, 150)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setScaledContents(False)
        self._title = title
        self.setText(f"  {title}  ")
        self.setStyleSheet("""
            QLabel {
                background: #1e293b;
                border: 1px solid #334155;
                border-radius: 6px;
                color: #64748b;
                font-size: 13px;
            }
        """)

    def set_frame(self, pixmap):
        """Set a frame pixmap, scaled to fit the label."""
        if pixmap and not pixmap.isNull():
            scaled = pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(scaled)

    def resizeEvent(self, event):
        """Re-scale pixmap when the label is resized."""
        pix = self.pixmap()
        if pix and not pix.isNull():
            self.setPixmap(pix.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        super().resizeEvent(event)
