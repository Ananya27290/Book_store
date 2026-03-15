from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import login_required, current_user
from config import get_db
from datetime import datetime

orders_bp = Blueprint('orders', __name__)

# 🛒 Checkout Page
@orders_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    conn = get_db()
    cursor = conn.cursor()

    # Get items in cart for current user
    cursor.execute("""
        SELECT c.id AS cart_id, b.id AS book_id, b.title, b.price, c.quantity, (b.price * c.quantity) AS total
        FROM cart c
        JOIN book b ON c.book_id = b.id
        WHERE c.user_id = %s
    """, (current_user.id,))
    cart_items = cursor.fetchall()

    # Calculate total amount
    total_amount = sum(item['total'] for item in cart_items)

    return render_template('checkout.html', cart_items=cart_items, total_amount=total_amount)

# ✅ Place Order Route
@orders_bp.route('/place_order', methods=['POST'])
@login_required
def place_order():
    conn = get_db()
    cursor = conn.cursor()

    user_id = current_user.id
    order_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Fetch cart items
    cursor.execute("""
        SELECT c.book_id, b.price, c.quantity
        FROM cart c
        JOIN book b ON c.book_id = b.id
        WHERE c.user_id = %s
    """, (user_id,))
    cart_items = cursor.fetchall()

    if not cart_items:
        flash("Your cart is empty. Cannot place order.", "danger")
        return redirect(url_for('cart.view_cart'))

    # Calculate total amount
    total_amount = sum(item['price'] * item['quantity'] for item in cart_items)

    # Insert into order table
    cursor.execute("""
        INSERT INTO `order` (user_id, order_date, total, status)
        VALUES (%s, %s, %s, %s)
    """, (user_id, order_date, total_amount, 'Pending'))
    conn.commit()
    order_id = cursor.lastrowid

    # Insert into order_item table
    for item in cart_items:
        cursor.execute("""
            INSERT INTO order_item (order_id, book_id, quantity, price)
            VALUES (%s, %s, %s, %s)
        """, (order_id, item['book_id'], item['quantity'], item['price']))
    conn.commit()

    # Insert payment info
    cursor.execute("""
        INSERT INTO payment (order_id, payment_date, amount, status)
        VALUES (%s, %s, %s, %s)
    """, (order_id, order_date, total_amount, 'Success'))
    conn.commit()

    # Clear user's cart
    cursor.execute("DELETE FROM cart WHERE user_id = %s", (user_id,))
    conn.commit()

    flash("Order placed successfully!", "success")

    # Redirect to payment success page with order_id
    return redirect(url_for('orders.payment_success', order_id=order_id))

# 📦 Payment Success Page
@orders_bp.route('/payment_success/<int:order_id>')
@login_required
def payment_success(order_id):
    conn = get_db()
    cursor = conn.cursor()

    # Fetch order items
    cursor.execute("""
        SELECT oi.book_id, b.title, oi.quantity, oi.price, (oi.quantity * oi.price) AS total
        FROM order_item oi
        JOIN book b ON oi.book_id = b.id
        WHERE oi.order_id = %s
    """, (order_id,))
    cart_items = cursor.fetchall()

    # Fetch payment info
    cursor.execute("""
        SELECT amount, payment_date, status
        FROM payment
        WHERE order_id = %s
    """, (order_id,))
    payment = cursor.fetchone()

    return render_template(
        'payment_success.html',
        order_id=order_id,
        cart_items=cart_items,
        payment=payment
    )

# 📦 View My Orders
@orders_bp.route('/my_orders')
@login_required
def my_orders():
    conn = get_db()
    cursor = conn.cursor()

    # Get all orders for the current user
    cursor.execute("SELECT * FROM `order` WHERE user_id = %s ORDER BY order_date DESC", (current_user.id,))
    orders = cursor.fetchall()

    order_list = []

    for order in orders:
        order_id = order['id']
        cursor.execute("""
            SELECT b.title, oi.quantity, b.price, (oi.quantity * b.price) AS total_price
            FROM order_item oi
            JOIN book b ON oi.book_id = b.id
            WHERE oi.order_id = %s
        """, (order_id,))
        items = cursor.fetchall()

        # Calculate total for this order
        total = sum(item['total_price'] for item in items)

        order_data = {
            'order_id': order_id,
            'order_date': order['order_date'].strftime('%Y-%m-%d'),
            'status': order['status'],
            'items': items,
            'total': total
        }
        order_list.append(order_data)

    return render_template('user_orders.html', orders=order_list)
