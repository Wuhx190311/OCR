from ocr.database_connector import Database_connector


def connect():
    c = Database_connector()
    passport = dict(db_username='root',
                    db_host='localhost',
                    db_password='password',
                    db_dbname='n')
    # print(**passport)

    c.set_all_info(**passport)

    print(c.connect_db())


if __name__ == '__main__':
    connect()
