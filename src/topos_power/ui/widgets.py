"""Topos Power 的轻量动态控件。"""

from PyQt6.QtCore import (QEasingCurve, QPropertyAnimation, QRectF, QSize,
                          Qt, QTimer, pyqtProperty)
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QSizePolicy, QWidget


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
