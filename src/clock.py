from PySide6.QtCore import Qt, QTimer, Slot, QPoint
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QSystemTrayIcon,
    QMenu,
)
from PySide6.QtGui import QFont, QIcon, QMouseEvent, QAction
from enum import Enum, unique
import rtoml as toml
import time
import sys
import images  # noqa: F401


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
        self.tray.show()

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
        self.tray.setIcon(QIcon(":/icon.svg"))
        self.tray_menu = QMenu()

        # 移动菜单
        self.move_menu = QMenu("移动到", self)
        move_top_left_action = QAction("&左上角", self)
        move_top_left_action.triggered.connect(lambda: self.move_to(Location.TOP_LEFT))
        move_top_right_action = QAction("&右上角", self)
        move_top_right_action.triggered.connect(
            lambda: self.move_to(Location.TOP_RIGHT)
        )
        move_bottom_left_action = QAction("&左下角", self)
        move_bottom_left_action.triggered.connect(
            lambda: self.move_to(Location.BOTTOM_LEFT)
        )
        move_bottom_right_action = QAction("&右下角", self)
        move_bottom_right_action.triggered.connect(
            lambda: self.move_to(Location.BOTTOM_RIGHT)
        )
        move_center_action = QAction("&居中", self)
        move_center_action.triggered.connect(lambda: self.move_to(Location.CENTER))

        self.move_menu.addAction(move_top_left_action)
        self.move_menu.addAction(move_top_right_action)
        self.move_menu.addAction(move_bottom_left_action)
        self.move_menu.addAction(move_bottom_right_action)
        self.move_menu.addAction(move_center_action)

        self.tray_menu.addMenu(self.move_menu)

        # 透明度菜单
        self.opacity_menu = QMenu("透明度调整", self)
        incress_opacity_action = QAction("&增加", self)
        incress_opacity_action.triggered.connect(self.incress_opacity)
        decress_opacity_action = QAction("&减少", self)
        decress_opacity_action.triggered.connect(self.decress_opacity)

        self.opacity_menu.addAction(incress_opacity_action)
        self.opacity_menu.addAction(decress_opacity_action)

        self.tray_menu.addMenu(self.opacity_menu)

        # 退出菜单
        exit_action = QAction("&退出", self)
        exit_action.triggered.connect(self.exit)

        self.tray_menu.addAction(exit_action)

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
                self.move(self.screen().size().width() - self.width(), 0)
            case Location.BOTTOM_LEFT:
                self.move(0, self.screen().size().height() - self.height())
            case Location.BOTTOM_RIGHT:
                self.move(
                    self.screen().size().width() - self.width(),
                    self.screen().size().height() - self.height(),
                )
            case Location.CENTER:
                self.move(
                    self.screen().size().width() / 2 - self.width() / 2,
                    self.screen().size().height() / 2 - self.height() / 2,
                )

    def load_config(self):
        with open("config.toml", "r", encoding="utf-8") as fp:
            self.config = toml.load(fp)

    def store_config(self):
        with open("config.toml", "w", encoding="utf-8") as fp:
            toml.dump(self.config, fp)

    @Slot()
    def update_time(self):
        self.time_label.setText(time.strftime("%H:%M:%S"))

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.config["window"]["locked"]:
            return
        if self._tracking:
            self._endPos = event.position().toPoint() - self._startPos
            self.move(self.pos() + self._endPos)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._tracking = False
            self._startPos = None
            self._endPos = None

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._startPos = QPoint(event.position().x(), event.position().y())
            self._tracking = True

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        self.config["window"]["locked"] = not self.config["window"]["locked"]

        return super().mouseDoubleClickEvent(event)

    def exit(self):
        self.close()
        # 默认窗口锁定不可修改
        self.config["window"]["locked"] = True

        self.store_config()
        sys.exit(0)

    def incress_opacity(self):
        if self.config["window"]["opacity"] >= 1.0:
            return
        self.setWindowOpacity(self.config["window"]["opacity"] + 0.1)
        self.config["window"]["opacity"] += 0.1

    def decress_opacity(self):
        if self.config["window"]["opacity"] <= 0.0:
            return
        self.setWindowOpacity(self.config["window"]["opacity"] - 0.1)
        self.config["window"]["opacity"] -= 0.1


def main():
    app = QApplication(sys.argv)
    root = Clock()
    root.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
