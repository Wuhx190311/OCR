# coding:utf-8
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QSlider


class QButtonLabel(QLabel):
    clicked = pyqtSignal()
    dragEnter = pyqtSignal(str)

    def __init__(self, parent=None):
        super(QButtonLabel, self).__init__(parent=parent)
        self.setAcceptDrops(True)

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        self.clicked.emit()

    def dragEnterEvent(self, e):
        m = e.mimeData()

        if m.hasText(): # 只能这么写
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        path = str(e.mimeData().urls()[0]).split('\'')[1].split('///')[1]
        self.dragEnter.emit(path)   # urls传回时要改成str类型
