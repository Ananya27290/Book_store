from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from config import get_db
from flask_login import login_required, current_user

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/cart')
@login_required
def view_cart():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id, b.title, c.quantity, b.price, (c.quantity * b.price) AS total
        FROM cart c
        JOIN book b ON c.book_id = b.id
        WHERE c.user_id = %s
    """, (current_user.id,))
    cart_items = cursor.fetchall()

    grand_total = sum(item['total'] for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, grand_total=grand_total)

@cart_bp.route('/add_to_cart/<int:book_id>', methods=['POST'])
@login_required
def add_to_cart(book_id):
    quantity = int(request.form['quantity'])

    conn = get_db()
    cursor = conn.cursor()

    # Check if book already in cart
    cursor.execute("SELECT * FROM cart WHERE user_id = %s AND book_id = %s", (current_user.id, book_id))
    existing_item = cursor.fetchone()

    if existing_item:
        cursor.execute("UPDATE cart SET quantity = quantity + %s WHERE id = %s", (quantity, existing_item['id']))
    else:
        cursor.execute("INSERT INTO cart (user_id, book_id, quantity) VALUES (%s, %s, %s)", (current_user.id, book_id, quantity))

    conn.commit()
    flash("Book added to cart.")
    return redirect(url_for('book.list_books'))
@cart_bp.route('/cart/remove/<int:cart_id>', methods=['POST'])
@login_required
def remove_from_cart(cart_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM cart WHERE id = %s AND user_id = %s", (cart_id, current_user.id))
    conn.commit()

    flash("Item removed from cart successfully.", "success")
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/checkout')
@login_required
def checkout():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.book_id, b.title, c.quantity, b.price
        FROM cart c
        JOIN book b ON c.book_id = b.id
        WHERE c.user_id = %s
    """, (current_user.id,))
    cart_items = cursor.fetchall()

    total_price = sum(item['quantity'] * item['price'] for item in cart_items)

    return render_template('checkout.html', cart_items=cart_items, total=total_price)

