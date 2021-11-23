import os

import cv2

import main

PROJECT_ABSOLUTE_PATH = os.path.dirname(os.path.abspath(main.__file__))
os.chdir(PROJECT_ABSOLUTE_PATH)


def write_to_file():
    PROJECT_ABSOLUTE_PATH = os.path.dirname(os.path.abspath(__file__))
    print('FILE_ABSOLUTE_PATH:%s' % PROJECT_ABSOLUTE_PATH)
    print(os.getcwd())
    # f = open('../../docs/test.txt', 'w')
    # f.write('dfs')


def vc2_path_test():
    cv2.bootstrap()


if __name__ == '__main__':
    vc2_path_test()
