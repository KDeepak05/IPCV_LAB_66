"""
UI Styles — Soft Charcoal Dark Theme
====================================
Sleek, professional soft dark gray theme (zinc). Easier on the eyes than pure black.
"""

COLORS = {
    'bg_primary': '#18181b',      # zinc-900
    'bg_secondary': '#27272a',    # zinc-800
    'bg_hover': '#3f3f46',        # zinc-700
    'accent_primary': '#ffffff',  # pure white
    'accent_hover': '#e4e4e7',    # zinc-200
    'text_primary': '#f4f4f5',    # zinc-50
    'text_secondary': '#a1a1aa',  # zinc-400
    'border': '#3f3f46',          # zinc-700
}

MAIN_STYLESHEET = """
/* ===== GLOBAL ===== */
QMainWindow, QWidget#centralWidget, QWidget#analyticsContent {
    background-color: #18181b;
    color: #f4f4f5;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    font-size: 13px;
}

/* ===== SCROLLBAR ===== */
QScrollArea {
    border: none;
    background-color: transparent;
}
QScrollArea > QWidget > QWidget {
    background-color: transparent;
}
QScrollBar:vertical {
    background: transparent;
    width: 4px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #3f3f46;
    border-radius: 2px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover {
    background: #52525b;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar:horizontal {
    background: transparent;
    height: 4px;
    margin: 0;
}
QScrollBar::handle:horizontal {
    background: #3f3f46;
    border-radius: 2px;
    min-width: 20px;
}
QScrollBar::handle:horizontal:hover {
    background: #52525b;
}

/* ===== LABELS ===== */
QLabel {
    color: #f4f4f5;
    background: transparent;
}
QLabel#sectionTitle {
    color: #a1a1aa;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 8px 0px 4px 0px;
}
QLabel#panelTitle {
    color: #a1a1aa;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    padding: 6px;
}
QLabel#videoLabel {
    background: #27272a;
    border: 1px solid #3f3f46;
    border-radius: 6px;
    padding: 0px;
}

/* ===== BUTTONS ===== */
QPushButton {
    background: #27272a;
    color: #f4f4f5;
    border: 1px solid #3f3f46;
    border-radius: 4px;
    padding: 8px 16px;
    font-size: 12px;
    font-weight: 500;
}
QPushButton:hover {
    background: #3f3f46;
    border: 1px solid #52525b;
}
QPushButton:pressed {
    background: #18181b;
}
QPushButton:disabled {
    background: transparent;
    color: #71717a;
    border: 1px dashed #3f3f46;
}
QPushButton#primaryBtn {
    background: #ffffff;
    color: #18181b;
    border: none;
    font-weight: 600;
}
QPushButton#primaryBtn:hover {
    background: #e4e4e7;
}
QPushButton#dangerBtn {
    background: transparent;
    color: #ef4444;
    border: 1px solid #7f1d1d;
}
QPushButton#dangerBtn:hover {
    background: #7f1d1d;
    color: #fca5a5;
}

/* ===== SLIDERS ===== */
QSlider::groove:horizontal {
    background: #3f3f46;
    height: 4px;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #ffffff;
    width: 12px;
    height: 12px;
    margin: -4px 0;
    border-radius: 6px;
}
QSlider::handle:horizontal:hover {
    background: #e4e4e7;
}
QSlider::sub-page:horizontal {
    background: #a1a1aa;
    border-radius: 2px;
}

/* ===== CHECKBOX ===== */
QCheckBox {
    color: #d4d4d8;
    spacing: 6px;
    font-size: 12px;
}
QCheckBox::indicator {
    width: 14px;
    height: 14px;
    border-radius: 3px;
    border: 1px solid #52525b;
    background: #27272a;
}
QCheckBox::indicator:hover {
    border-color: #71717a;
}
QCheckBox::indicator:checked {
    background: #ffffff;
    border: 1px solid #ffffff;
}

/* ===== GROUP BOX ===== */
QGroupBox {
    background: transparent;
    border: 1px solid #3f3f46;
    border-radius: 6px;
    margin-top: 10px;
    padding: 12px 8px 8px 8px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 4px;
    color: #a1a1aa;
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
}

/* ===== PROGRESS BAR ===== */
QProgressBar {
    background: #27272a;
    border: none;
    border-radius: 2px;
    height: 4px;
    text-align: center;
    color: transparent;
}
QProgressBar::chunk {
    background: #ffffff;
    border-radius: 2px;
}

/* ===== FRAME / CARD ===== */
QFrame#navbar {
    background: #18181b;
    border-bottom: 1px solid #27272a;
    padding: 8px 16px;
}
QFrame#sidebar {
    background: #18181b;
    border-right: 1px solid #27272a;
}

/* ===== TOOLTIPS ===== */
QToolTip {
    background: #27272a;
    color: #f4f4f5;
    border: 1px solid #3f3f46;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 11px;
}

/* ===== TABS ===== */
QTabWidget::pane {
    border: 1px solid #3f3f46;
    border-top: none;
    background: #27272a;
    border-radius: 0px 0px 6px 6px;
}
QTabBar::tab {
    background: #18181b;
    color: #a1a1aa;
    border: 1px solid #3f3f46;
    border-bottom: none;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 12px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}
QTabBar::tab:hover {
    background: #27272a;
    color: #f4f4f5;
}
QTabBar::tab:selected {
    background: #27272a;
    color: #ffffff;
    border-top: 2px solid #ffffff;
}
"""
