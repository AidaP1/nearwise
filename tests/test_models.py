from app.models import User

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