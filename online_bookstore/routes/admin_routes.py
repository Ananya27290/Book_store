from flask import Blueprint, render_template, request, redirect, url_for, flash,session
from flask_login import login_required, current_user
from config import get_db

admin_bp = Blueprint('admin', __name__)

# Ensure only admin can access
def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash("Admin access only.", "danger")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin Dashboard (Manage Books)
@admin_bp.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
                   SELECT b.id, b.title, b.author, b.price, b.stock, c.name AS category
        FROM book b
        LEFT JOIN category c ON b.category_id = c.id""")

    books = cursor.fetchall()
    conn.close()
    return render_template('admin_dashboard.html', books=books)

# Add Book
@admin_bp.route('/admin/book/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form.get('author')
        genre = request.form.get('genre')
        language = request.form.get('language')
        description = request.form.get('description')
        price = request.form.get('price')
        stock = request.form.get('stock')
        category_id = request.form.get('category_id')
        cover_image = request.form.get('cover_image')  # Store image path or URL

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO book (title, author, genre, language, description, price, stock, category_id, cover_image)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (title, author, genre, language, description, price, stock, category_id, cover_image))
        conn.commit()
        conn.close()

        flash('Book added successfully!', 'success')
        return redirect(url_for('book.list_books'))

    return render_template('admin_add_book.html')

# Edit Book
@admin_bp.route('/admin/book/edit/<int:book_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_book(book_id):
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        title = request.form['title']
        author = request.form.get('author')
        genre = request.form.get('genre')
        language = request.form.get('language')
        description = request.form.get('description')
        price = request.form.get('price')
        stock = request.form.get('stock')
        category_id = request.form.get('category_id')
        cover_image = request.form.get('cover_image')

        cursor.execute("""
            UPDATE book
            SET title=%s, author=%s, genre=%s, language=%s, description=%s,
                price=%s, stock=%s, category_id=%s, cover_image=%s
            WHERE id=%s
        """, (title, author, genre, language, description, price, stock, category_id, cover_image, book_id))
        conn.commit()
        conn.close()

        flash('Book updated successfully!', 'success')
        return redirect(url_for('book.list_books'))

    # For GET, fetch the current book details
    cursor.execute("SELECT * FROM book WHERE id = %s", (book_id,))
    book = cursor.fetchone()
    conn.close()

    return render_template('admin_edit_book.html', book=book)

# Delete Book
@admin_bp.route('/admin/delete_book/<int:book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    conn = get_db()
    cursor = conn.cursor()

    # Check if book is part of any order
    cursor.execute("SELECT * FROM order_item WHERE book_id = %s", (book_id,))
    if cursor.fetchone():
        flash("Cannot delete book. It is part of an existing order.", "danger")
        return redirect(url_for('admin.admin_dashboard'))  # Fixed endpoint

    # Safe to delete
    cursor.execute("DELETE FROM book WHERE id = %s", (book_id,))
    conn.commit()
    flash("Book deleted successfully.", "success")
    return redirect(url_for('admin.admin_dashboard'))  # Fixed endpoint

# View Orders (Admin)
@admin_bp.route('/admin/orders', endpoint='view_all_orders')
@login_required
@admin_required
def view_all_orders():
    conn = get_db()
    cursor = conn.cursor()
    
    # Order info
    cursor.execute("""
        SELECT 
            o.id AS order_id,
            u.full_name AS user_name,
            u.email,
            o.order_date,
            p.status AS payment_status,
            p.amount AS total_amount
        FROM `order` o
        JOIN user u ON o.user_id = u.id
        JOIN payment p ON o.id = p.order_id
        ORDER BY o.order_date DESC
    """)
    orders = cursor.fetchall()

    # Order items info
    cursor.execute("""
        SELECT oi.order_id, b.title, oi.quantity, b.price
        FROM order_item oi
        JOIN book b ON oi.book_id = b.id
    """)
    items = cursor.fetchall()
    conn.close()

    # Group items by order_id
    order_items = {}
    for item in items:
        order_id = item['order_id']
        if order_id not in order_items:
            order_items[order_id] = []
        order_items[order_id].append(item)

    return render_template('admin_orders.html', orders=orders, order_items=order_items)

# Update Order Status
@admin_bp.route('/admin/orders/<int:order_id>/update', methods=['POST'], endpoint='update_order_status')
@login_required
@admin_required
def update_order_status(order_id):
    new_status = request.form.get('status')

    conn = get_db()
    cursor = conn.cursor()

    # Update the status in payment table
    cursor.execute("""
        UPDATE payment
        SET status = %s
        WHERE order_id = %s
    """, (new_status, order_id))

    conn.commit()
    conn.close()

    flash("Order status updated successfully.", "success")
    return redirect(url_for('admin.view_all_orders'))
