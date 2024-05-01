from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt
from updater import Updater
import sys
import os


def main():
    # check for update
    app = QApplication(sys.argv)
    new_version = Updater.check_for_update()
    if new_version is not None:
        # show update message
        msg = QMessageBox()
        msg.setWindowTitle("Wosea Updater")
        msg.setText("       Wosea Updater\n检查到新版本,即将进行更新.")
        msg.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        msg.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        msg.exec()
        # update
        if not Updater.update(new_version):
            msg = QMessageBox()
            msg.setWindowTitle("Wosea Updater")
            msg.setText("    Wosea Updater\n更新失败,请联系开发者.")
            msg.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
            msg.setWindowFlag(Qt.WindowType.FramelessWindowHint)
            msg.exec()
    # start app
    os.execl("clock.exe", "clock.exe", "")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
