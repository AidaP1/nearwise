import pytest
from app import create_app, db
from app.config import TestConfig
from app.models import User

@pytest.fixture(scope='function')
def app():
    """
    Create a Flask app instance for the test session.
    """
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def db_session(app):
    """
    Provide a database session bound to a transaction, rolled back after each test.
    Compatible with Flask-SQLAlchemy 3.x (no direct assignment to db.session).
    """
    connection = db.engine.connect()
    transaction = connection.begin()

    # Bind the connection to the current session context
    db.session.bind = connection

    yield db

    transaction.rollback()
    connection.close()
    db.session.remove()

@pytest.fixture(scope='function')
def auth(client):
    """
    Authentication fixture that provides login/logout functionality for tests.
    """
    class AuthActions:
        def __init__(self, client):
            self._client = client

        def login(self, email='test@example.com', password='password'):
            # Create a test user if it doesn't exist
            user = User.query.filter_by(email=email).first()
            if not user:
                user = User(email=email)
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
            
            return self._client.post('/login', data={
                'email': email,
                'password': password
            }, follow_redirects=True)

        def logout(self):
            return self._client.get('/logout', follow_redirects=True)

    return AuthActions(client)
