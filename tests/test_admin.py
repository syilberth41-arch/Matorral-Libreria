"""Tests for admin blueprint."""


class TestAdminAccess:
    def test_admin_requires_login(self, client, db):
        resp = client.get('/admin/', follow_redirects=True)
        assert 'Iniciar Sesión' in resp.data.decode()

    def test_admin_denied_for_regular_user(self, logged_in_client):
        resp = logged_in_client.get('/admin/')
        assert resp.status_code == 403

    def test_admin_dashboard_loads(self, admin_client):
        resp = admin_client.get('/admin/')
        assert resp.status_code == 200
        assert 'Panel de Administración' in resp.data.decode()


class TestAdminBooks:
    def test_book_list(self, admin_client, sample_book):
        resp = admin_client.get('/admin/books')
        assert resp.status_code == 200
        assert 'Cien años de soledad' in resp.data.decode()

    def test_book_create_page(self, admin_client):
        resp = admin_client.get('/admin/books/new')
        assert resp.status_code == 200
        assert 'Nuevo Libro' in resp.data.decode()

    def test_book_create_submit(self, admin_client, sample_genre, app):
        from app.models.book import Book
        resp = admin_client.post('/admin/books/new', data={
            'title': 'Nuevo Libro Test',
            'price': '15.99',
            'stock': '5',
            'format': 'physical',
            'genre_id': sample_genre.id,
            'author_name': 'Nuevo Autor',
        }, follow_redirects=True)
        assert resp.status_code == 200
        with app.app_context():
            assert Book.query.filter_by(title='Nuevo Libro Test').first() is not None

    def test_book_edit(self, admin_client, sample_book):
        resp = admin_client.get(f'/admin/books/{sample_book.id}/edit')
        assert resp.status_code == 200
        assert 'Editar Libro' in resp.data.decode()

    def test_book_delete(self, admin_client, sample_book, app):
        from app.models.book import Book
        resp = admin_client.post(
            f'/admin/books/{sample_book.id}/delete', follow_redirects=True)
        assert resp.status_code == 200
        with app.app_context():
            assert Book.query.get(sample_book.id) is None


class TestAdminGenres:
    def test_genre_list(self, admin_client, sample_genre):
        resp = admin_client.get('/admin/genres')
        assert resp.status_code == 200
        assert 'Ficción' in resp.data.decode()

    def test_genre_create(self, admin_client, db):
        resp = admin_client.post('/admin/genres', data={
            'name': 'Ciencia Ficción',
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert 'creado' in resp.data.decode()


class TestAdminOrders:
    def test_order_list(self, admin_client):
        resp = admin_client.get('/admin/orders')
        assert resp.status_code == 200
        assert 'Gestión de Pedidos' in resp.data.decode()
