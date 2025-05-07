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
                        'duration': {'text': '30 mins'}
                    }
                ]
            }
        ]
    }

# Test get_travel_times
def test_get_travel_times(mock_api_response):
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_api_response
        results = get_travel_times('New York', 'Boston')
        assert results['driving'] == '30 mins'
        assert results['walking'] == '30 mins'
        assert results['bicycling'] == '30 mins'
        assert results['transit'] == '30 mins'

# Test get_travel_times with missing inputs 
def test_get_travel_times_missing_inputs():
    with pytest.raises(ValueError):
        get_travel_times('', 'Boston')
    with pytest.raises(ValueError):
        get_travel_times('New York', '')

# Test compare_locations
def test_compare_locations(mock_api_response, db_session):
    # Create a test user and location in the database
    user = User(email='test@example.com')
    user.set_password('password123')
    db_session.session.add(user)
    db_session.session.commit()

    location = Location(name='Test Location', address='New York', user_id=user.id)
    db_session.session.add(location)
    db_session.session.commit()

    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_api_response
        saved_location, results = compare_locations('Boston', location.id, user.id)
        assert saved_location.address == 'New York'
        assert results['driving'] == '30 mins'

# Test compare_locations with invalid location
def test_compare_locations_invalid_location(db_session):
    with pytest.raises(ValueError):
        compare_locations('Boston', 999, 1)  # Non-existent location ID