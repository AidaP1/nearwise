from app.models import User

def test_create_user(_db):
    """
    Test creating a new user and saving to the database.
    """
    user = User(username='testuser', email='test@example.com')
    _db.session.add(user)
    _db.session.commit()
    assert User.query.count() == 1
    assert User.query.first().username == 'testuser'

def test_unique_email_constraint(_db):
    """
    Test that creating two users with the same email fails if you have a unique constraint.
    """
    user1 = User(username='user1', email='unique@example.com')
    user2 = User(username='user2', email='unique@example.com')
    _db.session.add(user1)
    _db.session.commit()
    _db.session.add(user2)
    try:
        _db.session.commit()
        assert False, "Should have raised an IntegrityError"
    except Exception as e:
        _db.session.rollback()
        assert "UNIQUE constraint" in str(e)