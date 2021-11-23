import sys

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow
from UI.UIM import UIMWindow
from qt_material import apply_stylesheet

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    # main_window.setWindowOpacity(0.85)  # 设置窗口透明度
    # main_window.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # 设置窗口背景透明
    ui = UIMWindow()
    # 建立主窗口
    ui.setupUi(MainWindow=main_window)
    # 创建各控件功能
    ui.setup_widget_function()
    apply_stylesheet(app, theme='dark_cyan.xml')
    main_window.show()
    sys.exit(app.exec_())
