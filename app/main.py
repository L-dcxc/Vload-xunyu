import sys

from PyQt6.QtWidgets import QApplication

from .ui.main_window_v2 import MainWindowV2
from .ui.theme import APP_STYLESHEET


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLESHEET)
    window = MainWindowV2()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
