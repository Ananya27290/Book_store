# config.py
import pymysql

def get_db():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='online_book_store',
        cursorclass=pymysql.cursors.DictCursor
    )
