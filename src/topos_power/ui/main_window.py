import threading
import time
import platform
from datetime import datetime, timedelta

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QCheckBox,
                             QProgressBar, QFrame, QGroupBox, QSpinBox,
                             QSystemTrayIcon, QMenu, QStyle, QSlider,
                             QRadioButton, QButtonGroup, QStackedWidget,
                             QToolButton, QGraphicsOpacityEffect,
                             QSizePolicy, QMessageBox, QComboBox)
from PyQt6.QtCore import (Qt, QTimer, pyqtSignal, QPropertyAnimation,
                          QEasingCurve)
from PyQt6.QtGui import QIcon, QFont

from ..config import APP_NAME
from ..core.localization import LanguageManager
from ..core.power_manager import PowerManager
from .styles import SLIDER_STYLE, STYLESHEET


class PowerTimer(QMainWindow):
    """合并版：定时关机 + 定时睡眠/关屏"""

    # 后台的关机创建/取消完成后，安全地回到 GUI 线程更新界面。
    shutdown_operation_finished = pyqtSignal(str, bool)
    sleep_operation_finished = pyqtSignal(str, bool)
    idle_settings_finished = pyqtSignal(bool)

    # 顶层功能模式
    FUNC_SHUTDOWN = 0
    FUNC_SLEEP = 1

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} - 电源定时工具")
        self.setMinimumSize(560, 760)
        self.resize(620, 800)

        self.setStyleSheet(STYLESHEET)

        # ── 状态变量 ──
        self.current_func = self.FUNC_SHUTDOWN
        self.total_duration = 0
        self.target_time = None
        self.timer_id = None
        self.is_running = False
        self.screen_off_done = False
        self.screen_off_in_progress = False
        self.pending_both_sleep = False
        self.options_animation = None
        self.caffeinate_proc = None
        self.shutdown_operation = None
        self.cancel_after_shutdown_scheduled = False
        self.language_manager = LanguageManager(self)
        self.language_manager.language_changed.connect(
            self._apply_language)
        self.language_manager = LanguageManager(self)
        self.language_manager.language_changed.connect(
            self._apply_language)
        self.shutdown_operation_finished.connect(
            self._on_shutdown_operation_finished)
        self.sleep_operation_finished.connect(
            self._on_sleep_operation_finished)
        self.idle_settings_finished.connect(self._on_idle_applied)

        # 系统托盘
        self._setup_tray()
        # UI
        self._setup_ui()

    # ═══════════ 系统托盘 ═══════════
    def _setup_tray(self):
        icon = QIcon.fromTheme("computer")
        if icon.isNull():
            icon = self.style().standardIcon(
                QStyle.StandardPixmap.SP_ComputerIcon)
        self.tray_icon = QSystemTrayIcon(icon, self)

        tray_menu = QMenu()
        self.tray_toggle_action = tray_menu.addAction("显示/隐藏")
        self.tray_toggle_action.triggered.connect(self._toggle_window)
        tray_menu.addSeparator()
        self.tray_quit_action = tray_menu.addAction("退出")
        self.tray_quit_action.triggered.connect(self._quit_app)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def _toggle_window(self):
        if self.isMinimized():
            self.showNormal()
        elif self.isHidden():
            self.show()
        else:
            self.hide()

    # ═══════════ UI 构建 ═══════════
    def _tr(self, key, **values):
        return self.language_manager.text(key, **values)

    def _setup_ui(self):
        main_widget = QWidget()
        main_widget.setObjectName("AppSurface")
        self.setCentralWidget(main_widget)

        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(22, 16, 22, 14)
        layout.setSpacing(10)

        # ── 品牌头部 ──
        header_frame = QFrame()
        header_frame.setObjectName("HeaderFrame")
        header_frame.setFixedHeight(44)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(9)

        brand_mark = QLabel("⌁")
        brand_mark.setObjectName("BrandMark")
        header_layout.addWidget(brand_mark)

        title_column = QVBoxLayout()
        title_column.setSpacing(0)
        title_text = QLabel(APP_NAME)
        title_text.setObjectName("BrandTitle")
        self.subtitle = QLabel(self._tr("brand_subtitle"))
        self.subtitle.setObjectName("BrandSubtitle")
        title_column.addWidget(title_text)
        title_column.addWidget(self.subtitle)
        header_layout.addLayout(title_column)
        header_layout.addStretch()

        platform_name = {
            "Darwin": "macOS",
            "Windows": "Windows",
            "Linux": "Linux",
        }.get(platform.system(), platform.system())
        platform_badge = QLabel(platform_name)
        platform_badge.setObjectName("PlatformBadge")
        platform_badge.setFixedSize(68, 30)
        header_layout.addWidget(platform_badge)

        self.help_btn = QPushButton(self._tr("help"))
        self.help_btn.setObjectName("HelpButton")
        self.help_btn.setFixedSize(56, 30)
        self.help_btn.setToolTip(self._tr("help_tip"))
        self.help_btn.clicked.connect(self._show_help)
        header_layout.addWidget(self.help_btn)

        self.language_combo = QComboBox()
        self.language_combo.setObjectName("LanguageCombo")
        self.language_combo.setFixedSize(90, 30)
        for code, label in LanguageManager.languages:
            self.language_combo.addItem(label, code)
        current_index = self.language_combo.findData(
            self.language_manager.language)
        if current_index >= 0:
            self.language_combo.setCurrentIndex(current_index)
        self.language_combo.currentIndexChanged.connect(
            self._on_language_changed)
        header_layout.addWidget(self.language_combo)
        layout.addWidget(header_frame)

        # ── 顶层功能切换 ──
        switch_frame = QFrame()
        switch_frame.setObjectName("ModeBar")
        switch_frame.setFixedHeight(46)
        switch_layout = QHBoxLayout(switch_frame)
        switch_layout.setContentsMargins(4, 4, 4, 4)
        switch_layout.setSpacing(4)

        self.btn_shutdown = QToolButton()
        self.btn_shutdown.setObjectName("ModeSwitch")
        self.btn_shutdown.setFixedHeight(36)
        self.btn_shutdown.setText(self._tr("tab_shutdown"))
        self.btn_shutdown.setCheckable(True)
        self.btn_shutdown.setChecked(True)
        self.btn_shutdown.clicked.connect(
            lambda: self._switch_func(self.FUNC_SHUTDOWN))

        self.btn_sleep = QToolButton()
        self.btn_sleep.setObjectName("ModeSwitch")
        self.btn_sleep.setFixedHeight(36)
        self.btn_sleep.setText(self._tr("tab_sleep"))
        self.btn_sleep.setCheckable(True)
        self.btn_sleep.setChecked(False)
        self.btn_sleep.clicked.connect(
            lambda: self._switch_func(self.FUNC_SLEEP))

        switch_layout.addWidget(self.btn_shutdown, 1)
        switch_layout.addWidget(self.btn_sleep, 1)
        layout.addWidget(switch_frame)

        # ── 倒计时主卡片 ──
        countdown_card = QFrame()
        countdown_card.setObjectName("Card")
        countdown_card.setMinimumHeight(136)
        countdown_layout = QVBoxLayout(countdown_card)
        countdown_layout.setContentsMargins(16, 14, 16, 14)
        countdown_layout.setSpacing(7)

        countdown_header = QHBoxLayout()
        self.eyebrow = QLabel(self._tr("next_action"))
        self.eyebrow.setObjectName("CardEyebrow")
        countdown_header.addWidget(self.eyebrow)
        countdown_header.addStretch()

        self.status_badge = QLabel(self._tr("ready"))
        self.status_badge.setObjectName("StatusBadge")
        self.status_badge.setProperty("state", "ready")
        countdown_header.addWidget(self.status_badge)
        countdown_layout.addLayout(countdown_header)

        self.time_label = QLabel("00:00:00")
        self.time_label.setObjectName("TimeValue")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setMinimumHeight(58)
        self.time_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        countdown_layout.addWidget(self.time_label)

        self.pbar = QProgressBar()
        self.pbar.setObjectName("CountdownProgress")
        self.pbar.setValue(0)
        self.pbar.setTextVisible(False)
        countdown_layout.addWidget(self.pbar)

        target_row = QHBoxLayout()
        self.exec_time_label = QLabel("")
        self.exec_time_label.setObjectName("CountdownTarget")
        self.exec_time_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter)
        target_row.addWidget(self.exec_time_label)
        countdown_layout.addLayout(target_row)
        layout.addWidget(countdown_card)

        # ── 时间设置卡片 ──
        settings_card = QFrame()
        settings_card.setObjectName("Card")
        settings_layout = QVBoxLayout(settings_card)
        settings_layout.setContentsMargins(16, 14, 16, 14)
        settings_layout.setSpacing(7)

        settings_header = QHBoxLayout()
        self.settings_title = QLabel(self._tr("execution_time"))
        self.settings_title.setObjectName("CardTitle")
        settings_header.addWidget(self.settings_title)
        settings_header.addStretch()

        self.slider_value_label = QLabel(
            self._tr("duration_hours", hours=1))
        self.slider_value_label.setObjectName("LargeSettingValue")
        settings_header.addWidget(self.slider_value_label)
        settings_layout.addLayout(settings_header)

        self.setting_caption = QLabel(self._tr("execution_caption"))
        self.setting_caption.setObjectName("SettingCaption")
        settings_layout.addWidget(self.setting_caption)

        self.custom_slider = QSlider(Qt.Orientation.Horizontal)
        self.custom_slider.setRange(1, 1440)
        self.custom_slider.setValue(60)
        self.custom_slider.setStyleSheet(SLIDER_STYLE)
        self.custom_slider.valueChanged.connect(self._update_slider_label)
        settings_layout.addWidget(self.custom_slider)

        slider_bounds = QHBoxLayout()
        self.min_caption = QLabel(self._tr("one_minute"))
        self.min_caption.setObjectName("SecondaryText")
        self.max_caption = QLabel(self._tr("twenty_four_hours"))
        self.max_caption.setObjectName("SecondaryText")
        slider_bounds.addWidget(self.min_caption)
        slider_bounds.addStretch()
        slider_bounds.addWidget(self.max_caption)
        settings_layout.addLayout(slider_bounds)
        layout.addWidget(settings_card)

        # ── 模式选项卡片 ──
        self.options_card = QFrame()
        self.options_card.setObjectName("Card")
        self.options_card.setFixedHeight(124)
        options_card_layout = QVBoxLayout(self.options_card)
        options_card_layout.setContentsMargins(16, 13, 16, 13)
        options_card_layout.setSpacing(5)
        self.options_card.setMinimumHeight(108)

        options_header = QHBoxLayout()
        self.options_title = QLabel(self._tr("options"))
        self.options_title.setObjectName("CardTitle")
        options_header.addWidget(self.options_title)
        options_header.addStretch()
        self.options_summary = QLabel(self._tr("shutdown_summary"))
        self.options_summary.setObjectName("SecondaryText")
        options_header.addWidget(self.options_summary)
        options_card_layout.addLayout(options_header)

        self.options_stack = QStackedWidget()
        self.options_stack.setObjectName("OptionsStack")
        self.options_stack.setFixedHeight(70)
        self.options_stack.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.options_opacity = QGraphicsOpacityEffect(self.options_stack)
        self.options_stack.setGraphicsEffect(self.options_opacity)
        self.options_opacity.setOpacity(1.0)

        # Page 0: 关机选项
        shutdown_options = QFrame()
        sd_layout = QVBoxLayout(shutdown_options)
        sd_layout.setContentsMargins(0, 4, 0, 0)
        sd_layout.setSpacing(4)

        self.sd_hint = QLabel(self._tr("shutdown_hint"))
        self.sd_hint.setWordWrap(True)
        self.sd_hint.setObjectName("SecondaryText")
        sd_layout.addWidget(self.sd_hint)
        sd_layout.addStretch()
        self.options_stack.addWidget(shutdown_options)

        # Page 1: 睡眠选项
        sleep_options = QFrame()
        sl_layout = QVBoxLayout(sleep_options)
        sl_layout.setContentsMargins(0, 4, 0, 0)
        sl_layout.setSpacing(4)

        self.mode_btn_group = QButtonGroup(self)
        radio_row = QHBoxLayout()
        radio_row.setSpacing(12)

        self.radio_sleep = QRadioButton(self._tr("sleep_mode"))
        self.radio_sleep.setToolTip(self._tr("sleep_mode"))
        self.radio_sleep.setChecked(True)
        self.mode_btn_group.addButton(self.radio_sleep, 0)
        radio_row.addWidget(self.radio_sleep)

        self.radio_screen = QRadioButton(self._tr("screen_mode"))
        self.radio_screen.setToolTip(self._tr("screen_mode_tip"))
        self.mode_btn_group.addButton(self.radio_screen, 1)
        radio_row.addWidget(self.radio_screen)

        self.radio_both = QRadioButton(self._tr("both_mode"))
        self.radio_both.setToolTip(self._tr("both_mode_tip"))
        self.mode_btn_group.addButton(self.radio_both, 2)
        radio_row.addWidget(self.radio_both)
        radio_row.addStretch()
        sl_layout.addLayout(radio_row)

        self.screen_offset_frame = QFrame()
        offset_layout = QHBoxLayout(self.screen_offset_frame)
        offset_layout.setContentsMargins(8, 1, 4, 1)

        self.offset_label = QLabel(self._tr("offset_label"))
        self.offset_label.setObjectName("SecondaryText")
        offset_layout.addWidget(self.offset_label)

        self.screen_offset_spin = QSpinBox()
        self.screen_offset_spin.setRange(1, 60)
        self.screen_offset_spin.setValue(5)
        self.screen_offset_spin.setSuffix(self._tr("minutes_suffix"))
        self.screen_offset_spin.valueChanged.connect(
            self._update_exec_time_hint)
        offset_layout.addWidget(self.screen_offset_spin)

        self.offset_suffix = QLabel(self._tr("offset_suffix"))
        self.offset_suffix.setObjectName("SecondaryText")
        offset_layout.addWidget(self.offset_suffix)
        offset_layout.addStretch()
        self.screen_offset_frame.setVisible(False)
        self.screen_offset_frame.setMinimumWidth(184)
        self.screen_offset_frame.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        options_row = QHBoxLayout()
        options_row.setSpacing(10)
        options_row.addWidget(self.screen_offset_frame)
        self.lock_checkbox = QCheckBox(self._tr("lock_screen"))
        self.lock_checkbox.setChecked(True)
        self.lock_checkbox.setMinimumWidth(132)
        options_row.addWidget(self.lock_checkbox)
        self.prevent_sleep_checkbox = QCheckBox(self._tr("prevent_sleep"))
        self.prevent_sleep_checkbox.setToolTip(
            self._tr("prevent_sleep_tip"))
        self.prevent_sleep_checkbox.setChecked(True)
        self.prevent_sleep_checkbox.setMinimumWidth(135)
        options_row.addWidget(self.prevent_sleep_checkbox)
        options_row.addStretch()
        sl_layout.addLayout(options_row)

        self.mode_btn_group.buttonClicked.connect(self._on_sleep_mode_changed)
        self.options_stack.addWidget(sleep_options)
        options_card_layout.addWidget(self.options_stack)
        layout.addWidget(self.options_card)

        # ── macOS 系统空闲睡眠设置 ──
        self.idle_group = None
        if platform.system() == "Darwin":
            self.idle_group = QGroupBox(self._tr("idle_title"))
            self.idle_group.setObjectName("SystemSettingsCard")
            idle_layout = QVBoxLayout(self.idle_group)
            idle_layout.setSpacing(8)

            self.idle_hint = QLabel(self._tr("idle_hint"))
            self.idle_hint.setObjectName("SecondaryText")
            self.idle_hint.setWordWrap(True)
            idle_layout.addWidget(self.idle_hint)

            idle_row = QHBoxLayout()
            idle_row.setSpacing(12)

            self.lbl_display = QLabel(self._tr("display_sleep"))
            self.lbl_display.setObjectName("SettingCaption")
            idle_row.addWidget(self.lbl_display)

            self.idle_display_spin = QSpinBox()
            self.idle_display_spin.setRange(0, 10080)
            self.idle_display_spin.setValue(10)
            self.idle_display_spin.setSuffix(self._tr("minutes_suffix"))
            self.idle_display_spin.setSpecialValueText(self._tr("never"))
            idle_row.addWidget(self.idle_display_spin)

            self.lbl_sleep = QLabel(self._tr("system_sleep"))
            self.lbl_sleep.setObjectName("SettingCaption")
            idle_row.addSpacing(8)
            idle_row.addWidget(self.lbl_sleep)

            self.idle_sleep_spin = QSpinBox()
            self.idle_sleep_spin.setRange(0, 10080)
            self.idle_sleep_spin.setValue(30)
            self.idle_sleep_spin.setSuffix(self._tr("minutes_suffix"))
            self.idle_sleep_spin.setSpecialValueText(self._tr("never"))
            idle_row.addWidget(self.idle_sleep_spin)

            idle_row.addStretch()
            self.idle_apply_btn = QPushButton(self._tr("save_settings"))
            self.idle_apply_btn.setObjectName("SystemAction")
            self.idle_apply_btn.clicked.connect(self._apply_idle_settings)
            idle_row.addWidget(self.idle_apply_btn)
            idle_layout.addLayout(idle_row)

            self._load_idle_settings()
            self.idle_group.setVisible(False)
            layout.addWidget(self.idle_group)

        # ── 主操作 ──
        self.action_btn = QPushButton(self._tr("start"))
        self.action_btn.setObjectName("PrimaryAction")
        self.action_btn.setMinimumHeight(44)
        self.action_btn.clicked.connect(self._toggle_action)
        layout.addWidget(self.action_btn)

        # ── 底部操作栏 ──
        self.info_text = QLabel()
        self.info_text.setWordWrap(True)
        self.info_text.setObjectName("SecondaryText")
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.addStretch()

        self.status_label = QLabel(self._tr("status_ready"))
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setFixedHeight(20)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_layout.addWidget(self.status_label)
        layout.addLayout(footer_layout)

        self._update_button_state()
        self._update_exec_time_hint()
        self._update_info_text()
    # ═══════════ 功能切换 ═══════════
    def _animate_options_transition(self):
        """让选项卡切换有轻量淡入效果，避免界面突然跳变。"""
        self.options_opacity.setOpacity(0.35)
        animation = QPropertyAnimation(self.options_opacity, b"opacity", self)
        animation.setDuration(180)
        animation.setStartValue(0.35)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.options_animation = animation
        animation.start()

    def _switch_func(self, func):
        """切换顶层功能（关机 / 睡眠）"""
        if self.is_running:
            return  # 运行中禁止切换

        self.current_func = func

        # 更新分段按钮状态
        self.btn_shutdown.setChecked(func == self.FUNC_SHUTDOWN)
        self.btn_sleep.setChecked(func == self.FUNC_SLEEP)

        # 切换选项面板
        self.options_stack.setCurrentIndex(func)
        self.options_summary.setText(
            self._tr("shutdown_summary")
            if func == self.FUNC_SHUTDOWN else self._tr("sleep_summary"))
        self._animate_options_transition()

        # macOS 空闲设置仅睡眠模式可见
        if self.idle_group:
            self.idle_group.setVisible(func == self.FUNC_SLEEP)

        self._update_exec_time_hint()
        self._update_info_text()

    def _on_language_changed(self, index):
        code = self.language_combo.itemData(index)
        if code:
            self.language_manager.set_language(code)

    def _apply_language(self, _language):
        """刷新当前界面的静态文案和动态预览。"""
        self.setWindowTitle(f"{APP_NAME} - {self._tr('window_title')}")
        self.subtitle.setText(self._tr("brand_subtitle"))
        self.help_btn.setText(self._tr("help"))
        self.help_btn.setToolTip(self._tr("help_tip"))
        self.tray_toggle_action.setText(self._tr("tray_toggle"))
        self.tray_quit_action.setText(self._tr("tray_quit"))
        self.btn_shutdown.setText(self._tr("tab_shutdown"))
        self.btn_sleep.setText(self._tr("tab_sleep"))
        self.eyebrow.setText(self._tr("next_action"))
        self.settings_title.setText(self._tr("execution_time"))
        self.setting_caption.setText(self._tr("execution_caption"))
        self.min_caption.setText(self._tr("one_minute"))
        self.max_caption.setText(self._tr("twenty_four_hours"))
        self.options_title.setText(self._tr("options"))
        self.sd_hint.setText(self._tr("shutdown_hint"))
        self.radio_sleep.setText(self._tr("sleep_mode"))
        self.radio_sleep.setToolTip(self._tr("sleep_mode"))
        self.radio_screen.setText(self._tr("screen_mode"))
        self.radio_screen.setToolTip(self._tr("screen_mode_tip"))
        self.radio_both.setText(self._tr("both_mode"))
        self.radio_both.setToolTip(self._tr("both_mode_tip"))
        self.offset_label.setText(self._tr("offset_label"))
        self.offset_suffix.setText(self._tr("offset_suffix"))
        self.screen_offset_spin.setSuffix(self._tr("minutes_suffix"))
        self.lock_checkbox.setText(self._tr("lock_screen"))
        self.prevent_sleep_checkbox.setText(self._tr("prevent_sleep"))
        self.prevent_sleep_checkbox.setToolTip(
            self._tr("prevent_sleep_tip"))
        if self.idle_group:
            self.idle_group.setTitle(self._tr("idle_title"))
            self.idle_hint.setText(self._tr("idle_hint"))
            self.lbl_display.setText(self._tr("display_sleep"))
            self.lbl_sleep.setText(self._tr("system_sleep"))
            self.idle_display_spin.setSuffix(self._tr("minutes_suffix"))
            self.idle_display_spin.setSpecialValueText(self._tr("never"))
            self.idle_sleep_spin.setSuffix(self._tr("minutes_suffix"))
            self.idle_sleep_spin.setSpecialValueText(self._tr("never"))
            self.idle_apply_btn.setText(self._tr("save_settings"))
        if self.current_func == self.FUNC_SLEEP:
            self._on_sleep_mode_changed()
        else:
            self.options_summary.setText(self._tr("shutdown_summary"))
        self._update_slider_label(self.custom_slider.value())
        self._update_button_state()
        self._update_info_text()
        if not self.is_running:
            self.status_label.setText(self._tr("status_ready"))

    # ═══════════ 辅助方法 ═══════════
    def _update_slider_label(self, value):
        # “提前关屏”不能大于总时长，否则会出现过去的预计时间，
        # 并在刚开始倒计时时立即关屏。
        self.screen_offset_spin.setMaximum(value)
        if value >= 60:
            hours = value // 60
            minutes = value % 60
            if minutes > 0:
                self.slider_value_label.setText(self._tr(
                    "duration_hours_minutes", hours=hours, minutes=minutes))
            else:
                self.slider_value_label.setText(
                    self._tr("duration_hours", hours=hours))
        else:
            self.slider_value_label.setText(
                self._tr("duration_minutes", value=value))
        self._update_exec_time_hint()

    def _update_exec_time_hint(self):
        minutes = self.custom_slider.value()
        exec_time = datetime.now() + timedelta(minutes=minutes)
        time_str = exec_time.strftime('%H:%M')

        if self.current_func == self.FUNC_SHUTDOWN:
            self.exec_time_label.setText(
                self._tr("preview_shutdown", time=time_str))
        else:
            mode = self._get_sleep_mode()
            if mode == PowerManager.MODE_SCREEN_OFF:
                self.exec_time_label.setText(
                    self._tr("preview_screen", time=time_str))
            elif mode == PowerManager.MODE_BOTH:
                offset = self.screen_offset_spin.value()
                screen_time = (datetime.now()
                               + timedelta(minutes=minutes - offset))
                self.exec_time_label.setText(
                    self._tr(
                        "preview_both",
                        screen_time=screen_time.strftime('%H:%M'),
                        sleep_time=time_str))
            else:
                self.exec_time_label.setText(
                    self._tr("preview_sleep", time=time_str))

    def _get_sleep_mode(self):
        checked_id = self.mode_btn_group.checkedId()
        if checked_id == 1:
            return PowerManager.MODE_SCREEN_OFF
        elif checked_id == 2:
            return PowerManager.MODE_BOTH
        return PowerManager.MODE_SLEEP

    def _on_sleep_mode_changed(self):
        mode = self._get_sleep_mode()
        self.screen_offset_frame.setVisible(
            mode == PowerManager.MODE_BOTH)
        screen_only = (mode == PowerManager.MODE_SCREEN_OFF)
        self.lock_checkbox.setVisible(not screen_only)
        self.prevent_sleep_checkbox.setVisible(not screen_only)
        mode_names = {
            PowerManager.MODE_SLEEP: self._tr("sleep_mode"),
            PowerManager.MODE_SCREEN_OFF: self._tr("screen_mode"),
            PowerManager.MODE_BOTH: self._tr("both_mode"),
        }
        self.options_summary.setText(mode_names[mode])
        self._update_exec_time_hint()

    def _show_help(self):
        """按需显示帮助内容，避免帮助文字长期占用主界面空间。"""
        QMessageBox.information(
            self,
            self._tr("help_title"),
            f"{self.info_text.text()}\n\n{self._tr('help_permissions')}",
        )

    def _update_info_text(self):
        if self.current_func == self.FUNC_SHUTDOWN:
            self.info_text.setText(self._tr("shutdown_info"))
        else:
            self.info_text.setText(self._tr("sleep_info"))

    def _update_button_state(self):
        if self.is_running:
            self.action_btn.setText(self._tr("stop"))
            self.action_btn.setProperty("state", "running")
        else:
            self.action_btn.setText(self._tr("start"))
            self.action_btn.setProperty("state", "normal")
        self.action_btn.style().unpolish(self.action_btn)
        self.action_btn.style().polish(self.action_btn)
        if hasattr(self, "status_badge"):
            self.status_badge.setText(
                self._tr("running") if self.is_running
                else self._tr("ready"))
            self.status_badge.setProperty(
                "state", "running" if self.is_running else "ready")
            self.status_badge.style().unpolish(self.status_badge)
            self.status_badge.style().polish(self.status_badge)

    def _set_controls_enabled(self, enabled):
        """统一启用/禁用输入控件"""
        self.custom_slider.setEnabled(enabled)
        self.btn_shutdown.setEnabled(enabled)
        self.btn_sleep.setEnabled(enabled)

        if self.current_func == self.FUNC_SLEEP:
            self.lock_checkbox.setEnabled(enabled)
            self.prevent_sleep_checkbox.setEnabled(enabled)
            self.screen_offset_spin.setEnabled(enabled)
            for btn in self.mode_btn_group.buttons():
                btn.setEnabled(enabled)

    # ═══════════ 核心逻辑 ═══════════
    def _toggle_action(self):
        if self.is_running:
            self._stop()
        else:
            self._start()

    def _start(self):
        if self.is_running:
            return

        self.total_duration = self.custom_slider.value() * 60
        self.screen_off_done = False
        self.screen_off_in_progress = False
        self.pending_both_sleep = False

        if self.current_func == self.FUNC_SHUTDOWN:
            # 关机模式：调度系统级关机
            self.shutdown_operation = "schedule"
            self.cancel_after_shutdown_scheduled = False
            threading.Thread(
                target=self._run_shutdown_operation,
                args=("schedule", self.total_duration),
                daemon=True).start()
        else:
            # 睡眠模式：阻止自动睡眠
            mode = self._get_sleep_mode()
            if (mode != PowerManager.MODE_SCREEN_OFF
                    and self.prevent_sleep_checkbox.isChecked()):
                self.caffeinate_proc = PowerManager.prevent_sleep()

        # 记录目标时间
        self.target_time = datetime.now() + timedelta(
            seconds=self.total_duration)

        # 关机计划需要先由系统确认创建成功，再开始倒计时；否则命令失败时
        # 界面会错误显示一个永远不会执行的倒计时。
        self.timer_id = QTimer(self)
        self.timer_id.timeout.connect(self._update_countdown)
        if self.current_func != self.FUNC_SHUTDOWN:
            self.timer_id.start(1000)
            self._update_countdown()

        # 禁用控件
        self.is_running = True
        self._set_controls_enabled(False)
        self._update_button_state()

        # 状态文本
        exec_time = (datetime.now()
                     + timedelta(seconds=self.total_duration))
        if self.current_func == self.FUNC_SHUTDOWN:
            self.status_label.setText(self._tr("shutdown_authorizing"))
        else:
            mode_names = {
                PowerManager.MODE_SLEEP: self._tr("sleep_mode"),
                PowerManager.MODE_SCREEN_OFF: self._tr("screen_mode"),
                PowerManager.MODE_BOTH: self._tr("both_mode"),
            }
            mode = self._get_sleep_mode()
            self.status_label.setText(
                self._tr("scheduled_action",
                         time=exec_time.strftime('%H:%M:%S'),
                         action=mode_names[mode]))
        self.status_label.setStyleSheet("color: #f85149; font-size: 12px;")

    def _run_shutdown_operation(self, operation, seconds=None):
        """在线程中执行需要授权的系统命令，并通过信号返回 GUI 线程。"""
        if operation == "schedule":
            success = PowerManager.shutdown(seconds)
        else:
            success = PowerManager.cancel_shutdown()
        self.shutdown_operation_finished.emit(operation, success)

    def _on_shutdown_operation_finished(self, operation, success):
        """处理关机计划的创建/取消结果，避免开始和停止发生竞态。"""
        if operation != self.shutdown_operation:
            return

        self.shutdown_operation = None
        if operation == "schedule":
            if not success:
                self._finish_stop(
                    self._tr("shutdown_create_failed"), "#f85149")
            elif self.cancel_after_shutdown_scheduled:
                self._begin_shutdown_cancel()
            elif self.is_running:
                self.timer_id.start(1000)
                self._update_countdown()
                exec_time = (datetime.now()
                             + timedelta(seconds=self.total_duration))
                self.status_label.setText(
                    self._tr("shutdown_scheduled",
                             time=exec_time.strftime('%H:%M:%S')))
                self.status_label.setStyleSheet(
                    "color: #f85149; font-size: 12px;")
            return

        if success:
            self._finish_stop(self._tr("shutdown_canceled"), "#58a6ff")
        else:
            # 此时系统关机计划可能依然有效，保留“停止运行”按钮供重试，
            # 不能错误地允许创建另一个计划。
            self.status_label.setText(self._tr("shutdown_cancel_failed"))
            self.status_label.setStyleSheet(
                "color: #f85149; font-size: 12px;")
            self.action_btn.setEnabled(True)

    def _begin_shutdown_cancel(self):
        self.shutdown_operation = "cancel"
        self.cancel_after_shutdown_scheduled = False
        self.status_label.setText(self._tr("shutdown_canceling"))
        self.status_label.setStyleSheet("color: #f85149; font-size: 12px;")
        threading.Thread(
            target=self._run_shutdown_operation,
            args=("cancel",), daemon=True).start()

    def _run_power_action(self, mode, lock=False, result_mode=None):
        """在线程中执行睡眠/关屏，并把真实结果送回 GUI 线程。"""
        operation = result_mode or mode
        if lock:
            if not PowerManager.lock_screen():
                self.sleep_operation_finished.emit(operation, False)
                return
            time.sleep(1)

        if mode == PowerManager.MODE_SLEEP:
            success = PowerManager.sleep()
        elif mode == PowerManager.MODE_SCREEN_OFF:
            success = PowerManager.screen_off()
        else:
            success = False
        self.sleep_operation_finished.emit(operation, success)

    def _run_both_action(self, lock=False):
        """按顺序执行关屏和睡眠，避免两个后台线程同时抢占电源状态。"""
        if lock:
            if not PowerManager.lock_screen():
                self.sleep_operation_finished.emit(
                    PowerManager.MODE_BOTH, False)
                return
            time.sleep(1)

        if not PowerManager.screen_off():
            self.sleep_operation_finished.emit(
                PowerManager.MODE_BOTH, False)
            return
        success = PowerManager.sleep()
        self.sleep_operation_finished.emit(PowerManager.MODE_BOTH, success)

    def _on_sleep_operation_finished(self, operation, success):
        """显示睡眠/关屏命令的真实执行结果，避免误报成功。"""
        if operation == "screen_off_early":
            self.screen_off_in_progress = False
            self.screen_off_done = success
            if self.pending_both_sleep:
                self.pending_both_sleep = False
                if success:
                    threading.Thread(
                        target=self._run_power_action,
                        args=(PowerManager.MODE_SLEEP,),
                        daemon=True).start()
                else:
                    threading.Thread(
                        target=self._run_both_action,
                        args=(self.lock_checkbox.isChecked(),),
                        daemon=True).start()
                self.status_label.setText(self._tr("sleep_starting"))
            return

        messages = {
            PowerManager.MODE_SLEEP: (self._tr("power_command_sent"), "#107c10"),
            PowerManager.MODE_SCREEN_OFF: (self._tr("screen_off"), "#107c10"),
            PowerManager.MODE_BOTH: (self._tr("both_command_sent"), "#107c10"),
        }
        failures = {
            PowerManager.MODE_SLEEP: self._tr("sleep_failed"),
            PowerManager.MODE_SCREEN_OFF: self._tr("screen_failed"),
            PowerManager.MODE_BOTH: self._tr("both_failed"),
        }
        if success:
            message, color = messages[operation]
        else:
            message, color = failures.get(
                operation, self._tr("power_failed")), "#f85149"
        self.status_label.setText(message)
        self.status_label.setStyleSheet(
            f"color: {color}; font-size: 12px;")

    def _finish_stop(self, message, color):
        """停止任务后统一恢复界面。"""
        PowerManager.cancel_prevent_sleep(self.caffeinate_proc)
        self.caffeinate_proc = None
        if self.timer_id:
            self.timer_id.stop()
        self.target_time = None

        self.is_running = False
        self._set_controls_enabled(True)
        self._update_button_state()
        self.action_btn.setEnabled(True)
        self.time_label.setText("00:00:00")
        self.pbar.setValue(0)
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {color}; font-size: 12px;")

    def _update_countdown(self):
        if self.target_time is None:
            return

        remaining = (self.target_time - datetime.now()).total_seconds()

        # ── 睡眠模式：中途关屏 ──
        if (self.current_func == self.FUNC_SLEEP
                and self._get_sleep_mode() == PowerManager.MODE_BOTH
                and not self.screen_off_done
                and not self.screen_off_in_progress):
            offset_seconds = self.screen_offset_spin.value() * 60
            if remaining <= offset_seconds:
                # 在后台线程执行，避免阻塞 UI
                lock = self.lock_checkbox.isChecked()
                self.screen_off_in_progress = True
                threading.Thread(
                    target=self._run_power_action,
                    args=(PowerManager.MODE_SCREEN_OFF, lock,
                          "screen_off_early"),
                    daemon=True).start()

        # ── 倒计时结束 ──
        if remaining <= 0:
            self.timer_id.stop()
            self.is_running = False

            PowerManager.cancel_prevent_sleep(self.caffeinate_proc)
            self.caffeinate_proc = None

            self.time_label.setText("00:00:00")
            self.pbar.setValue(0)
            self._update_button_state()
            self._set_controls_enabled(True)

            if self.current_func == self.FUNC_SHUTDOWN:
                # 关机已由系统调度执行，无需额外操作
                self.status_label.setText(self._tr("shutdown_executed"))
            else:
                mode = self._get_sleep_mode()
                if mode == PowerManager.MODE_SLEEP:
                    lock = self.lock_checkbox.isChecked()
                    threading.Thread(
                        target=self._run_power_action,
                        args=(PowerManager.MODE_SLEEP, lock),
                        daemon=True).start()
                    self.status_label.setText(self._tr("sleep_starting"))

                elif mode == PowerManager.MODE_SCREEN_OFF:
                    threading.Thread(
                        target=self._run_power_action,
                        args=(PowerManager.MODE_SCREEN_OFF,),
                        daemon=True).start()
                    self.status_label.setText(self._tr("screen_starting"))

                elif mode == PowerManager.MODE_BOTH:
                    if self.screen_off_in_progress:
                        self.pending_both_sleep = True
                        self.status_label.setText(self._tr("both_waiting"))
                    elif self.screen_off_done:
                        threading.Thread(
                            target=self._run_power_action,
                            args=(PowerManager.MODE_SLEEP,),
                            daemon=True).start()
                        self.status_label.setText(self._tr("sleep_starting"))
                    else:
                        threading.Thread(
                            target=self._run_both_action,
                            args=(self.lock_checkbox.isChecked(),),
                            daemon=True).start()
                        self.status_label.setText(self._tr("both_starting"))

            self.status_label.setStyleSheet(
                "color: #f85149; font-size: 12px;")
            return

        # 格式化时间
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        seconds = int(remaining % 60)
        self.time_label.setText(
            f"{hours:02d}:{minutes:02d}:{seconds:02d}")

        # 进度条
        progress = (1 - remaining / self.total_duration) * 100
        self.pbar.setValue(int(progress))

    def _stop(self):
        if not self.is_running:
            return

        # 取消系统关机调度
        if self.current_func == self.FUNC_SHUTDOWN:
            if self.shutdown_operation == "schedule":
                # 计划尚未创建完成时不能抢先取消；等创建完成后再取消。
                self.cancel_after_shutdown_scheduled = True
                if self.timer_id:
                    self.timer_id.stop()
                self.action_btn.setEnabled(False)
                self.status_label.setText(self._tr("shutdown_wait_cancel"))
                self.status_label.setStyleSheet(
                    "color: #f85149; font-size: 12px;")
                return
            if self.shutdown_operation is None:
                if self.timer_id:
                    self.timer_id.stop()
                self.action_btn.setEnabled(False)
                self._begin_shutdown_cancel()
            return

        self._finish_stop(self._tr("task_canceled"), "#58a6ff")

    # ═══════════ macOS 空闲设置 ═══════════
    def _load_idle_settings(self):
        display_min, sleep_min = PowerManager.get_system_idle_settings()
        if display_min is not None:
            self.idle_display_spin.setValue(display_min)
        if sleep_min is not None:
            self.idle_sleep_spin.setValue(sleep_min)

    def _apply_idle_settings(self):
        display_min = self.idle_display_spin.value()
        sleep_min = self.idle_sleep_spin.value()

        self.idle_apply_btn.setEnabled(False)
        self.idle_apply_btn.setText(self._tr("idle_saving"))

        def _do_apply():
            ok = PowerManager.set_system_idle_settings(
                display_min, sleep_min)
            # QTimer.singleShot 在工作线程中没有事件循环时不会触发；
            # 使用 Qt 信号才能保证回调进入主线程。
            self.idle_settings_finished.emit(ok)

        threading.Thread(target=_do_apply, daemon=True).start()

    def _on_idle_applied(self, success):
        self.idle_apply_btn.setEnabled(True)
        if success:
            self.idle_apply_btn.setText(self._tr("idle_saved"))
            self.status_label.setText(self._tr("idle_updated"))
            self.status_label.setStyleSheet(
                "color: #107c10; font-size: 12px;")
        else:
            self.idle_apply_btn.setText(self._tr("idle_save_failed"))
            self.status_label.setText(self._tr("idle_error"))
            self.status_label.setStyleSheet(
                "color: #f85149; font-size: 12px;")
        QTimer.singleShot(
            3000, lambda: self.idle_apply_btn.setText(
                self._tr("save_settings")))

    # ═══════════ 退出 / 关闭 ═══════════
    def _quit_app(self):
        if self.is_running:
            PowerManager.cancel_prevent_sleep(self.caffeinate_proc)
            self.caffeinate_proc = None
            if self.current_func == self.FUNC_SHUTDOWN:
                PowerManager.cancel_shutdown()

        app = QApplication.instance()
        if app:
            app.quit()

    def closeEvent(self, event):
        if self.is_running:
            self.hide()
            self.tray_icon.showMessage(
                "程序运行中",
                "定时任务仍在后台运行",
                QSystemTrayIcon.MessageIcon.Information,
                2000)
            event.ignore()
        else:
            if hasattr(self, 'tray_icon'):
                self.tray_icon.hide()
            event.accept()


# =======================
