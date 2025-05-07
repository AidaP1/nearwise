from app.utils.password import is_password_secure


def test_password_security():
    """
    Test password security requirements
    """
    # Test too short password
    is_secure, message = is_password_secure("Abc1!")
    assert not is_secure
    assert "8 characters" in message

    # Test missing uppercase
    is_secure, message = is_password_secure("password123!")
    assert not is_secure
    assert "uppercase" in message

    # Test missing lowercase
    is_secure, message = is_password_secure("PASSWORD123!")
    assert not is_secure
    assert "lowercase" in message

    # Test missing number
    is_secure, message = is_password_secure("Password!")
    assert not is_secure
    assert "number" in message

    # Test missing special character
    is_secure, message = is_password_secure("Password123")
    assert not is_secure
    assert "special character" in message

    # Test valid password
    is_secure, message = is_password_secure("SecurePass123!")
    assert is_secure
    assert "secure" in message

def test_login_logout(client, db_session):
    from app.models import User

    user = User(email='login@example.com')
    user.set_password('password123')
    db_session.session.add(user)
    db_session.session.commit()

    # Attempt login — change 'username' to 'email'
    response = client.post('/login', data={
        'email': 'login@example.com',   # ✅ fixed key
        'password': 'password123'
    }, follow_redirects=True)

    assert b"Logout" in response.data  # Adjust message as needed

    # Attempt logout
    response = client.get('/logout', follow_redirects=True)
    assert b"Login" in response.data
