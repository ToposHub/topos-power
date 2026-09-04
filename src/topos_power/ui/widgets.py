"""Topos Power 的轻量动态控件。"""

from PyQt6.QtCore import (QEasingCurve, QEvent, QPropertyAnimation, QRectF,
                          QSize, Qt, QTimer, pyqtProperty, pyqtSignal)
from PyQt6.QtGui import (QBrush, QColor, QFont, QIntValidator, QPainter, QPen)
from PyQt6.QtWidgets import (QApplication, QCheckBox, QLabel, QLineEdit,
                             QSizePolicy, QStyle, QStyleOptionButton, QWidget)


class _DurationEditor(QLineEdit):
    """支持 Esc 取消的短时长输入框。"""

    canceled = pyqtSignal()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.canceled.emit()
            event.accept()
            return
        super().keyPressEvent(event)


class EditableDurationLabel(QLabel):
    """可双击切换为分钟数输入的时长标签。"""

    value_edited = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._editor = None

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._start_editing()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def _start_editing(self):
        if self._editor is not None:
            return

        # Use a sibling overlay instead of a child of the label. A child is
        # clipped to the label's original bounds, which can cut off the
        # editor border or the entered value on some window sizes.
        editor = _DurationEditor(self.parentWidget())
        editor.setObjectName("DurationEditor")
        editor.setAlignment(Qt.AlignmentFlag.AlignRight)
        editor.setValidator(QIntValidator(1, 1440, editor))
        editor.setText(str(self.property("durationMinutes") or ""))
        editor.setToolTip(self.toolTip())
        editor_width = max(self.width(), 116)
        editor_rect = self.geometry()
        editor_rect.setLeft(editor_rect.right() - editor_width + 1)
        editor_rect.setWidth(editor_width)
        editor.setGeometry(editor_rect)
        editor.editingFinished.connect(self._commit_editing)
        editor.canceled.connect(self._cancel_editing)
        self._editor = editor
        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(self)
        editor.show()
        editor.raise_()
        editor.selectAll()
        editor.setFocus()

    def set_duration_minutes(self, value):
        self.setProperty("durationMinutes", int(value))
        self.style().unpolish(self)
        self.style().polish(self)

    def _commit_editing(self):
        if self._editor is None:
            return
        text = self._editor.text().strip()
        if text:
            self.value_edited.emit(int(text))
        self._close_editor()

    def _cancel_editing(self):
        self._close_editor()

    def eventFilter(self, watched, event):
        if (self._editor is not None
                and event.type() == QEvent.Type.MouseButtonPress):
            inside_editor = watched is self._editor
            if isinstance(watched, QWidget):
                inside_editor = inside_editor or self._editor.isAncestorOf(
                    watched)
            if not inside_editor:
                self._commit_editing()
        return super().eventFilter(watched, event)

    def _close_editor(self):
        editor = self._editor
        self._editor = None
        app = QApplication.instance()
        if app is not None:
            app.removeEventFilter(self)
        if editor is not None:
            editor.hide()
            editor.deleteLater()


