from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager


app = Flask(__name__)  # <-- This exact line must exist

login_manager = LoginManager(app)
login_manager.login_view = 'login'  # endpoint name for login page

# Load environment variables from .env file (for secrets and config)
load_dotenv()

# Configure database URL
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'myapp.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # disable FSADeprecationWarning
db = SQLAlchemy(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from flask import request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))  # if logged in, skip register
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        # Simple validation:
        if not email or not password:
            flash("Please fill all fields.")
        elif User.query.filter_by(email=email).first():
            flash("That email address is already in use.")
        else:
            # create new user
            hashed_pw = generate_password_hash(password)
            new_user = User(email=email, password_hash=hashed_pw)
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful! Please log in.")
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)  # log the user in
            return redirect(url_for('index'))
        else:
            flash("Invalid credentials.")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have logged out.")
    return redirect(url_for('index'))

@app.route("/")
def home():
    return render_template('home.html')


