"""Topos Power 应用入口。"""

import sys

from PyQt6.QtWidgets import QApplication

from .config import APP_NAME, APP_VERSION
from .ui.main_window import PowerTimer


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    window = PowerTimer()
    window.show()
    sys.exit(app.exec())
