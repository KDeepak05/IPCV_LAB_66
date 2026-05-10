"""
Left Sidebar
=============
Contains video controls, detection settings, and action buttons in a compact layout.
"""

from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, QSlider,
                              QCheckBox, QGroupBox, QSizePolicy, QGridLayout)
from PyQt5.QtCore import Qt, pyqtSignal
from ui.widgets import ModernButton


class Sidebar(QFrame):
    """Left sidebar with controls and settings."""

    # Signals
    upload_clicked = pyqtSignal()
    start_clicked = pyqtSignal()
    pause_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    save_clicked = pyqtSignal()
    screenshot_clicked = pyqtSignal()
    export_graphs_clicked = pyqtSignal()
    
    # Settings signals
    sensitivity_changed = pyqtSignal(int)
    trail_length_changed = pyqtSignal(int)
    preprocessing_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(220)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # === VIDEO CONTROLS ===
        self.btn_upload = ModernButton("📂 Upload", primary=True)
        self.btn_upload.clicked.connect(self.upload_clicked.emit)
        layout.addWidget(self.btn_upload)
        
        self.btn_start = ModernButton("▶ Start")
        self.btn_start.clicked.connect(self.start_clicked.emit)
        self.btn_start.setEnabled(False)
        layout.addWidget(self.btn_start)
        
        play_ctrl_layout = QHBoxLayout()
        play_ctrl_layout.setSpacing(4)
        
        self.btn_pause = ModernButton("⏸ Pause")
        self.btn_pause.clicked.connect(self.pause_clicked.emit)
        self.btn_pause.setEnabled(False)
        play_ctrl_layout.addWidget(self.btn_pause)
        
        self.btn_stop = ModernButton("⏹ Stop", danger=True)
        self.btn_stop.clicked.connect(self.stop_clicked.emit)
        self.btn_stop.setEnabled(False)
        play_ctrl_layout.addWidget(self.btn_stop)
        
        layout.addLayout(play_ctrl_layout)
        
        # === OUTPUT ACTIONS ===
        output_layout = QHBoxLayout()
        output_layout.setSpacing(4)
        
        self.btn_save = ModernButton("💾")
        self.btn_save.setToolTip("Save Video")
        self.btn_save.clicked.connect(self.save_clicked.emit)
        self.btn_save.setEnabled(False)
        output_layout.addWidget(self.btn_save)
        
        self.btn_screenshot = ModernButton("📸")
        self.btn_screenshot.setToolTip("Screenshot")
        self.btn_screenshot.clicked.connect(self.screenshot_clicked.emit)
        self.btn_screenshot.setEnabled(False)
        output_layout.addWidget(self.btn_screenshot)
        
        self.btn_export = ModernButton("📊")
        self.btn_export.setToolTip("Export Graphs")
        self.btn_export.clicked.connect(self.export_graphs_clicked.emit)
        self.btn_export.setEnabled(False)
        output_layout.addWidget(self.btn_export)
        
        layout.addLayout(output_layout)
        
        # === SETTINGS ===
        settings_group = QGroupBox("SETTINGS")
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.setSpacing(6)
        settings_layout.setContentsMargins(8, 12, 8, 8)
        
        # Detection sensitivity
        sens_label_layout = QHBoxLayout()
        sens_label = QLabel("Sensitivity")
        sens_label.setStyleSheet("color: #94a3b8; font-size: 10px;")
        self.sens_value_label = QLabel("500")
        self.sens_value_label.setStyleSheet("color: #64748b; font-size: 10px;")
        sens_label_layout.addWidget(sens_label)
        sens_label_layout.addStretch()
        sens_label_layout.addWidget(self.sens_value_label)
        settings_layout.addLayout(sens_label_layout)
        
        self.sensitivity_slider = QSlider(Qt.Horizontal)
        self.sensitivity_slider.setRange(100, 2000)
        self.sensitivity_slider.setValue(500)
        self.sensitivity_slider.valueChanged.connect(self.sensitivity_changed.emit)
        self.sensitivity_slider.valueChanged.connect(lambda v: self.sens_value_label.setText(str(v)))
        settings_layout.addWidget(self.sensitivity_slider)
        
        # Trail length
        trail_label_layout = QHBoxLayout()
        trail_label = QLabel("Trail Length")
        trail_label.setStyleSheet("color: #94a3b8; font-size: 10px;")
        self.trail_value_label = QLabel("60")
        self.trail_value_label.setStyleSheet("color: #64748b; font-size: 10px;")
        trail_label_layout.addWidget(trail_label)
        trail_label_layout.addStretch()
        trail_label_layout.addWidget(self.trail_value_label)
        settings_layout.addLayout(trail_label_layout)
        
        self.trail_slider = QSlider(Qt.Horizontal)
        self.trail_slider.setRange(10, 120)
        self.trail_slider.setValue(60)
        self.trail_slider.valueChanged.connect(self.trail_length_changed.emit)
        self.trail_slider.valueChanged.connect(lambda v: self.trail_value_label.setText(str(v)))
        settings_layout.addWidget(self.trail_slider)
        
        # Preprocessing toggles in a compact grid
        settings_layout.addSpacing(4)
        preproc_label = QLabel("Filters")
        preproc_label.setStyleSheet("color: #94a3b8; font-size: 10px;")
        settings_layout.addWidget(preproc_label)
        
        grid = QGridLayout()
        grid.setSpacing(4)
        self.chk_resize = QCheckBox("Resize")
        self.chk_resize.setChecked(True)
        self.chk_gaussian = QCheckBox("Blur")
        self.chk_gaussian.setChecked(True)
        self.chk_median = QCheckBox("Median")
        self.chk_median.setChecked(False)
        self.chk_clahe = QCheckBox("CLAHE")
        self.chk_clahe.setChecked(True)
        
        grid.addWidget(self.chk_resize, 0, 0)
        grid.addWidget(self.chk_gaussian, 0, 1)
        grid.addWidget(self.chk_median, 1, 0)
        grid.addWidget(self.chk_clahe, 1, 1)
        settings_layout.addLayout(grid)
        
        for chk in [self.chk_resize, self.chk_gaussian, self.chk_median, self.chk_clahe]:
            chk.stateChanged.connect(self._emit_preprocessing)
        
        layout.addWidget(settings_group)
        
        # Push everything up
        layout.addStretch()
        
        # Progress bar
        from PyQt5.QtWidgets import QProgressBar
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setFixedHeight(4) # Thinner
        self.progress.setTextVisible(False)
        layout.addWidget(self.progress)

    def _emit_preprocessing(self):
        settings = {
            'resize': self.chk_resize.isChecked(),
            'gaussian': self.chk_gaussian.isChecked(),
            'median': self.chk_median.isChecked(),
            'clahe': self.chk_clahe.isChecked(),
        }
        self.preprocessing_changed.emit(settings)

    def set_processing_state(self, is_processing):
        self.btn_upload.setEnabled(not is_processing)
        self.btn_start.setEnabled(not is_processing)
        self.btn_pause.setEnabled(is_processing)
        self.btn_stop.setEnabled(is_processing)
        self.btn_save.setEnabled(is_processing)
        self.btn_screenshot.setEnabled(is_processing)
        self.btn_export.setEnabled(True)

    def set_video_loaded(self, loaded):
        self.btn_start.setEnabled(loaded)

    def set_progress(self, value):
        self.progress.setValue(int(value))
