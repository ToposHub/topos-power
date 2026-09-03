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

/* ========== Topos Power modern surface ========== */
QWidget#AppSurface {
    background-color: #111318;
}

QFrame#Card, QGroupBox#Card {
    background-color: #181a20;
    border: 1px solid #2a2d35;
    border-radius: 14px;
}

QFrame#HeaderFrame {
    background: transparent;
}

QLabel#BrandMark {
    background-color: #3478f6;
    border-radius: 15px;
    color: #ffffff;
    font-size: 18px;
    font-weight: bold;
    min-width: 30px;
    max-width: 30px;
    min-height: 30px;
    max-height: 30px;
    qproperty-alignment: AlignCenter;
}

QLabel#BrandTitle {
    color: #f5f5f7;
    font-size: 20px;
    font-weight: bold;
}

QLabel#BrandSubtitle, QLabel#SecondaryText {
    color: #8d9099;
    font-size: 11px;
}

QLabel#PlatformBadge, QLabel#StatusBadge {
    background-color: #20232b;
    border: 1px solid #30343e;
    border-radius: 10px;
    color: #aeb4c0;
    padding: 5px 10px;
    font-size: 11px;
}

QLabel#StatusBadge[state="running"] {
    background-color: #253b69;
    border-color: #3478f6;
    color: #d9e6ff;
}

QLabel#StatusBadge[state="ready"] {
    background-color: #20232b;
    border-color: #30343e;
    color: #aeb4c0;
}

QFrame#ModeBar {
    background-color: #1b1d23;
    border: 1px solid #2b2e37;
    border-radius: 11px;
}

QToolButton#ModeSwitch {
    background: transparent;
    border: none;
    border-radius: 8px;
    color: #9297a3;
    font-size: 13px;
    font-weight: 500;
    padding: 8px 22px;
}

QToolButton#ModeSwitch:hover {
    background-color: #252831;
    color: #e9ebf0;
}

QToolButton#ModeSwitch:checked {
    background-color: #3478f6;
    color: #ffffff;
}

QLabel#CardEyebrow {
    color: #8d9099;
    font-size: 11px;
    font-weight: 500;
}

QLabel#CardTitle {
    color: #f5f5f7;
    font-size: 15px;
    font-weight: 500;
}

QLabel#TimeValue {
    color: #f5f5f7;
    font-size: 44px;
    font-weight: 500;
    letter-spacing: 0px;
}

QLabel#CountdownTarget {
    color: #9297a3;
    font-size: 12px;
}

QProgressBar#CountdownProgress {
    background-color: #292c34;
    border: none;
    border-radius: 4px;
    min-height: 7px;
    max-height: 7px;
}

QProgressBar#CountdownProgress::chunk {
    background-color: #3478f6;
    border-radius: 4px;
}

QLabel#LargeSettingValue {
    color: #f5f5f7;
    font-size: 23px;
    font-weight: 500;
}

QLabel#SettingCaption {
    color: #8d9099;
    font-size: 12px;
}

QFrame#Divider {
    background-color: #2a2d35;
    min-height: 1px;
    max-height: 1px;
}

QRadioButton, QCheckBox {
    color: #d9dce3;
    spacing: 8px;
    min-height: 22px;
    padding: 0px;
}

QRadioButton:hover, QCheckBox:hover {
    color: #ffffff;
}

QPushButton#PrimaryAction {
    background-color: #3478f6;
    border: none;
    border-radius: 11px;
    color: #ffffff;
    font-size: 14px;
    font-weight: 500;
    min-height: 44px;
}

QPushButton#PrimaryAction:hover {
    background-color: #4b8bff;
}

QPushButton#PrimaryAction:pressed {
    background-color: #2864d3;
}

QPushButton#PrimaryAction[state="running"] {
    background-color: #d94f5c;
}

QPushButton#SystemAction {
    background-color: #23262e;
    border: 1px solid #343842;
    border-radius: 8px;
    color: #aeb4c0;
    padding: 5px 12px;
}

QPushButton#SystemAction:hover {
    background-color: #2b2f38;
    color: #ffffff;
}

QLabel#StatusLabel {
    color: #8d9099;
    font-size: 11px;
    min-height: 18px;
}

QPushButton#HelpButton {
    background-color: transparent;
    border: 1px solid #343842;
    border-radius: 8px;
    color: #aeb4c0;
    min-height: 22px;
    padding: 2px 10px;
}

QPushButton#HelpButton:hover {
    background-color: #23262e;
    color: #ffffff;
}

QPushButton#HelpButton:pressed {
    background-color: #2b2f38;
}

QComboBox#LanguageCombo {
    background-color: #20232b;
    border: 1px solid #343842;
    border-radius: 8px;
    color: #c8ccd5;
    min-height: 22px;
    min-width: 48px;
    padding: 2px 16px 2px 8px;
}

QComboBox#LanguageCombo:hover, QComboBox#LanguageCombo:focus {
    border-color: #3478f6;
    color: #ffffff;
}

QComboBox#LanguageCombo::drop-down {
    border: none;
    width: 20px;
}

QComboBox#LanguageCombo QAbstractItemView {
    background-color: #20232b;
    border: 1px solid #343842;
    color: #f5f5f7;
    selection-background-color: #3478f6;
}

QGroupBox#SystemSettingsCard {
    background-color: #181a20;
    border: 1px solid #2a2d35;
    border-radius: 14px;
    margin-top: 8px;
    padding-top: 12px;
}

QGroupBox#SystemSettingsCard::title {
    color: #f5f5f7;
    left: 14px;
    padding: 0 6px;
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
