# routes/auth_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from models.user_model import User
from config import get_db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO user (full_name, email, password, role) VALUES (%s, %s, %s, 'user')",
                           (full_name, email, hashed_password))
            conn.commit()
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for('auth.login'))
        except Exception as e:
            conn.rollback()
            flash("Registration failed. Email may already be in use.", "danger")
        finally:
            conn.close()
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user WHERE email = %s", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            user_obj = User(user['id'], user['full_name'], user['email'], user['role'])
            login_user(user_obj)
            flash('Login successful!', 'success')  # ✅ Flash BEFORE redirect
            if user['role'] == 'admin':
                return redirect(url_for('admin.admin_dashboard'))
            else:
                return redirect(url_for('main.home'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html')
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
