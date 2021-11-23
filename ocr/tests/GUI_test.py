import sys

import main
from UI.OCR_Surface import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QDialog
import os
from UI.UIM import UIMWindow, Confirm_Dialog

# 将文件根路径统一为OCR
PROJECT_ABSOLUTE_PATH = os.path.dirname(os.path.abspath(main.__file__))
os.chdir(PROJECT_ABSOLUTE_PATH)


def main_win_test():
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    ui = UIMWindow()
    # 建立主窗口
    ui.setupUi(MainWindow=main_window)
    # 创建各控件功能
    ui.setup_widget_function()
    main_window.show()
    sys.exit(app.exec_())


def table_preview_test():
    app = QApplication(sys.argv)
    dialog = QDialog()
    ui = Confirm_Dialog()
    # 建立主窗口
    ui.setupUi(Dialog=dialog)

    dialog.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    table_preview_test()
