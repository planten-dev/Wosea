from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QSystemTrayIcon,
    QMenu,
)
from PySide6.QtGui import QFont, QIcon
from enum import Enum, unique
import rtoml as toml
import time
import sys


@unique
class Location(Enum):
    TOP_LEFT = 0
    TOP_RIGHT = 1
    BOTTOM_LEFT = 2
    BOTTOM_RIGHT = 3
    CENTER = 4


class Clock(QWidget):
    def __init__(self):
        super().__init__()
        self.load_config()
        self.init_widget()
        self.init_tray_menu()
        self.init_timer()
        self.init_window_attributes()

        self.move_to(Location.TOP_LEFT)
        self.timer.start(self.config["timer"]["frequency"])

        self.show()

    def init_widget(self):
        self.layout = QVBoxLayout(self)
        self.time_label = QLabel(
            "等待加载...", self, alignment=Qt.AlignmentFlag.AlignCenter
        )
        self.time_label.setFont(
            QFont(self.config["font"]["family"], self.config["font"]["size"])
        )
        self.layout.addWidget(self.time_label)

    def init_tray_menu(self):
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(QIcon(":/icon.png"))
        self.tray_menu = QMenu()
        # TODO: add menu items
        self.tray.setContextMenu(self.tray_menu)

    def init_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)

    def init_window_attributes(self):
        self.setWindowOpacity(self.config["window"]["opacity"])
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
        )

    def move_to(self, location: Location):
        match location:
            case Location.TOP_LEFT:
                self.move(0, 0)
            case Location.TOP_RIGHT:
                self.move(self.screen().width() - self.width(), 0)
            case Location.BOTTOM_LEFT:
                self.move(0, self.screen().height() - self.height())
            case Location.BOTTOM_RIGHT:
                self.move(
                    self.screen().width() - self.width(),
                    self.screen().height() - self.height(),
                )
            case Location.CENTER:
                self.move(
                    self.screen().width() / 2 - self.width() / 2,
                    self.screen().height() / 2 - self.height() / 2,
                )

    def load_config(self):
        with open("config.toml") as fp:
            self.config = toml.load(fp)

    def store_config(self):
        toml.dump(self.config, "config.toml")

    @Slot()
    def update_time(self):
        self.time_label.setText(time.strftime("%H:%M:%S"))


def main():
    app = QApplication(sys.argv)
    root = Clock()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
