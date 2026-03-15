from werkzeug.security import generate_password_hash
import pymysql

# Connect to your DB
conn = pymysql.connect(host='localhost', user='root', password='', db='online_book_store', cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

# Admin credentials
admin_email = 'admin12@example.com'
admin_password = 'admin@123'

# Generate proper hash
hashed_password = generate_password_hash(admin_password)
print(hashed_password)