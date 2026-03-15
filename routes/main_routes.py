# routes/main_routes.py
# routes/main_routes.py

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from config import get_db

main_bp = Blueprint('main', __name__)

# -------------------------------------------------
# Home Page
# -------------------------------------------------
@main_bp.route('/')
def home():
    return render_template('main.html')


# -------------------------------------------------
# User Profile Page
# -------------------------------------------------
@main_bp.route('/profile')
@login_required
def profile():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    # Fetch logged-in user details
    cursor.execute(
        "SELECT id, name, email, role FROM user WHERE id = %s",
        (current_user.id,)
    )
    user = cursor.fetchone()

    # Fetch user orders
    cursor.execute("""
        SELECT 
            o.id AS order_id,
            o.order_date,
            o.status,
            b.title,
            oi.quantity,
            b.price,
            (oi.quantity * b.price) AS total_price
        FROM `order` o
        JOIN order_item oi ON o.id = oi.order_id
        JOIN book b ON oi.book_id = b.id
        WHERE o.user_id = %s
        ORDER BY o.order_date DESC
    """, (current_user.id,))

    orders = cursor.fetchall()
    conn.close()

    return render_template('profile.html', user=user, orders=orders)


# -------------------------------------------------
# Order Confirmation Page
# -------------------------------------------------
@main_bp.route('/order_confirmation')
@login_required
def order_confirmation():
    order_id = request.args.get('order_id')
    return render_template('order_confirmation.html', order_id=order_id)
