from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()  # Create LoginManager instance globally

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = 'your_secret_key_here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://tew:tew%40laxmi123@localhost:3306/project_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)  # Initialize LoginManager with app
    login_manager.login_view = 'main.login'  # Redirect unauthorized users to login page
    login_manager.login_message_category = 'info'  # Optional: flash category for login message
    
    from app.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
       return User.query.get(int(user_id))

    from .routes import main
    app.register_blueprint(main)


    return app
