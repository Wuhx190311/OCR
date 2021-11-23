import os
from enum import Enum
import pickle
from ocr.database_connector import Database_connector
from ocr.img_manager import Img_manager, NotAImgException
import pandas as pd

PROJECT_ABSOLUTE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ABSOLUTE_PATH)

STD_PASSPORT_INDEX = ['username', 'host', 'password', 'db']


class Data_manager:
    """储存用户在UI中填入的数据"""

    class Trans_type(Enum):
        TXT = 0
        TABLE = 1

    class Trans_detail(Enum):
        EXCEL = 0
        CSV = 1
        MySQL = 2

    def __init__(self):
        self.img_manager = Img_manager()
        self.db_connector = Database_connector()

        self.img_path: str = ''
        self.img_name: str = ''

        # 转文本/表格
        self.trans_type = self.Trans_type
        # 转excel/csv/mysql
        self.trans_detail = self.Trans_detail
        self.passport = dict(username='',
                             host='',
                             password='',
                             db='')

        self.db_remember_passwd = False

        # output_path 默认在桌面
        self.output_path = 'C:/Users/Whongxuan/Desktop'
        self.output_name = None  # 通过img_name和trans_type推测输出文件名
        self.output_table_name = "untitled"

        # 转换完成的内容
        self.content = None
        self.load_passport()

    def set_output_path(self, output_path):
        self.output_path = output_path

    def set_output_table_name(self, table_name):
        self.output_table_name = table_name

    def set_img(self, img_path):
        self.img_path = img_path
        self.img_name = os.path.split(img_path)[-1]
        self.output_name = os.path.splitext(self.img_name)[0]
        if "untitled" == self.output_table_name:
            self.output_table_name = self.output_name

    def set_all_info(self, passport: dict):
        """
        :param passport: {'username': name,
                          'host': localhost
                          'password': password
                          'db': db_name}
        """
        self.set_username(passport.get('username'))
        self.set_host(passport.get('host'))
        self.set_passwd(passport.get('password'))
        self.set_database_name(passport.get('db'))

    def set_username(self, name):
        self.passport["username"] = name

    def set_passwd(self, key):
        self.passport["password"] = key

    def set_host(self, host):
        self.passport["host"] = host

    def set_database_name(self, db_name):
        self.passport["db"] = db_name

    def remember_passwd(self, boolean: bool):
        self.db_remember_passwd = boolean

    def connect_db(self) -> str:
        """
        连接数据库：
            1.给db_connector发送登录字典
            2.拿到登录返回的信息
                i.登录成功：记录信息，记录日志
                ii.登录失败, 记录日志
        @:return msg:str
        """

        self.db_connector.set_all_info(**self.passport)
        msg = self.db_connector.connect_db()

        # 如果连接成功，且确认记住密码，则将数据库连接文件写入文件/数据库保存
        if -1 != msg.find("Successful connected to database"):
            try:
                with open(f'{PROJECT_ABSOLUTE_PATH}/docs/db_connect.back', 'wb') as f:
                    if not self.db_remember_passwd:
                        self.passport['password'] = ""
                    pickle.dump(self.passport, f)
            except FileNotFoundError:
                print(os.getcwd())
        return msg

    @staticmethod
    def __write_to_file(filepath: str, filename: str, exp: str, content: str):
        """写入文件的通用方法"""
        with open(f"{filepath}/{filename}.{exp}", 'w') as file:
            file.write(content)

    def output(self):
        if self.Trans_type.TXT == self.trans_type:
            self.write_to_text()
        if self.Trans_type.TABLE == self.trans_type:
            if self.trans_detail == self.Trans_detail.CSV:
                self.write_to_csv()
            if self.trans_detail == self.Trans_detail.EXCEL:
                self.write_to_excel()
            if self.trans_detail == self.Trans_detail.MySQL:
                self.write_to_db()
        else:
            raise TypeError("filetype is not standard output type!")

    def write_to_text(self):
        exp_name = 'txt'
        name = os.path.splitext(self.img_name)[0]
        if self.content == '':
            self.content = 'you haven\'t select any images!'
            self.__write_to_file(filepath=self.output_path, filename='warning', exp='log', content=self.content)
            return
        self.__write_to_file(filepath=self.output_path, filename=name, exp=exp_name, content=self.content)

    def write_to_excel(self):
        exp_name = 'xlsx'
        name = os.path.splitext(self.img_name)[0]
        if self.content is None:
            self.content = 'you haven\'t select any images!'
            self.__write_to_file(filepath=self.output_path, filename='warning', exp='log', content=self.content)
            return
        pd.DataFrame(self.content).to_excel(f"{self.output_path}/{name}.{exp_name}")

    def write_to_csv(self):
        exp_name = 'csv'
        name = os.path.splitext(self.img_name)[0]
        if self.content is None:
            self.content = 'you haven\'t select any images!'
            self.__write_to_file(filepath=self.output_path, filename='warning', exp='log', content=self.content)
            return
        pd.DataFrame(self.content).to_csv(f"{self.output_path}/{name}.{exp_name}")

    def write_to_db(self):
        msg = self.db_connector.write_to_db(self.output_table_name, data=self.content)
        if msg == "Done!":
            with open(f'{PROJECT_ABSOLUTE_PATH}/docs/db_connect.back', 'wb') as f:
                if not self.db_remember_passwd:
                    self.passport['password'] = ""
                pickle.dump(self.passport, f)
        return msg

    def img_preprocessing(self):
        """cv2 预处理图片"""
        try:
            self.img_manager.set_img(self.img_path)
        except NotAImgException:
            self.content = None
        self.img_manager.manage_img()
        pass

    def parse_img_to_text(self):
        """tesseracts 将图片转文本,转换的内容保存在self.content中"""
        self.content = self.img_manager.parse_pic_to_text()

    def parse_img_to_excel(self):
        """tesseracts 将图片转表格, 转换的内容保存在self.content中"""
        self.content = self.img_manager.parse_pic_to_excel_data()

    def img_preview(self):
        """导入数据库前先在UI预览，并由用户修正好后再导入"""
        pass

    def load_passport(self):
        try:
            with open(f"{PROJECT_ABSOLUTE_PATH}/docs/db_connect.back", 'rb')as f:
                passport: dict = pickle.load(f)
                if list(passport.keys()) == STD_PASSPORT_INDEX:
                    self.passport = passport
                    self.set_all_info(passport)
        # 找不到序列化文件
        except FileNotFoundError:
            f = open(f"{PROJECT_ABSOLUTE_PATH}/docs/db_connect.back", 'wb')
            f.close()
        # 文件为空
        except EOFError:
            return
