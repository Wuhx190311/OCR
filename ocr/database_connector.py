import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String
import pymysql


class Database_connector:
    def __init__(self, name='root', password='password', host='localhost', db_name='orc_data'):
        self.__username = name
        self.__passwd = password
        self.__host = host
        self.__database = db_name

    def set_username(self, name):
        self.__username = name

    def set_passwd(self, key):
        self.__passwd = key

    def set_host(self, host):
        self.__host = host

    def set_database_name(self, db_name):
        self.__database = db_name

    def set_all_info(self, username, host, password, db):
        try:
            self.set_username(username)
            self.set_host(host)
            self.set_passwd(password)
            self.set_database_name(db)
        except KeyError:
            return

    def connect_db(self) -> str:
        """
        :return: connect message
        """
        try:
            db = pymysql.connect(host=self.__host, user=self.__username, password=self.__passwd, database=self.__database)
        except pymysql.err.OperationalError as e:
            error_msg = f"error: {e}"
            return error_msg
        cursor = db.cursor()
        cursor.execute("SELECT VERSION()")
        msg = str(f"Successful connected to database \nmysql version: {cursor.fetchone()[0]}")
        db.close()
        return msg

    def write_to_db(self, name: str, data: pd.DataFrame):
        if data is None:
            return "no input"
        engine = create_engine(
            f"mysql+pymysql://{self.__username}:{self.__passwd}@{self.__host}:3306/{self.__database}",
            encoding='utf-8', echo=True)
        try:
            data.to_sql(name, con=engine, if_exists='replace', index=False)
        except sqlalchemy.exc.OperationalError as e:
            error_msg = f"error: {e}"
            return error_msg
        return "Done!"
