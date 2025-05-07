def test_homepage(client):
    """
    Test that the homepage loads successfully.
    """
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome" in response.data  # Adjust to match your homepage content

def test_404(client):
    """
    Test that a non-existent route returns a 404.
    """
    response = client.get('/nonexistent')
    assert response.status_code == 404

def test_locations_page_requires_login(client):
    """
    Test that the locations page requires login.
    """
    response = client.get('/locations')
    assert response.status_code == 302  # Redirect to login page

def test_locations_page_loads(client, auth):
    """
    Test that the locations page loads successfully for logged in users.
    """
    auth.login()  # Login as test user
    response = client.get('/locations')
    assert response.status_code == 200
    assert b"My Locations" in response.data
    assert b"Add New Location" in response.data

def test_add_location(client, auth):
    """
    Test adding a new location.
    """
    auth.login()  # Login as test user
    
    # Test adding a location
    response = client.post('/locations', data={
        'name': 'Test Location',
        'address': '123 Test St'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Location saved successfully!" in response.data
    assert b"Test Location" in response.data
    assert b"123 Test St" in response.data

def test_add_location_validation(client, auth):
    """
    Test validation when adding a location.
    """
    auth.login()  # Login as test user
    
    # Test adding a location with missing fields
    response = client.post('/locations', data={
        'name': '',  # Empty name
        'address': '123 Test St'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Both name and address are required" in response.data

    # Test adding a location with missing address
    response = client.post('/locations', data={
        'name': 'Test Location',
        'address': ''  # Empty address
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Both name and address are required" in response.data