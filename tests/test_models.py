"""Tests for database models."""
import pytest
from app.models.user import User
from app.models.book import Book, Genre, Author
from app.models.cart import CartItem
from app.models.order import Order, OrderItem
from app.extensions import db as _db


class TestUserModel:
    """User model tests."""

    def test_create_user(self, db, sample_user):
        assert sample_user.id is not None
        assert sample_user.username == 'testuser'
        assert sample_user.email == 'test@test.com'
        assert sample_user.is_admin is False

    def test_password_hashing(self, db, sample_user):
        assert sample_user.password_hash != 'password123'
        assert sample_user.check_password('password123') is True
        assert sample_user.check_password('wrong') is False

    def test_totp_secret_generation(self, db, sample_user):
        secret = sample_user.generate_totp_secret()
        assert secret is not None
        assert len(secret) == 32
        assert sample_user.totp_secret == secret

    def test_totp_uri(self, db, sample_user):
        sample_user.generate_totp_secret()
        uri = sample_user.get_totp_uri()
        assert 'otpauth://totp/' in uri
        assert 'BookStore' in uri

    def test_unique_email(self, db, sample_user):
        u2 = User(username='other', email='test@test.com')
        u2.set_password('pass1234')
        _db.session.add(u2)
        with pytest.raises(Exception):
            _db.session.commit()
        _db.session.rollback()

    def test_unique_username(self, db, sample_user):
        u2 = User(username='testuser', email='other@test.com')
        u2.set_password('pass1234')
        _db.session.add(u2)
        with pytest.raises(Exception):
            _db.session.commit()
        _db.session.rollback()


class TestBookModel:
    """Book model tests."""

    def test_create_book(self, db, sample_book):
        assert sample_book.id is not None
        assert sample_book.title == 'Cien años de soledad'
        assert sample_book.price == 24.99

    def test_is_digital(self, db, sample_book):
        assert sample_book.is_digital is True
        sample_book.format = 'physical'
        assert sample_book.is_digital is False

    def test_is_physical(self, db, sample_book):
        assert sample_book.is_physical is True
        sample_book.format = 'digital'
        assert sample_book.is_physical is False

    def test_in_stock_digital(self, db, sample_genre, sample_author):
        b = Book(title='Digital Book', price=10, stock=0, format='digital',
                 genre_id=sample_genre.id, author_id=sample_author.id)
        _db.session.add(b)
        _db.session.commit()
        assert b.in_stock is True

    def test_in_stock_physical_zero(self, db, sample_genre, sample_author):
        b = Book(title='Empty Book', price=10, stock=0, format='physical',
                 genre_id=sample_genre.id, author_id=sample_author.id)
        _db.session.add(b)
        _db.session.commit()
        assert b.in_stock is False

    def test_genre_relationship(self, db, sample_book, sample_genre):
        assert sample_book.genre.name == 'Ficción'

    def test_author_relationship(self, db, sample_book, sample_author):
        assert sample_book.author.name == 'Gabriel García Márquez'


class TestCartItemModel:
    """CartItem model tests."""

    def test_add_to_cart(self, db, sample_user, sample_book):
        item = CartItem(user_id=sample_user.id, book_id=sample_book.id, quantity=2)
        _db.session.add(item)
        _db.session.commit()
        assert item.id is not None
        assert item.quantity == 2

    def test_subtotal(self, db, sample_user, sample_book):
        item = CartItem(user_id=sample_user.id, book_id=sample_book.id, quantity=3)
        _db.session.add(item)
        _db.session.commit()
        assert item.subtotal == pytest.approx(24.99 * 3)

    def test_unique_constraint_prevents_duplicates(self, db, sample_user, sample_book):
        item1 = CartItem(user_id=sample_user.id, book_id=sample_book.id, quantity=1)
        _db.session.add(item1)
        _db.session.commit()

        item2 = CartItem(user_id=sample_user.id, book_id=sample_book.id, quantity=1)
        _db.session.add(item2)
        with pytest.raises(Exception):
            _db.session.commit()
        _db.session.rollback()


class TestOrderModel:
    """Order model tests."""

    def test_create_order(self, db, sample_user, sample_book):
        order = Order(user_id=sample_user.id, status='paid', total=24.99,
                      payment_token='tok_test123')
        _db.session.add(order)
        _db.session.flush()

        oi = OrderItem(order_id=order.id, book_id=sample_book.id,
                       quantity=1, unit_price=24.99)
        _db.session.add(oi)
        _db.session.commit()

        assert order.id is not None
        assert len(order.items) == 1
        assert order.items[0].subtotal == 24.99

    def test_calculate_total(self, db, sample_user, sample_book):
        order = Order(user_id=sample_user.id, total=0)
        _db.session.add(order)
        _db.session.flush()

        oi = OrderItem(order_id=order.id, book_id=sample_book.id,
                       quantity=2, unit_price=24.99)
        _db.session.add(oi)
        _db.session.commit()

        total = order.calculate_total()
        assert total == pytest.approx(49.98)
