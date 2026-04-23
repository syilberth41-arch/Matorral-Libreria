"""Pytest fixtures for the bookstore test suite."""
import pytest
from app import create_app
from app.extensions import db as _db
from app.models.user import User
from app.models.book import Book, Genre, Author
from app.models.cart import CartItem
from app.models.order import Order, OrderItem


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    app = create_app('testing')
    yield app


@pytest.fixture(scope='function')
def db(app):
    """Fresh database for each test."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        _db.drop_all()


@pytest.fixture
def client(app, db):
    """Test client."""
    return app.test_client()


@pytest.fixture
def sample_genre(db):
    g = Genre(name='Ficción')
    db.session.add(g)
    db.session.commit()
    return g


@pytest.fixture
def sample_author(db):
    a = Author(name='Gabriel García Márquez')
    db.session.add(a)
    db.session.commit()
    return a


@pytest.fixture
def sample_book(db, sample_genre, sample_author):
    b = Book(
        title='Cien años de soledad',
        price=24.99,
        stock=10,
        format='both',
        genre_id=sample_genre.id,
        author_id=sample_author.id,
        description='Obra maestra del realismo mágico.',
        file_path='cien_anos.pdf',
    )
    db.session.add(b)
    db.session.commit()
    return b


@pytest.fixture
def sample_user(db):
    u = User(username='testuser', email='test@test.com')
    u.set_password('password123')
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture
def admin_user(db):
    u = User(username='admin', email='admin@test.com', is_admin=True)
    u.set_password('admin123')
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture
def logged_in_client(client, sample_user):
    """Client logged in as a regular user."""
    client.post('/auth/login', data={
        'email': 'test@test.com',
        'password': 'password123',
    }, follow_redirects=True)
    return client


@pytest.fixture
def admin_client(client, admin_user):
    """Client logged in as admin."""
    client.post('/auth/login', data={
        'email': 'admin@test.com',
        'password': 'admin123',
    }, follow_redirects=True)
    return client
