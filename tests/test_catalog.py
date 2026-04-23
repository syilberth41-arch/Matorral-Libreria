"""Tests for catalog blueprint."""
from app.models.book import Book, Genre, Author
from app.extensions import db as _db


class TestCatalogIndex:
    def test_homepage_loads(self, client, db):
        resp = client.get('/')
        assert resp.status_code == 200
        assert 'BookStore' in resp.data.decode()

    def test_homepage_shows_featured(self, client, db, sample_book):
        resp = client.get('/')
        assert 'Cien años de soledad' in resp.data.decode()

    def test_homepage_shows_genres(self, client, db, sample_genre):
        resp = client.get('/')
        assert 'Ficción' in resp.data.decode()


class TestBookList:
    def test_catalog_loads(self, client, db):
        resp = client.get('/books')
        assert resp.status_code == 200
        assert 'Catálogo' in resp.data.decode()

    def test_catalog_shows_books(self, client, db, sample_book):
        resp = client.get('/books')
        assert 'Cien años de soledad' in resp.data.decode()

    def test_search_by_title(self, client, db, sample_book):
        resp = client.get('/books?q=soledad')
        assert 'Cien años de soledad' in resp.data.decode()

    def test_search_no_results(self, client, db, sample_book):
        resp = client.get('/books?q=xyznonexistent')
        assert 'No se encontraron' in resp.data.decode()

    def test_filter_by_genre(self, client, db, sample_book, sample_genre):
        resp = client.get(f'/books?genre={sample_genre.id}')
        assert 'Cien años de soledad' in resp.data.decode()

    def test_filter_by_author(self, client, db, sample_book):
        resp = client.get('/books?author=García')
        assert 'Cien años de soledad' in resp.data.decode()

    def test_filter_by_price_range(self, client, db, sample_book):
        resp = client.get('/books?price_min=20&price_max=30')
        assert 'Cien años de soledad' in resp.data.decode()

    def test_filter_by_price_excludes(self, client, db, sample_book):
        resp = client.get('/books?price_min=30&price_max=50')
        assert 'Cien años de soledad' not in resp.data.decode()


class TestBookDetail:
    def test_detail_page(self, client, db, sample_book):
        resp = client.get(f'/books/{sample_book.id}')
        assert resp.status_code == 200
        assert 'Cien años de soledad' in resp.data.decode()
        assert '24.99' in resp.data.decode()

    def test_detail_not_found(self, client, db):
        resp = client.get('/books/9999')
        assert resp.status_code == 404


class TestMultipleBooks:
    def test_pagination(self, client, db, sample_genre, sample_author, app):
        """Create 25 books and verify pagination."""
        with app.app_context():
            for i in range(25):
                b = Book(title=f'Book {i}', price=10+i, stock=5, format='physical',
                         genre_id=sample_genre.id, author_id=sample_author.id)
                _db.session.add(b)
            _db.session.commit()

            resp = client.get('/books?page=1')
            assert resp.status_code == 200

            resp2 = client.get('/books?page=2')
            assert resp2.status_code == 200
