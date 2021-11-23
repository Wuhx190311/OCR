from ocr.img_manager import Img_manager
import os
import main

PROJECT_ABSOLUTE_PATH = os.path.dirname(os.path.abspath(main.__file__))
os.chdir(PROJECT_ABSOLUTE_PATH)


def img_test():
    m = Img_manager()
    m.set_img(img_path='images/table.png')
    m.manage_img()
    df = m.img_to_table()
    # __txt = m.parse_pic_to_text()
    print(df)


if __name__ == '__main__':
    img_test()
