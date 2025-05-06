def test_login_logout(client, _db):
    from app.models import User

    user = User(email='login@example.com')
    user.set_password('password123')
    _db.session.add(user)
    _db.session.commit()

    # Attempt login — change 'username' to 'email'
    response = client.post('/login', data={
        'email': 'login@example.com',   # ✅ fixed key
        'password': 'password123'
    }, follow_redirects=True)

    assert b"Logout" in response.data  # Adjust message as needed

    # Attempt logout
    response = client.get('/logout', follow_redirects=True)
    assert b"Login" in response.data
