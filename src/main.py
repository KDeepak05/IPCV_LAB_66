"""
ViBe Surveillance System
========================
Moving Object Detection and Trajectory Tracking using ViBe Background Extractor

Entry point for the application.
Run: python main.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from ui.main_window import MainWindow


def main():
    """Launch the ViBe Surveillance System application."""
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    
    # Set application-wide font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Create and show main window
    window = MainWindow()
    window.showMaximized()
    
    print("=" * 60)
    print("  ViBe Surveillance System")
    print("  Moving Object Detection & Trajectory Tracking")
    print("=" * 60)
    print("  Application started successfully!")
    print("  Upload a video file to begin detection.")
    print("=" * 60)
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
