import re

import numpy as np
import sys
import os
import pandas as pd

import pytesseract
from cv2 import cv2

TEMP_PATH = './temp'  # 这里的根路径时调用者GUI_test的路径


class NotAImgException(Exception):
    def __init__(self, msg):
        super.__init__(msg)
        self.msg = f"{msg} is not a image"


class Img_manager:

    def __init__(self, img_path: str = ''):
        self.__raw = None
        self.__img = None
        self.__txt = ''
        self.__df: pd.DataFrame = pd.DataFrame()
        self.set_img(img_path)

    def set_img(self, img_path: str):
        if '' == img_path:
            return
        img_name = str(os.path.split(img_path)[-1])
        if img_name.endswith('.jpg') | img_name.endswith('.png'):
            self.__raw = self.__img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), -1)
        else:
            raise NotAImgException(img_path)

    # get grayscale image
    @staticmethod
    def get_grayscale(image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # noise removal
    @staticmethod
    def remove_noise(image):
        return cv2.medianBlur(image, 5)

    # thresholding
    @staticmethod
    def thresholding(image):
        # ret, thresh = cv2.threshold(image, 240, 255, cv2.THRESH_BINARY)
        thresh = cv2.adaptiveThreshold(~image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 35, -5)
        # ret, thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh

    # dilation
    @staticmethod
    def dilate(image):
        kernel = np.ones((5, 5), np.uint8)
        return cv2.dilate(image, kernel, iterations=1)

    # erosion
    @staticmethod
    def erode(image):
        kernel = np.ones((5, 5), np.uint8)
        return cv2.erode(image, kernel, iterations=1)

    # opening - erosion followed by dilation
    @staticmethod
    def opening(image):
        kernel = np.ones((5, 5), np.uint8)
        return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

    # canny edge detection
    @staticmethod
    def canny(image):
        return cv2.Canny(image, 100, 200)

    # skew correction
    @staticmethod
    def deskew(image):
        coords = np.column_stack(np.where(image > 0))
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated

    # template matching
    @staticmethod
    def match_template(image, template):
        return cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)

    def manage_img(self):
        if self.__img is None:
            return None
        # 灰度图片
        gray_img = self.get_grayscale(self.__img)
        # 二值化
        binary_img = self.thresholding(gray_img)

        self.__img = binary_img
        self.save_img('binary_img')
        return binary_img

    def parse_pic_to_text(self) -> str:
        if self.__img is None:
            return ''
        txt = pytesseract.image_to_string(self.__img, lang='chi_sim')
        self.__txt = txt
        return str(txt)

    def parse_pic_to_excel_data(self):
        if self.__img is None:
            return None
        df = self.img_to_table()
        self.__df = df
        return df

    def show_img(self):
        if self.__img is None:
            return
        cv2.imshow("picture", self.__img)  # 展示图片
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def save_img(self, filename: str = 'temp'):
        if self.__img is None:
            return
        path = f'{TEMP_PATH}/temp_{filename}.jpg'
        cv2.imwrite(path, self.__img)

    @staticmethod
    def save_other_img(img, filename: str = 'temp'):

        path = f'{TEMP_PATH}/temp_{filename}.jpg'
        cv2.imwrite(path, img)
        pass

    #  横纵向直线检测
    def img_to_table(self) -> pd.DataFrame:
        """
        将图片转换成pandas表格
        :return: pandas.DataFrame
        """
        # self.manage_img()
        # Canny边缘检测
        edges = cv2.Canny(self.__img, 100, 200)
        # cv2.imshow('hough', edges)
        # cv2.waitKey(0)

        # Hough直线检测
        minLineLength = 400
        maxLineGap = 40
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength, maxLineGap).tolist()
        sorted_lines = sorted(lines, key=lambda x: x[0])
        # 纵向直线列表
        vertical_lines = []
        # 横向直线列表
        horizontal_lines = []
        for line in sorted_lines:
            for x1, y1, x2, y2 in line:
                # 提取纵向直线x坐标
                if abs(x1 - x2) < 1:
                    div = [abs(x - x1) for x in vertical_lines]
                    if len(div) > 0:
                        if min(div) < 6:
                            continue
                    vertical_lines.append(x1)
            for x1, y1, x2, y2 in line:
                # 提取横向直线y坐标
                if abs(y1 - y2) < 1:
                    div = [abs(y - y1) for y in horizontal_lines]

                    if len(div) > 0:
                        if min(div) < 6:
                            continue
                    horizontal_lines.append(y1)

        vertical_lines = sorted(vertical_lines)
        horizontal_lines = sorted(horizontal_lines)

        # 交叉点坐标
        h_line = (horizontal_lines[0], horizontal_lines[-1])
        v_line = (vertical_lines[0], vertical_lines[-1])

        # 高亮单元格分割线
        for y in horizontal_lines:
            cv2.line(self.__raw, (v_line[0], y), (v_line[1], y), (0, 0, 255), 2)

        for x in vertical_lines:
            cv2.line(self.__raw, (x, h_line[0]), (x, h_line[-1]), (0, 0, 255), 2)

        # cv2.imshow('hough', self.__raw)
        # cv2.waitKey(0)

        lines = pd.DataFrame()
        for i in range(len(horizontal_lines) - 1):
            line = pd.Series()
            for j in range(len(vertical_lines) - 1):
                # 在分割时，第一个参数为y坐标，第二个参数为x坐标
                cell = self.__raw[horizontal_lines[i]:horizontal_lines[i + 1], vertical_lines[j]:vertical_lines[j + 1]]

                # 查看每个cell
                # cv2.imshow('hough', cell)
                # cv2.waitKey(0)

                txt = pytesseract.image_to_string(cell, config='--psm 6')  # , lang='chi_sim'
                # 一个内由多行时，将这多行存入pandas.series中等待后续拼接
                s = pd.Series(txt.splitlines())

                # 去除一列中的‘’值
                count = 0
                for txt in s:
                    if txt == '':
                        s.drop(count, inplace=True)
                    count += 1
                s.dropna(inplace=True, how="any")
                # 重构索引
                s = s.reset_index(drop=True)

                # 列拼接
                line = pd.concat([line, s], axis=1, ignore_index=True)
            # 丢弃全为NaN的列（该列在 line = pd.Series() 初始化时产生）
            line.dropna(axis=1, inplace=True, how="all")
            # 行拼接
            lines = pd.concat([lines, line], axis=0)
        # 行拼接完成后重塑索引
        lines = lines.reset_index(drop=True)

        # 将第一行设为列名,并丢弃其作为数据的一行
        lines.columns = lines.iloc[0, :].to_list()
        lines.drop(index=0, inplace=True)

        # 重构索引
        lines = lines.reset_index(drop=True)
        return lines