class CheckMarkBox(QCheckBox):
    """复选框：在平台样式的激活底色上补一个清晰的白色勾。"""

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.isChecked():
            return

        option = QStyleOptionButton()
        self.initStyleOption(option)
        indicator = self.style().subElementRect(
            QStyle.SubElement.SE_CheckBoxIndicator, option, self)
        if not indicator.isValid():
            return

        painter = QPainter(self)
        pen = QPen(QColor("#ffffff"), max(1, indicator.height() // 7))
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        left = indicator.left() + indicator.width() * 0.24
        middle = indicator.left() + indicator.width() * 0.45
        right = indicator.left() + indicator.width() * 0.77
        y = indicator.top()
        painter.drawLine(int(left), int(y + indicator.height() * 0.52),
                         int(middle), int(y + indicator.height() * 0.72))
        painter.drawLine(int(middle), int(y + indicator.height() * 0.72),
                         int(right), int(y + indicator.height() * 0.30))
        painter.end()


class CircularProgress(QWidget):
    """带平滑过渡的环形进度条。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0.0
        self._animation = None
        self.setMinimumSize(96, 96)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def sizeHint(self):
        return QSize(104, 104)

    def get_value(self):
        return self._value

    def set_value(self, value):
        self._value = max(0.0, min(100.0, float(value)))
        self.update()

    value = pyqtProperty(float, fget=get_value, fset=set_value)

    def setValue(self, value):
        """兼容 QProgressBar 的调用方式。"""
        if self._animation:
            self._animation.stop()
        self._animation = QPropertyAnimation(self, b"value", self)
        self._animation.setDuration(260)
        self._animation.setStartValue(self._value)
        self._animation.setEndValue(float(value))
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.start()

    def paintEvent(self, _event):
        side = min(self.width(), self.height())
        bounds = QRectF(
            (self.width() - side) / 2 + 8,
            (self.height() - side) / 2 + 8,
            side - 16,
            side - 16,
        )
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        track_pen = QPen(QColor("#292d36"), 7, Qt.PenStyle.SolidLine)
        track_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(track_pen)
        painter.drawArc(bounds, 90 * 16, -360 * 16)

        progress_pen = QPen(QColor("#3478f6"), 7, Qt.PenStyle.SolidLine)
        progress_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(progress_pen)
        painter.drawArc(bounds, 90 * 16, int(-self._value * 3.6 * 16))

        painter.setPen(QColor("#aeb4c0"))
        font = QFont(self.font())
        font.setPointSize(10)
        painter.setFont(font)
        painter.drawText(bounds, Qt.AlignmentFlag.AlignCenter,
                         f"{round(self._value)}%")
        painter.end()


class PowerPhaseTimeline(QWidget):
    """展示当前电源任务阶段，并对活动节点做轻微呼吸动画。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._phases = []
        self._active_index = -1
        self._pulse = 0.0
        self._pulse_timer = QTimer(self)
        self._pulse_timer.timeout.connect(self._advance_pulse)
        self.setMinimumHeight(42)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Fixed)

    def sizeHint(self):
        return QSize(420, 42)

    def set_phases(self, phases):
        self._phases = list(phases)
        self.update()

    def phase_count(self):
        return len(self._phases)

    def set_active(self, index):
        if not self._phases:
            return
        self._active_index = max(-1, min(index, len(self._phases) - 1))
        if self._active_index >= 0:
            self._pulse_timer.start(70)
        else:
            self._pulse_timer.stop()
        self.update()

    def _advance_pulse(self):
        self._pulse = (self._pulse + 0.08) % 1.0
        self.update()

    def paintEvent(self, _event):
        if not self._phases:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        left = 12
        right = self.width() - 12
        y = 11
        step = (right - left) / max(1, len(self._phases) - 1)

        for index in range(len(self._phases) - 1):
            x1 = left + step * index
            x2 = left + step * (index + 1)
            color = QColor("#3478f6") if index < self._active_index else QColor("#30343e")
            painter.setPen(QPen(color, 2))
            painter.drawLine(int(x1), y, int(x2), y)

        for index, phase in enumerate(self._phases):
            x = left + step * index
            if index == self._active_index:
                glow_radius = 7 + int(self._pulse * 4)
                painter.setBrush(QBrush(QColor(52, 120, 246, 35)))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(QRectF(x - glow_radius, y - glow_radius,
                                           glow_radius * 2, glow_radius * 2))
                painter.setBrush(QBrush(QColor("#3478f6")))
            elif index < self._active_index:
                painter.setBrush(QBrush(QColor("#3478f6")))
            else:
                painter.setBrush(QBrush(QColor("#30343e")))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QRectF(x - 4, y - 4, 8, 8))

            painter.setPen(QColor("#8d9099" if index != self._active_index
                                 else "#d9e6ff"))
            font = QFont(self.font())
            font.setPointSize(8)
            painter.setFont(font)
            text_rect = QRectF(x - step / 2, 20, step, 18)
            if index == 0:
                text_rect.setLeft(0)
            if index == len(self._phases) - 1:
                text_rect.setRight(self.width())
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, phase)
        painter.end()
