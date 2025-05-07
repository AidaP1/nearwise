import pytest
from app import create_app, db
from app.config import TestConfig

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
