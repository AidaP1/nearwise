from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager
import requests
from sqlalchemy import inspect


app = Flask(__name__)  # <-- This exact line must exist
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key')  # fallback for local

login_manager = LoginManager(app)
login_manager.login_view = 'login'  # endpoint name for login page

# Load environment variables from .env file (for secrets and config)
load_dotenv()

# Configure database URL
basedir = os.path.abspath(os.path.dirname(__file__))
if os.environ.get('RENDER') == 'true':
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'myapp.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # disable FSADeprecationWarning
db = SQLAlchemy(app)

def init_database():
    try:
        with app.app_context():
            print("Attempting to initialize database...")
            print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
            # Check if tables exist and create them if they don't
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            print(f"Existing tables: {existing_tables}")
            
            if not existing_tables:
                print("No existing tables found. Creating database tables...")
                db.create_all()
                print("Database tables created successfully!")
            else:
                print("Tables already exist in the database.")
    except Exception as e:
        print(f"Error during database initialization: {str(e)}")
        raise

# Initialize database
init_database()

class User(db.Model, UserMixin):
    __tablename__ = 'user'  # Explicitly set table name
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    # One-to-many relationship
    locations = db.relationship('Location', backref='user', lazy=True)

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))  # e.g. "Work", "Home", "Client HQ"
    address = db.Column(db.String(255), nullable=False)  # or lat/lng if you prefer
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from flask import request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))  # if logged in, skip register
    if request.method == 'POST':
        try:
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
        except Exception as e:
            flash(f"An error occurred: {str(e)}")
            db.session.rollback()
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            password = request.form.get('password')
            user = User.query.filter_by(email=email).first()
            if user and check_password_hash(user.password_hash, password):
                login_user(user)  # log the user in
                return redirect(url_for('home'))
            else:
                flash("Invalid credentials.")
        except Exception as e:
            flash(f"An error occurred: {str(e)}")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have logged out.")
    return redirect(url_for('home'))

@app.route('/api/travel_times')
def travel_times():
    origin = request.args.get('origin')  # e.g., "New York, NY"
    destination = request.args.get('destination')  # e.g., "Boston, MA"

    if not origin or not destination:
        return {"error": "Please provide both origin and destination."}, 400

    api_key = os.environ.get('GOOGLE_API_KEY')
    modes = ['driving', 'walking', 'bicycling', 'transit']
    results = {}

    for mode in modes:
        url = (
            f"https://maps.googleapis.com/maps/api/distancematrix/json"
            f"?origins={origin}&destinations={destination}"
            f"&mode={mode}&key={api_key}"
        )
        response = requests.get(url)
        data = response.json()

        if data['status'] == 'OK':
            try:
                duration = data['rows'][0]['elements'][0]['duration']['text']
                results[mode] = duration
            except (KeyError, IndexError):
                results[mode] = "Not available"
        else:
            results[mode] = "Error contacting API"

    return results

@app.route('/add_location', methods=['GET', 'POST'])
@login_required
def add_location():
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')

        if not name or not address:
            flash('Both name and address are required.')
            return redirect(url_for('add_location'))

        # Create and save new location
        new_loc = Location(name=name, address=address, user_id=current_user.id)
        db.session.add(new_loc)
        db.session.commit()
        flash('Location saved successfully!')
        return redirect(url_for('add_location'))

    return render_template('add_location.html')

@app.route('/my_locations')
@login_required
def my_locations():
    locations = Location.query.filter_by(user_id=current_user.id).all()
    return render_template('my_locations.html', locations=locations)

@app.route('/compare_travel', methods=['GET', 'POST'])
@login_required
def compare_travel():
    if request.method == 'POST':
        new_location = request.form.get('new_location')
        saved_location_id = request.form.get('saved_location_id')

        saved_location = Location.query.filter_by(id=saved_location_id, user_id=current_user.id).first()

        if not new_location or not saved_location:
            flash("Missing information or invalid saved location.")
            return redirect(url_for('compare_travel'))

        # Call Google API
        api_key = os.environ.get('GOOGLE_API_KEY')
        modes = ['driving', 'walking', 'bicycling', 'transit']
        results = {}

        for mode in modes:
            url = (
                f"https://maps.googleapis.com/maps/api/distancematrix/json"
                f"?origins={new_location}&destinations={saved_location.address}"
                f"&mode={mode}&key={api_key}"
            )
            response = requests.get(url)
            data = response.json()

            if data['status'] == 'OK':
                try:
                    duration = data['rows'][0]['elements'][0]['duration']['text']
                    results[mode] = duration
                except (KeyError, IndexError):
                    results[mode] = "Unavailable"
            else:
                results[mode] = "API error"

        return render_template(
            'travel_results.html',
            new_location=new_location,
            saved_location=saved_location,
            results=results
        )

    # GET: show form
    saved_locations = Location.query.filter_by(user_id=current_user.id).all()
    return render_template('compare_travel.html', saved_locations=saved_locations)



@app.route("/")
def home():
    if current_user.is_authenticated:
        return render_template('home.html', user=current_user)
    return render_template('home.html')

@app.route("/index")
def index():
    return redirect(url_for('home'))

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)



