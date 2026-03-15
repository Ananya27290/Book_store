# config.py
import pymysql
import os

def get_db():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "online_book_store"),
        cursorclass=pymysql.cursors.DictCursor
    )
