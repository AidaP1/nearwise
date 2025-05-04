from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import User, Location
from .. import db
from ..services.travel import get_travel_times, compare_locations

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def home():
    if current_user.is_authenticated:
        return render_template('home.html', user=current_user)
    return render_template('home.html')

@main_bp.route("/index")
def index():
    return redirect(url_for('main.home'))

@main_bp.route("/register", methods=["GET", "POST"])
def register_user():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))  # if logged in, skip register
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
                return redirect(url_for('main.login'))
        except Exception as e:
            flash(f"An error occurred: {str(e)}")
            db.session.rollback()
    return render_template('register.html')

@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            password = request.form.get('password')
            user = User.query.filter_by(email=email).first()
            if user and check_password_hash(user.password_hash, password):
                login_user(user)  # log the user in
                return redirect(url_for('main.home'))
            else:
                flash("Invalid credentials.")
        except Exception as e:
            flash(f"An error occurred: {str(e)}")
    return render_template('login.html')

@main_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have logged out.")
    return redirect(url_for("main.home"))

@main_bp.route("/my_locations")
@login_required
def my_locations():
    locations = Location.query.filter_by(user_id=current_user.id).all()
    return render_template('my_locations.html', locations=locations)

@main_bp.route("/add_location", methods=["GET", "POST"])
@login_required
def add_location():
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')

        if not name or not address:
            flash('Both name and address are required.')
            return redirect(url_for('main.add_location'))

        # Create and save new location
        new_loc = Location(name=name, address=address, user_id=current_user.id)
        db.session.add(new_loc)
        db.session.commit()
        flash('Location saved successfully!')
        return redirect(url_for('main.add_location'))

    return render_template('main.add_location.html')

@main_bp.route('/compare_travel', methods=['GET', 'POST'])
@login_required
def compare_travel():
    if request.method == 'POST':
        new_location = request.form.get('new_location')
        saved_location_id = request.form.get('saved_location_id')

        try:
            saved_location, results = compare_locations(
                new_location_address=new_location,
                saved_location_id=saved_location_id,
                user_id=current_user.id
            )
            return render_template(
                'travel_results.html',
                new_location=new_location,
                saved_location=saved_location,
                results=results
            )
        except Exception as e:
            flash(str(e))
            return redirect(url_for('main.compare_travel'))

    saved_locations = Location.query.filter_by(user_id=current_user.id).all()
    return render_template('compare_travel.html', saved_locations=saved_locations)