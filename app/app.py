from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='user')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Role Decorator
def roles_required(*roles):
    def wrapper(f):
        @wraps(f)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                flash("Access denied.", "danger")
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_view
    return wrapper

# Routes
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash("Invalid credentials", "danger")
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/admin')
@login_required
@roles_required('admin')
def admin():
    return 'Welcome to Admin Panel!'

@app.route('/editor')
@login_required
@roles_required('editor', 'admin')
def editor():
    return 'Welcome Editor!'

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Only run once to create the DB and a test user
@app.cli.command("initdb")
def initdb():
    db.create_all()
    admin = User(username="admin", password=generate_password_hash("admin123"), role="admin")
    editor = User(username="editor", password=generate_password_hash("editor123"), role="editor")
    user = User(username="user", password=generate_password_hash("user123"), role="user")
    hashed_password = generate_password_hash(request.form['password'], method='sha256')
    new_user = User(username=request.form['username'], password=hashed_password, role='user')
    db.session.add(new_user)
    db.session.commit()

    db.session.add_all([admin, editor, user])
    db.session.commit()
    print("Initialized the database with default users.")

if __name__ == '__main__':
    app.run(debug=True)
