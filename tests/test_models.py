from app.models import User, Location
from app.utils.password import is_password_secure
from sqlalchemy.exc import IntegrityError

def test_create_user(db_session):
    """
    Test creating a new user and saving to the database.
    """
    user = User(email='test@example.com')
    user.set_password('securepass')
    db_session.session.add(user)
    db_session.session.commit()
    assert db_session.session.query(User).count() == 1
    assert User.query.first().email == 'test@example.com'

def test_unique_email_constraint(db_session):
    """
    Test that creating two users with the same email fails if you have a unique constraint.
    """
    user1 = User(email='unique@example.com')
    user2 = User(email='unique@example.com')
    user1.set_password('securepass')
    user2.set_password('securepass')
    db_session.session.add(user1)
    db_session.session.commit()
    db_session.session.add(user2)
    try:
        db_session.session.commit()
        assert False, "Should have raised an IntegrityError"
    except Exception as e:
        db_session.session.rollback()
        assert "UNIQUE constraint" in str(e)

def test_create_location(db_session):
    """
    Test creating a new location with coordinates and saving to the database.
    """
    # Create a user first
    user = User(email='test@example.com')
    user.set_password('securepass')
    db_session.session.add(user)
    db_session.session.commit()

    # Create a location
    location = Location(
        name='Home',
        address='123 Main St, City, State',
        latitude=40.7128,
        longitude=-74.0060,
        user_id=user.id
    )
    db_session.session.add(location)
    db_session.session.commit()

    # Verify the location was saved correctly
    saved_location = Location.query.first()
    assert saved_location.name == 'Home'
    assert saved_location.address == '123 Main St, City, State'
    assert saved_location.latitude == 40.7128
    assert saved_location.longitude == -74.0060
    assert saved_location.user_id == user.id

def test_location_user_relationship(db_session):
    """
    Test the relationship between Location and User models.
    """
    # Create a user
    user = User(email='test@example.com')
    user.set_password('securepass')
    db_session.session.add(user)
    db_session.session.commit()

    # Create multiple locations for the user
    locations = [
        Location(
            name='Home',
            address='123 Main St',
            latitude=40.7128,
            longitude=-74.0060,
            user_id=user.id
        ),
        Location(
            name='Work',
            address='456 Work Ave',
            latitude=40.7589,
            longitude=-73.9851,
            user_id=user.id
        )
    ]
    db_session.session.add_all(locations)
    db_session.session.commit()

    # Verify the relationship
    assert len(user.locations) == 2
    assert user.locations[0].name == 'Home'
    assert user.locations[1].name == 'Work'

def test_location_required_fields(db_session):
    """
    Test that required fields (address, user_id, latitude, longitude) cannot be null.
    """
    user = User(email='test@example.com')
    user.set_password('securepass')
    db_session.session.add(user)
    db_session.session.commit()

    # Test missing address
    location_no_address = Location(
        name='No Address',
        latitude=40.7128,
        longitude=-74.0060,
        user_id=user.id
    )
    db_session.session.add(location_no_address)
    try:
        db_session.session.commit()
        assert False, "Should have raised an IntegrityError for missing address"
    except IntegrityError:
        db_session.session.rollback()

    # Test missing user_id
    location_no_user = Location(
        name='No User',
        address='Some Address',
        latitude=40.7128,
        longitude=-74.0060
    )
    db_session.session.add(location_no_user)
    try:
        db_session.session.commit()
        assert False, "Should have raised an IntegrityError for missing user_id"
    except IntegrityError:
        db_session.session.rollback()

    # Test missing latitude
    location_no_lat = Location(
        name='No Latitude',
        address='Some Address',
        longitude=-74.0060,
        user_id=user.id
    )
    db_session.session.add(location_no_lat)
    try:
        db_session.session.commit()
        assert False, "Should have raised an IntegrityError for missing latitude"
    except IntegrityError:
        db_session.session.rollback()

    # Test missing longitude
    location_no_lng = Location(
        name='No Longitude',
        address='Some Address',
        latitude=40.7128,
        user_id=user.id
    )
    db_session.session.add(location_no_lng)
    try:
        db_session.session.commit()
        assert False, "Should have raised an IntegrityError for missing longitude"
    except IntegrityError:
        db_session.session.rollback()