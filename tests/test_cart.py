"""Tests for cart blueprint."""
from app.models.cart import CartItem
from app.models.order import Order
from app.extensions import db as _db


class TestCartView:
    def test_cart_requires_login(self, client, db):
        resp = client.get('/cart', follow_redirects=True)
        assert 'Iniciar Sesión' in resp.data.decode()

    def test_empty_cart(self, logged_in_client):
        resp = logged_in_client.get('/cart')
        assert resp.status_code == 200
        assert 'vacío' in resp.data.decode()


class TestAddToCart:
    def test_add_book_to_cart(self, logged_in_client, sample_book):
        resp = logged_in_client.post(
            f'/cart/add/{sample_book.id}', follow_redirects=True)
        assert resp.status_code == 200
        assert 'agregado' in resp.data.decode()

    def test_add_duplicate_increments_quantity(self, logged_in_client, sample_book, app):
        logged_in_client.post(f'/cart/add/{sample_book.id}', follow_redirects=True)
        logged_in_client.post(f'/cart/add/{sample_book.id}', follow_redirects=True)
        with app.app_context():
            items = CartItem.query.filter_by(book_id=sample_book.id).all()
            assert len(items) == 1
            assert items[0].quantity == 2

    def test_add_nonexistent_book(self, logged_in_client):
        resp = logged_in_client.post('/cart/add/9999', follow_redirects=True)
        assert 'no encontrado' in resp.data.decode()


class TestUpdateCart:
    def test_update_quantity(self, logged_in_client, sample_book, app):
        logged_in_client.post(f'/cart/add/{sample_book.id}', follow_redirects=True)
        with app.app_context():
            item = CartItem.query.first()
            resp = logged_in_client.post(
                f'/cart/update/{item.id}',
                data={'quantity': 5},
                follow_redirects=True)
            assert resp.status_code == 200
            updated = _db.session.get(CartItem, item.id)
            assert updated.quantity == 5


class TestRemoveFromCart:
    def test_remove_item(self, logged_in_client, sample_book, app):
        logged_in_client.post(f'/cart/add/{sample_book.id}', follow_redirects=True)
        with app.app_context():
            item = CartItem.query.first()
            resp = logged_in_client.post(
                f'/cart/remove/{item.id}', follow_redirects=True)
            assert resp.status_code == 200
            assert 'eliminado' in resp.data.decode()
            assert CartItem.query.count() == 0


class TestCheckout:
    def test_checkout_empty_cart(self, logged_in_client):
        resp = logged_in_client.get('/checkout', follow_redirects=True)
        assert 'vacío' in resp.data.decode()

    def test_checkout_page_loads(self, logged_in_client, sample_book):
        logged_in_client.post(f'/cart/add/{sample_book.id}', follow_redirects=True)
        resp = logged_in_client.get('/checkout')
        assert resp.status_code == 200
        assert 'Realizar Pago' in resp.data.decode()

    def test_checkout_success(self, logged_in_client, sample_book, app):
        logged_in_client.post(f'/cart/add/{sample_book.id}', follow_redirects=True)
        resp = logged_in_client.post('/checkout', data={
            'card_number': '4111111111111111',
            'shipping_address': 'Calle Falsa 123, Bogotá',
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert 'Compra Exitosa' in resp.data.decode()
        with app.app_context():
            assert Order.query.count() == 1
            assert CartItem.query.count() == 0

    def test_checkout_invalid_card(self, logged_in_client, sample_book):
        logged_in_client.post(f'/cart/add/{sample_book.id}', follow_redirects=True)
        resp = logged_in_client.post('/checkout', data={
            'card_number': '123',
            'shipping_address': 'Calle Falsa 123',
        }, follow_redirects=True)
        assert 'inválido' in resp.data.decode()
