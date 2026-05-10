"""
Right Analytics Panel
=====================
Minimalist real-time statistics dashboard: FPS, object count, motion intensity,
and a single clean chart.
"""

from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel,
                              QSizePolicy, QScrollArea, QWidget)
from PyQt5.QtCore import Qt
from ui.widgets import SimpleStat
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from collections import deque


class MiniChart(FigureCanvasQTAgg):
    """Small embedded matplotlib chart for real-time data."""

    def __init__(self, title="", color='#ffffff', parent=None, width=2.5, height=1.5):
        self.fig = Figure(figsize=(width, height), dpi=80)
        self.fig.patch.set_facecolor('#18181b')
        super().__init__(self.fig)
        
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#18181b')
        self.ax.set_title(title, color='#94a3b8', fontsize=8, pad=4)
        self.ax.tick_params(colors='#64748b', labelsize=6)
        self.ax.spines['bottom'].set_color('#27272a')
        self.ax.spines['left'].set_color('#27272a')
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.grid(alpha=0.1, color='gray')
        
        self._color = color
        self._data = deque(maxlen=60)
        self.fig.tight_layout(pad=1.0)
        self.setStyleSheet("background: transparent; border: none;")

    def update_data(self, value):
        self._data.append(value)
        data_list = list(self._data)
        
        self.ax.clear()
        self.ax.set_facecolor('#18181b')
        self.ax.plot(data_list, color=self._color, linewidth=1.2, alpha=0.9)
        self.ax.fill_between(range(len(data_list)), data_list, alpha=0.15, color=self._color)
        self.ax.tick_params(colors='#64748b', labelsize=6)
        self.ax.spines['bottom'].set_color('#27272a')
        self.ax.spines['left'].set_color('#27272a')
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.grid(alpha=0.1, color='gray')
        
        try:
            self.fig.tight_layout(pad=1.0)
            self.draw_idle()
        except Exception:
            pass

    def clear_data(self):
        self._data.clear()
        self.ax.clear()
        self.ax.set_facecolor('#18181b')
        self.draw_idle()


class AnalyticsPanel(QFrame):
    """Right panel showing clean, minimalist analytics."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar") # Reuse sidebar style (border-left instead of full card)
        self.setStyleSheet("border-left: 1px solid #1e293b; background: #0f172a;")
        self.setFixedWidth(200) # Thinner
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        content = QWidget()
        content.setObjectName("analyticsContent")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(16)
        
        # System status
        self.status_label = QLabel("⬤  System Ready")
        self.status_label.setStyleSheet("color: #10b981; font-size: 11px; font-weight: bold; background: transparent; border: none;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Divider
        div1 = QFrame()
        div1.setFrameShape(QFrame.HLine)
        div1.setStyleSheet("background: #1e293b; border: none; min-height: 1px; max-height: 1px;")
        layout.addWidget(div1)
        
        # Simple stats grid
        grid1 = QHBoxLayout()
        self.fps_card = SimpleStat("FPS", "0.0")
        self.fps_card.set_color('#ffffff')
        grid1.addWidget(self.fps_card)
        self.objects_card = SimpleStat("Objects", "0")
        self.objects_card.set_color('#7c3aed')
        grid1.addWidget(self.objects_card)
        layout.addLayout(grid1)
        
        grid2 = QHBoxLayout()
        self.motion_card = SimpleStat("Motion %", "0.0")
        self.motion_card.set_color('#f59e0b')
        grid2.addWidget(self.motion_card)
        self.proc_card = SimpleStat("Proc ms", "0.0")
        self.proc_card.set_color('#10b981')
        grid2.addWidget(self.proc_card)
        layout.addLayout(grid2)
        
        self.frames_card = SimpleStat("Total Frames", "0")
        self.frames_card.set_color('#94a3b8')
        layout.addWidget(self.frames_card)
        
        # Divider
        div2 = QFrame()
        div2.setFrameShape(QFrame.HLine)
        div2.setStyleSheet("background: #1e293b; border: none; min-height: 1px; max-height: 1px;")
        layout.addWidget(div2)
        
        # Single FPS Chart
        self.fps_chart = MiniChart(title="FPS OVER TIME", color='#ffffff')
        self.fps_chart.setMinimumHeight(100)
        self.fps_chart.setMaximumHeight(120)
        layout.addWidget(self.fps_chart)
        
        layout.addStretch()
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def update_metrics(self, fps, num_objects, motion_intensity, proc_time, total_frames):
        self.fps_card.set_value(f"{fps:.1f}")
        self.objects_card.set_value(str(num_objects))
        self.motion_card.set_value(f"{motion_intensity:.1f}")
        self.proc_card.set_value(f"{proc_time:.1f}")
        self.frames_card.set_value(str(total_frames))
        
        if fps >= 25:
            self.fps_card.set_color('#10b981')
        elif fps >= 15:
            self.fps_card.set_color('#f59e0b')
        else:
            self.fps_card.set_color('#ef4444')
            
        self.fps_chart.update_data(fps)

    def add_log_entry(self, message):
        """Mock method to prevent breaking main_window.py that still calls this."""
        print(f"Log: {message}")

    def set_system_status(self, status, color='#10b981'):
        self.status_label.setText(f"⬤  {status}")
        self.status_label.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: bold; background: transparent; border: none;")

    def clear_all(self):
        self.fps_card.set_value("0.0")
        self.objects_card.set_value("0")
        self.motion_card.set_value("0.0")
        self.proc_card.set_value("0.0")
        self.frames_card.set_value("0")
        self.fps_chart.clear_data()
        self.set_system_status("System Ready", '#10b981')
