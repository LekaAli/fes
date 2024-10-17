import pytest
from backend.app import create_app, db
from backend.models import Transaction
from backend.config import TestConfig


@pytest.fixture
def app():
    """Create a new app instance with test config for each test."""
    app = create_app()
    app.config.from_object(TestConfig)

    with app.app_context():
        db.create_all()  # Create an empty test database
        yield app
        db.session.remove()
        db.drop_all()  # Clean up the database after the test


@pytest.fixture
def client(app):
    """Return a test client to simulate requests to the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Return a test runner for invoking commands on the app."""
    return app.test_cli_runner()


def test_get_users_empty(client):
    """Test the GET /users route with an empty database."""
    response = client.get('/users')
    assert response.status_code == 200
    assert response.json == []


def test_create_user(client):
    """Test creating a new user via POST /users."""
    response = client.post('/users', json={
        'username': 'john_doe',
        'email': 'john@example.com'
    })
    assert response.status_code == 201
    data = response.json
    assert data['username'] == 'john_doe'
    assert data['email'] == 'john@example.com'

    # Test if the user exists in the database
    user = Transaction.query.filter_by(username='john_doe').first()
    assert user is not None
    assert user.email == 'john@example.com'


def test_get_user(client):
    """Test retrieving a user by ID via GET /users/<id>."""
    # First, create a new user
    response = client.post('/users', json={
        'username': 'john_doe',
        'email': 'john@example.com'
    })
    user_id = response.json['id']

    # Retrieve the user
    response = client.get(f'/users/{user_id}')
    assert response.status_code == 200
    assert response.json['username'] == 'john_doe'
    assert response.json['email'] == 'john@example.com'


def test_update_user(client):
    """Test updating an existing user via PUT /users/<id>."""
    # First, create a new user
    response = client.post('/users', json={
        'username': 'john_doe',
        'email': 'john@example.com'
    })
    user_id = response.json['id']

    # Update the user's email
    response = client.put(f'/users/{user_id}', json={
        'email': 'new_email@example.com'
    })
    assert response.status_code == 200
    assert response.json['email'] == 'new_email@example.com'

    # Verify that the email was updated in the database
    user = Transaction.query.get(user_id)
    assert user.email == 'new_email@example.com'


def test_delete_user(client):
    """Test deleting a user via DELETE /users/<id>."""
    # First, create a new user
    response = client.post('/users', json={
        'username': 'john_doe',
        'email': 'john@example.com'
    })
    user_id = response.json['id']

    # Delete the user
    response = client.delete(f'/users/{user_id}')
    assert response.status_code == 200
    assert response.json == {'message': 'User deleted'}

    # Verify that the user no longer exists in the database
    user = Transaction.query.get(user_id)
    assert user is None

