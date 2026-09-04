"""Topos Power 应用入口。"""

import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from .config import APP_ICON_PATH, APP_NAME, APP_VERSION
from .ui.main_window import PowerTimer


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    if APP_ICON_PATH.exists():
        app.setWindowIcon(QIcon(str(APP_ICON_PATH)))
    window = PowerTimer()
    window.show()
    sys.exit(app.exec())
