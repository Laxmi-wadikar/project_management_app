from flask import Flask, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_cors import CORS
from functools import wraps

# Initialize extensions globally (no app bound yet)
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this in production!
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://flaskuser:tew%40123@localhost/flask_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Optional: load from config.py if you need more flexibility
    # app.config.from_object("config.Config")

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    CORS(app)

    login_manager.login_view = 'main.login'

    # Import models so they are registered with SQLAlchemy
    from app.models import User, Client_data, DailyEntry, WeeklyReport

    # Flask-Login user loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Role-based access decorator
    def roles_required(*roles):
        def wrapper(f):
            @wraps(f)
            def decorated_view(*args, **kwargs):
                if not current_user.is_authenticated or current_user.role not in roles:
                    flash("Access denied.", "danger")
                    return redirect(url_for('main.dashboard'))  # Adjust route if needed
                return f(*args, **kwargs)
            return decorated_view
        return wrapper

    # Make decorator available in templates
    app.jinja_env.globals['roles_required'] = roles_required

    # Register Blueprints
    from app.routes import main
    app.register_blueprint(main)

    return app




