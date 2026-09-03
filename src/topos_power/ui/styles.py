STYLESHEET = """
/* ========== 全局 ========== */
QMainWindow { background-color: #0d1117; }

QWidget {
    font-family: "Segoe UI", "Microsoft YaHei", "Roboto", sans-serif;
    color: #e6edf3;
    font-size: 13px;
}

QFrame { background-color: transparent; }

/* ========== 分组框 ========== */
QGroupBox {
    border: 1px solid #30363d;
    border-radius: 6px;
    margin-top: 8px;
    padding-top: 10px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
    color: #58a6ff;
}

/* ========== 标签 ========== */
QLabel { color: #8b949e; }

QLabel#TimeValue {
    color: #58a6ff;
    font-size: 36px;
    font-weight: bold;
    font-family: Consolas, "SF Mono", monospace;
}

/* ========== 模式切换按钮 ========== */
QToolButton#ModeSwitch {
    background-color: #21262d;
    border: 1px solid #30363d;
    color: #8b949e;
    padding: 8px 20px;
    font-size: 13px;
    font-weight: bold;
}

QToolButton#ModeSwitch[first="true"] {
    border-radius: 6px 0 0 6px;
    border-right: none;
}

QToolButton#ModeSwitch[last="true"] {
    border-radius: 0 6px 6px 0;
    border-left: 1px solid #30363d;
}

QToolButton#ModeSwitch:checked {
    background-color: #1f6feb;
    border-color: #1f6feb;
    color: #ffffff;
}

QToolButton#ModeSwitch:hover:!checked {
    background-color: #30363d;
    color: #e6edf3;
}

/* ========== 主操作按钮 ========== */
QPushButton#ActionBtn {
    background-color: #2da44e;
    border: 1px solid #2da44e;
    border-radius: 8px;
    color: #ffffff;
    font-weight: bold;
    font-family: "Segoe UI", sans-serif;
    font-size: 16px;
    padding: 4px;
}

QPushButton#ActionBtn:hover {
    background-color: #4ac26b;
    border-color: #4ac26b;
}

QPushButton#ActionBtn:pressed {
    background-color: #238636;
    border-color: #238636;
    padding-top: 7px;
    padding-left: 6px;
}

QPushButton#ActionBtn[state="running"] {
    background-color: #cf222e;
    border: 1px solid #cf222e;
}

QPushButton#ActionBtn[state="running"]:hover {
    background-color: #ff4444;
    border-color: #ff4444;
}

QPushButton#ActionBtn[state="running"]:pressed {
    background-color: #a40e26;
    border-color: #a40e26;
}

QPushButton:disabled {
    background-color: #21262d;
    color: #484f58;
    border: 1px solid #30363d;
}

/* ========== 进度条 ========== */
QProgressBar {
    border: none;
    background-color: #21262d;
    border-radius: 4px;
    height: 8px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #2ea043;
}

/* ========== 复选框 ========== */
QCheckBox {
    color: #8b949e;
    spacing: 10px;
    padding: 5px 0;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    background-color: #21262d;
    border: 2px solid #30363d;
    border-radius: 4px;
}

QCheckBox::indicator:checked {
    background-color: #238636;
    border-color: #238636;
    image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 12 12'><polyline points='2.5,6.5 5,9 9.5,3' fill='none' stroke='white' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/></svg>");
}

/* ========== 单选按钮 ========== */
QRadioButton {
    color: #e6edf3;
    spacing: 10px;
    padding: 5px 0;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    background-color: #21262d;
    border: 2px solid #30363d;
    border-radius: 10px;
}

QRadioButton::indicator:checked {
    background-color: #58a6ff;
    border-color: #58a6ff;
}

QRadioButton::indicator:hover {
    border-color: #58a6ff;
}

/* ========== 数字输入框 ========== */
QSpinBox {
    background-color: #21262d;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 5px 28px 5px 10px;
    color: #e6edf3;
    min-height: 28px;
    min-width: 60px;
}

QSpinBox:focus { border-color: #58a6ff; }

QSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 22px;
    height: 15px;
    border: none;
    background-color: transparent;
}

QSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 22px;
    height: 15px;
    border: none;
    background-color: transparent;
}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background-color: #484f58;
}

QSpinBox::up-arrow {
    image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'><polyline points='1,7 6,1 11,7' fill='none' stroke='%238b949e' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/></svg>");
    width: 12px;
    height: 8px;
}

QSpinBox::down-arrow {
    image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'><polyline points='1,1 6,7 11,1' fill='none' stroke='%238b949e' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/></svg>");
    width: 12px;
    height: 8px;
}

/* ========== 滚动条 ========== */
QScrollBar:vertical {
    border: none;
    background: #0d1117;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #30363d;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover { background: #58a6ff; }

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
    subcontrol-origin: margin;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

/* ========== 工具提示 ========== */
QToolTip {
    background-color: #30363d;
    color: #e6edf3;
    border: 1px solid #484f58;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 12px;
}
"""

# 滑动条内联样式（较大手柄）
SLIDER_STYLE = """
    QSlider::groove:horizontal {
        border: 1px solid #30363d;
        height: 10px;
        background: #21262d;
        margin: 2px 0;
        border-radius: 5px;
    }
    QSlider::handle:horizontal {
        background: #58a6ff;
        border: 1px solid #58a6ff;
        width: 24px;
        height: 24px;
        margin: -7px 0;
        border-radius: 12px;
    }
    QSlider::handle:horizontal:hover {
        background: #79c0ff;
        border-color: #79c0ff;
    }
    QSlider::handle:horizontal:pressed {
        background: #1f6feb;
        border-color: #1f6feb;
    }
    QSlider::sub-page:horizontal {
        background: #1f6feb;
        border: 1px solid #30363d;
        height: 10px;
        border-radius: 5px;
    }
"""

