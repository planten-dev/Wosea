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


@unique
class Color(Enum):
    RED = 0
    GREEN = 1
    BLUE = 2
    YELLOW = 3
    PURPLE = 4
    ORANGE = 5
    WHITE = 6
    PINK = 7
    BLACK = 8


class Clock(QWidget):
    exam_mode = False

    def __init__(self):
        super().__init__()
        self.load_config()
        self.init_widget()
        self.init_tray_menu()
        self.init_timer()
        self.init_window_attributes()

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

        # 字体菜单
        self.font_menu = QMenu("字体调整", self)
        incress_font_size_action = QAction("&增加", self)
        incress_font_size_action.triggered.connect(self.incress_font_size)
        decress_font_size_action = QAction("&减少", self)
        decress_font_size_action.triggered.connect(self.decress_font_size)
        reset_font_size_action = QAction("&重置", self)
        reset_font_size_action.triggered.connect(self.reset_font_size)

        self.font_menu.addAction(incress_font_size_action)
        self.font_menu.addAction(decress_font_size_action)
        self.font_menu.addAction(reset_font_size_action)

        self.tray_menu.addMenu(self.font_menu)

        # 字体颜色菜单
        self.font_color_menu = QMenu("字体颜色调整", self)
        red_action = QAction("&红色", self)
        red_action.triggered.connect(lambda: self.set_font_color(Color.RED))
        green_action = QAction("&绿色", self)
        green_action.triggered.connect(lambda: self.set_font_color(Color.GREEN))
        blue_action = QAction("&蓝色", self)
        blue_action.triggered.connect(lambda: self.set_font_color(Color.BLUE))
        yellow_action = QAction("&黄色", self)
        yellow_action.triggered.connect(lambda: self.set_font_color(Color.YELLOW))
        purple_action = QAction("&紫色", self)
        purple_action.triggered.connect(lambda: self.set_font_color(Color.PURPLE))
        orange_action = QAction("&橙色", self)
        orange_action.triggered.connect(lambda: self.set_font_color(Color.ORANGE))
        white_action = QAction("&白色", self)
        white_action.triggered.connect(lambda: self.set_font_color(Color.WHITE))
        pink_action = QAction("&粉色", self)
        pink_action.triggered.connect(lambda: self.set_font_color(Color.PINK))
        black_action = QAction("&黑色", self)
        black_action.triggered.connect(lambda: self.set_font_color(Color.BLACK))
        reset_action = QAction("&重置", self)
        reset_action.triggered.connect(lambda: self.set_font_color(Color.BLACK))

        self.font_color_menu.addAction(red_action)
        self.font_color_menu.addAction(green_action)
        self.font_color_menu.addAction(blue_action)
        self.font_color_menu.addAction(yellow_action)
        self.font_color_menu.addAction(purple_action)
        self.font_color_menu.addAction(orange_action)
        self.font_color_menu.addAction(white_action)
        self.font_color_menu.addAction(pink_action)
        self.font_color_menu.addAction(black_action)
        self.font_color_menu.addAction(reset_action)

        self.tray_menu.addMenu(self.font_color_menu)

        # 考试模式
        exam_action = QAction("&考试模式", self)
        exam_action.triggered.connect(lambda: self.set_exam_mode(True))

        self.tray_menu.addAction(exam_action)

        # 退出菜单
        exit_action = QAction("&退出", self)
        exit_action.triggered.connect(self.exit)

        self.tray_menu.addAction(exit_action)

        self.tray.setContextMenu(self.tray_menu)

    def init_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(self.config["timer"]["frequency"])

    def init_window_attributes(self):
        self.setWindowOpacity(self.config["window"]["opacity"])
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
        )

        match self.config["window"]["location"]:
            case "top-left":
                self.move_to(Location.TOP_LEFT)
            case "top-right":
                self.move_to(Location.TOP_RIGHT)
            case "bottom-left":
                self.move_to(Location.BOTTOM_LEFT)
            case "bottom-right":
                self.move_to(Location.BOTTOM_RIGHT)
            case "center":
                self.move_to(Location.CENTER)

        match self.config["font"]["color"]:
            case "red":
                self.set_font_color(Color.RED)
            case "green":
                self.set_font_color(Color.GREEN)
            case "blue":
                self.set_font_color(Color.BLUE)
            case "yellow":
                self.set_font_color(Color.YELLOW)
            case "purple":
                self.set_font_color(Color.PURPLE)
            case "orange":
                self.set_font_color(Color.ORANGE)
            case "white":
                self.set_font_color(Color.WHITE)
            case "pink":
                self.set_font_color(Color.PINK)
            case "black":
                self.set_font_color(Color.BLACK)

    def move_to(self, location: Location):
        match location:
            case Location.TOP_LEFT:
                self.move(0, 0)
                self.config["window"]["location"] = "top-left"
            case Location.TOP_RIGHT:
                self.move(self.screen().size().width() - self.width(), 0)
                self.config["window"]["location"] = "top-right"
            case Location.BOTTOM_LEFT:
                self.move(0, self.screen().size().height() - self.height())
                self.config["window"]["location"] = "bottom-left"
            case Location.BOTTOM_RIGHT:
                self.move(
                    self.screen().size().width() - self.width(),
                    self.screen().size().height() - self.height(),
                )
                self.config["window"]["location"] = "bottom-right"
            case Location.CENTER:
                self.move(
                    self.screen().size().width() / 2 - self.width() / 2,
                    self.screen().size().height() / 2 - self.height() / 2,
                )
                self.config["window"]["location"] = "center"

    def load_config(self):
        with open("config.toml", "r", encoding="utf-8") as fp:
            self.config = toml.load(fp)

    def store_config(self):
        with open("config.toml", "w", encoding="utf-8") as fp:
            toml.dump(self.config, fp)

    @Slot()
    def update_time(self):
        self.time_label.setText(time.strftime(self.config["timer"]["template"]))

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
        # 考试模式一次性
        self.set_exam_mode(False)

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

    def incress_font_size(self):
        self.config["font"]["size"] += 5
        self.time_label.setFont(
            QFont(self.config["font"]["family"], self.config["font"]["size"])
        )
        # 由于字体改动会导致窗口大小改变，所以需要重新调整窗口位置
        self.setFixedSize(self.sizeHint())
        self.move_to(self.config["window"]["location"])

    def decress_font_size(self):
        self.config["font"]["size"] -= 5
        self.time_label.setFont(
            QFont(self.config["font"]["family"], self.config["font"]["size"])
        )
        # 由于字体改动会导致窗口大小改变，所以需要重新调整窗口位置
        self.setFixedSize(self.sizeHint())
        self.move_to(self.config["window"]["location"])

    def reset_font_size(self):
        self.config["font"]["size"] = 18
        self.time_label.setFont(
            QFont(self.config["font"]["family"], self.config["font"]["size"])
        )
        # 由于字体改动会导致窗口大小改变，所以需要重新调整窗口位置
        self.setFixedSize(self.sizeHint())
        self.move_to(self.config["window"]["location"])

    def set_font_color(self, color: Color):
        match color:
            case Color.RED:
                self.config["font"]["color"] = "red"
                self.time_label.setStyleSheet("color: red;")
            case Color.GREEN:
                self.config["font"]["color"] = "green"
                self.time_label.setStyleSheet("color: green;")
            case Color.BLUE:
                self.config["font"]["color"] = "blue"
                self.time_label.setStyleSheet("color: blue;")
            case Color.YELLOW:
                self.config["font"]["color"] = "yellow"
                self.time_label.setStyleSheet("color: yellow;")
            case Color.PURPLE:
                self.config["font"]["color"] = "purple"
                self.time_label.setStyleSheet("color: purple;")
            case Color.ORANGE:
                self.config["font"]["color"] = "orange"
                self.time_label.setStyleSheet("color: orange;")
            case Color.WHITE:
                self.config["font"]["color"] = "white"
                self.time_label.setStyleSheet("color: white;")
            case Color.PINK:
                self.config["font"]["color"] = "pink"
                self.time_label.setStyleSheet("color: pink;")
            case Color.BLACK:
                self.config["font"]["color"] = "black"
                self.time_label.setStyleSheet("color: black;")

    def set_exam_mode(self, mode: bool):
        if self.exam_mode == mode:
            return
        if mode:
            self.exam_mode = True
            self.config["timer"]["template"] = (
                "当前时间:\n"
                + self.config["timer"]["template"]
                + "\n\n端正考风,严肃考纪\n振奋精神,考出水平"
            )
            self.time_label.setFont(QFont(self.config["font"]["family"], 50))
            self.time_label.setStyleSheet("color: black;")
            self.setWindowOpacity(1.0)
        else:
            self.exam_mode = False
            self.config["timer"]["template"] = "%H:%M:%S"


def main():
    app = QApplication(sys.argv)
    root = Clock()
    root.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
