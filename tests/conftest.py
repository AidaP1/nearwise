import pytest
from app import create_app, db
from app.config import TestConfig

@pytest.fixture(scope='session')
def app():
    """
    Create and configure a new app instance for each test session.
    Uses the TestConfig to ensure the test database is used.
    """
    app = create_app(TestConfig)
    with app.app_context():
        yield app

@pytest.fixture(scope='session')
def client(app):
    """
    Returns a test client for the app.
    """
    return app.test_client()

@pytest.fixture(scope='session')
def _db(app):
    """
    Returns a database instance for the tests.
    Drops and creates all tables at the start of the session.
    """
    db.app = app
    db.drop_all()
    db.create_all()
    yield db
    db.session.remove()
    db.drop_all()
