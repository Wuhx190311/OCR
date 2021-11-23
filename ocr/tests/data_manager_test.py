from ocr.data_manager import Data_manager


def test():
    m = Data_manager()
    m.load_passport()
    print(m.passport)


def dict_test():
    passport = dict(username='root',
                             host='localhost',
                             password='password',
                             db='')
    print(list(passport.keys()))


if __name__ == '__main__':
    test()
