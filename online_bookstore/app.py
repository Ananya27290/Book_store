# app.py
from flask import Flask
from routes.main_routes import main_bp
from routes.auth_routes import auth_bp
from routes.book_routes import book_bp
from routes.cart_routes import cart_bp
from routes.admin_routes import admin_bp
from routes.order_routes import orders_bp
from flask_login import LoginManager

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Register Blueprints

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(book_bp)
app.register_blueprint(cart_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(orders_bp)

# Flask-Login Config
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

from models.user_model import User

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

if __name__ == '__main__':
    app.run(debug=True)
    print(app.url_map)
print(app.url_map)

