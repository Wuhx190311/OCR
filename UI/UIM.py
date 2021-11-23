from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QFileDialog, QDialog, QApplication, QWidget
from UI.OCR_Surface import Ui_MainWindow as UIM
from UI.Confirm_Window import Ui_Dialog as Confirm_dialog
from UI.Preview_Window import Ui_Form as Preview_widget
from ocr.data_manager import Data_manager


class UIMWindow(UIM, QtWidgets.QWidget):

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.data_manager = Data_manager()
        self.confirm_dialog = Confirm_Dialog()

    def setup_widget_function(self):
        """初始化所有控件的行为"""

        self.usr_Edit.setText(self.data_manager.passport.get("username"))
        self.addr_Edit.setText(self.data_manager.passport.get("host"))
        self.passwd_Edit.setText(self.data_manager.passport.get("password"))
        self.database_Edit.setText(self.data_manager.passport.get("db"))
        self.trans2table_radionButton.setChecked(True)
        self.form_select_box.setCurrentIndex(0)
        self.detect_status_label.setText('等待识别中')
        # 选择待扫描的图片文件
        # 选择
        self.img_select_lable.clicked.connect(self.select_img)
        # 拖入
        self.img_select_lable.dragEnter[str].connect(self.drag_enter_img)

        # 初始界面默认为转excel，隐藏数据库输入面板
        self.dbconnector_frame.setVisible(False)

        # 图片转表格 单选按钮按下时按照当前form_box选择情况更新界面
        self.trans2table_radionButton.clicked.connect(self.form_box_select_change_slot)

        # 单选按钮：图片转文本
        self.trans2txt_raionButton.clicked['bool'].connect(
            lambda: self.output_Edit.setPlaceholderText('C:\\users\\User\\Documents'))

        # 下拉列表：输出格式选择
        self.form_select_box.currentIndexChanged.connect(self.form_box_select_change_slot)

        # 文件输出目录选择
        self.output_toolButton.clicked.connect(self.select_dir)
        self.output_Edit.editingFinished.connect(lambda: self.data_manager.set_output_table_name(self.output_Edit.text()))

        # 数据库链接四件套
        # 用户
        self.usr_Edit.editingFinished.connect(lambda: self.data_manager.set_username(self.usr_Edit.text()))

        # 地址
        self.addr_Edit.editingFinished.connect(lambda: self.data_manager.set_host(self.addr_Edit.text()))

        # 密码
        self.passwd_Edit.editingFinished.connect(lambda: self.data_manager.set_passwd(self.passwd_Edit.text()))

        # 数据库名
        self.database_Edit.editingFinished.connect(
            lambda: self.data_manager.set_database_name(self.database_Edit.text()))

        # 记住密码
        self.remeber_key_checkBox.clicked[bool].connect(
            lambda boolean: self.data_manager.remember_passwd(boolean=boolean))

        # 连接测试
        self.link_test_button.clicked.connect(self.database_link_test)

        # 测试等待提示图标
        # self.loading_movie = QMovie('img/wait.gif')
        # self.loading_label.setMovie(self.loading_movie)
        # self.loading_movie.start()

        # 开始转换
        self.detect_start_button.clicked.connect(self.start_detect)

    def drag_enter_img(self, url: str):
        """读取拖入图片的地址"""
        # todo:图片文件判断
        self.output_Edit.setText(self.data_manager.output_name)
        self.detect_status_label.setText('等待识别中')
        self.data_manager.set_img(url)
        self.img_select_lable.setPixmap(QPixmap(url))
        self.img_select_lable.setScaledContents(True)
        self.data_manager.img_preprocessing()

    def select_img(self):
        """打开一个文件选择窗口，选择一个图片文件（.jpg/.png）, 并将该图片在标签处展示"""
        self.output_Edit.setText(self.data_manager.output_name)
        self.detect_status_label.setText('等待识别中')
        filepath, filetype = QFileDialog.getOpenFileName(self, caption="选取文件", directory="./",
                                                         filter="Images (*.jpg *.png)")
        # 取消选择时，图片保持不变
        if '' == filepath:
            return
        self.data_manager.set_img(img_path=filepath)
        self.img_select_lable.setPixmap(QPixmap(filepath))
        self.img_select_lable.setScaledContents(True)

        # 开启一个新线程开始处理图像,处理完的图像保存在temp.jpg中
        self.data_manager.img_preprocessing()

    def select_dir(self):
        """选择文件架，将文件路径保存在 output_Edit 中"""
        directory = QFileDialog.getExistingDirectory(self, "文件夹", "./")
        self.output_Edit.setText(directory)
        self.data_manager.set_output_path(directory)

    def start_detect(self):
        """
        1.图像开始识别
        2.显示识别中的等待界面
        """
        self.detect_status_label.setText('识别中...')
        QApplication.processEvents()
        conform_msg = "识别成功"
        # 1.转文字：
        if self.trans2txt_raionButton.isChecked():
            self.detect_status_label.setText('识别中...')
            self.data_manager.parse_img_to_text()
            self.data_manager.write_to_text()

        # 2.转表格：
        if self.trans2table_radionButton.isChecked():
            self.detect_status_label.setText('识别中...')
            self.data_manager.parse_img_to_excel()
            # 2-1.转excel
            if 0 == self.form_select_box.currentIndex():
                self.detect_status_label.setText('写入Excel...')
                QApplication.processEvents()
                self.data_manager.write_to_excel()
            elif 1 == self.form_select_box.currentIndex():
                self.detect_status_label.setText('写入CSV...')
                QApplication.processEvents()
                self.data_manager.write_to_csv()
            # 2-3.导入MySQL
            elif 2 == self.form_select_box.currentIndex():
                self.data_manager.img_preview()
                open_Preview_Widget()
                self.detect_status_label.setText('写入MySQL...')
                # QApplication.processEvents()
                msg = self.data_manager.write_to_db()
                if msg == "no input":
                    conform_msg = "找不到输入文件QAQ"
                elif msg.find("error") == 0:
                    conform_msg = "数据库连接失败了……"
                self.test_result_browser.setText(msg)
        # 弹出确认窗口
        self.open_Confirm_Dialog(conform_msg)
        self.detect_status_label.setText('等待选择图片')

    def form_box_select_change_slot(self):
        """下拉表单选择为:
            1.mysql 激活数据库链接,将 “输出位置” 标签改名为 “输出表名”
            2.其他 隐藏数据库链接,显示输出位置
        """
        # 当选择的输出为MySQL,激活数据库连接板块
        index = self.form_select_box.currentIndex()
        if 2 == index:  # 选项是mysql时
            # 启用数据库链接输入项
            self.dbconnector_frame.setVisible(True)
            self.dbconnector_frame.setEnabled(True)
            # 启用输入表名和填充，并清空output_edit
            self.output_Edit.clear()
            self.output_lable.setText('输出表名')
            self.output_toolButton.setHidden(True)
            self.output_Edit.setPlaceholderText('untitled')
        else:
            self.dbconnector_frame.setHidden(True)
            self.output_lable.setText('输出路径')
            self.output_toolButton.setVisible(True)
            self.output_Edit.clear()
            self.output_Edit.setPlaceholderText('C:\\users\\User\\Documents')

    def database_link_test(self):
        """测试数据库是否连通，将连接结果在 @:param:test_result_browser中输出 """
        self.test_result_browser.clear()
        self.test_result_browser.setText('connecting...')
        msg = self.data_manager.connect_db()
        self.test_result_browser.setText(msg)

    def open_Confirm_Dialog(self, msg: str = "识别成功"):
        dialog = QDialog()
        # ui = Confirm_Dialog()
        # 建立主窗口
        self.confirm_dialog.setupUi(Dialog=dialog)
        self.confirm_dialog.label.setText(msg)
        dialog.show()
        dialog.exec_()


#
# def open_Confirm_Dialog():
#     dialog = QDialog()
#     ui = Confirm_Dialog()
#     # 建立主窗口
#     ui.setupUi(Dialog=dialog)
#     dialog.show()
#     dialog.exec_()
#
#

def open_Preview_Widget():
    widget = QWidget()
    ui = Preview_Widget()
    # 建立主窗口
    ui.setupUi(Form=widget)
    widget.show()


class Confirm_Dialog(Confirm_dialog, QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)


class Preview_Widget(Preview_widget, QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
