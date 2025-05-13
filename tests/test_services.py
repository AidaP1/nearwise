import pytest
from unittest.mock import patch
from app.services.travel import get_travel_times, compare_locations
from app.models import Location, User

# Mock API response for get_travel_times
@pytest.fixture
def mock_api_response():
    return {
        'status': 'OK',
        'rows': [
            {
                'elements': [
                    {
                        'duration': {'text': '30 mins'},
                        'distance': {'text': '5.2 km'}
                    }
                ]
            }
        ]
    }

# Test get_travel_times
def test_get_travel_times(mock_api_response):
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_api_response
        origin_coords = (40.7128, -74.0060)  # New York coordinates
        dest_coords = (42.3601, -71.0589)    # Boston coordinates
        results = get_travel_times(origin_coords, dest_coords)
        
        expected_result = {
            'duration': '30 mins',
            'distance': '5.2 km'
        }
        
        assert results['driving'] == expected_result
        assert results['walking'] == expected_result
        assert results['bicycling'] == expected_result
        assert results['transit'] == expected_result

# Test get_travel_times with missing inputs 
def test_get_travel_times_missing_inputs():
    with pytest.raises(ValueError):
        get_travel_times(None, (42.3601, -71.0589))
    with pytest.raises(ValueError):
        get_travel_times((40.7128, -74.0060), None)

# Test compare_locations
def test_compare_locations(mock_api_response, db_session):
    # Create a test user and location in the database
    user = User(email='test@example.com')
    user.set_password('password123')
    db_session.session.add(user)
    db_session.session.commit()

    # Create location with coordinates
    location = Location(
        name='Test Location',
        address='New York',
        latitude=40.7128,
        longitude=-74.0060,
        user_id=user.id
    )
    db_session.session.add(location)
    db_session.session.commit()

    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_api_response
        new_coords = (42.3601, -71.0589)  # Boston coordinates
        saved_location, results = compare_locations(new_coords, location.id, user.id)
        
        assert saved_location.latitude == 40.7128
        assert saved_location.longitude == -74.0060
        
        expected_result = {
            'duration': '30 mins',
            'distance': '5.2 km'
        }
        assert results['driving'] == expected_result

# Test compare_locations with invalid location
def test_compare_locations_invalid_location(db_session):
    with pytest.raises(ValueError):
        compare_locations((42.3601, -71.0589), 999, 1)  # Non-existent location ID

# Test compare_locations with missing coordinates
def test_compare_locations_missing_coordinates(db_session):
    """Test that comparing locations with invalid coordinates raises an error."""
    # Create a test user
    user = User(email='test@example.com')
    user.set_password('password123')  # Set a password for the user
    db_session.session.add(user)
    db_session.session.commit()

    # Add a location with invalid coordinates
    location = Location(
        name='Test Location',
        address='123 Test St',
        user_id=user.id,
        latitude=200.0,  # Invalid latitude (should be between -90 and 90)
        longitude=-74.0060
    )
    db_session.session.add(location)
    db_session.session.commit()

    # Test that comparing locations with invalid coordinates raises an error
    with pytest.raises(ValueError, match="Invalid coordinates"):
        compare_locations((40.7128, -74.0060), location.id, user.id)