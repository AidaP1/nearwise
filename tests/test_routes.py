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