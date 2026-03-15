# routes/book_routes.py
from flask import Blueprint, render_template
from flask_login import login_required
from config import get_db

book_bp = Blueprint('book', __name__, url_prefix='/books')

@book_bp.route('/')
@login_required
def list_books():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.id, b.title, b.author, b.price, b.cover_image, c.name AS category
        FROM book b
        LEFT JOIN category c ON b.category_id = c.id
    """)
    books = cursor.fetchall()
    conn.close()
    return render_template('books.html', books=books)
