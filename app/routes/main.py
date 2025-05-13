from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User, Location
from .. import db
from ..services.travel import compare_locations
from ..services.address import create_location_with_verified_address, verify_address
from ..utils.password import is_password_secure

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def home():
    if current_user.is_authenticated:
        return render_template('home.html', user=current_user)
    return render_template('home.html')

@main_bp.route("/register", methods=["GET", "POST"])
def register_user():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            password = request.form.get('password')
            if not email or not password:
                flash("Please fill all fields.")
            elif User.query.filter_by(email=email).first():
                flash("That email address is already in use.")
            else:
                is_secure, message = is_password_secure(password)
                if not is_secure:
                    flash(message)
                    return render_template('register.html')
                
                new_user = User(email=email)
                new_user.set_password(password)
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
            if user and user.check_password(password):
                login_user(user)
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

@main_bp.route("/locations", methods=["GET", "POST"])
@login_required
def locations():
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')

        if not name or not address:
            flash('Both name and address are required.')
        else:
            # Create location with verified address and coordinates
            success, location = create_location_with_verified_address(
                user_id=current_user.id,
                name=name,
                address=address
            )
            
            if success:
                flash('Location added successfully!')
                return redirect(url_for('main.locations'))
            else:
                flash('Could not verify the address. Please check and try again.')

    locations = Location.query.filter_by(user_id=current_user.id).all()
    return render_template('locations.html', locations=locations)

@main_bp.route('/compare_travel', methods=['GET', 'POST'])
@login_required
def compare_travel():
    if request.method == 'POST':
        new_location_address = request.form.get('new_location')
        saved_location_id = request.form.get('saved_location_id')

        if not new_location_address or not saved_location_id:
            flash('Both new location and saved location are required.')
            return redirect(url_for('main.compare_travel'))

        # Verify the new location address and get coordinates
        is_valid, details = verify_address(new_location_address)
        if not is_valid:
            flash('Could not verify the new location address. Please check and try again.')
            return redirect(url_for('main.compare_travel'))

        try:
            # Convert address to coordinates
            new_location_coords = (details['lat'], details['lng'])
            saved_location, results = compare_locations(
                new_location_coords=new_location_coords,
                saved_location_id=saved_location_id,
                user_id=current_user.id
            )
            return render_template(
                'travel_results.html',
                new_location=new_location_address,
                saved_location=saved_location,
                results=results
            )
        except Exception as e:
            flash(str(e))
            return redirect(url_for('main.compare_travel'))

    saved_locations = Location.query.filter_by(user_id=current_user.id).all()
    return render_template('compare_travel.html', saved_locations=saved_locations)