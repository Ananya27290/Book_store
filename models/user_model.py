# models/user_model.py
from config import get_db
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, full_name, email, role):
        self.id = id
        self.full_name = full_name
        self.email = email
        self.role = role

    @staticmethod
    def get_by_id(user_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return User(row['id'], row['full_name'], row['email'], row['role'])
        return None
