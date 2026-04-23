"""Tests for SearchService and PaymentService."""
from app.services.search_service import SearchService
from app.services.payment_service import PaymentService
from app.models.book import Book, Genre, Author
from app.extensions import db as _db


class TestSearchService:
    def test_get_genres(self, app, db, sample_genre):
        with app.app_context():
            genres = SearchService.get_genres()
            assert len(genres) >= 1
            assert genres[0].name == 'Ficción'

    def test_search_all_books(self, app, db, sample_book):
        with app.app_context():
            result = SearchService.search_books()
            assert result.total >= 1

    def test_search_by_title(self, app, db, sample_book):
        with app.app_context():
            result = SearchService.search_books(query='soledad')
            assert result.total == 1
            assert result.items[0].title == 'Cien años de soledad'

    def test_search_by_genre(self, app, db, sample_book, sample_genre):
        with app.app_context():
            result = SearchService.search_books(genre_id=sample_genre.id)
            assert result.total >= 1

    def test_search_by_author_name(self, app, db, sample_book):
        with app.app_context():
            result = SearchService.search_books(author_name='García')
            assert result.total >= 1

    def test_search_by_price_range(self, app, db, sample_book):
        with app.app_context():
            result = SearchService.search_books(price_min=20, price_max=30)
            assert result.total >= 1

    def test_search_empty_result(self, app, db, sample_book):
        with app.app_context():
            result = SearchService.search_books(query='xyz_nonexistent')
            assert result.total == 0

    def test_get_featured_books(self, app, db, sample_book):
        with app.app_context():
            featured = SearchService.get_featured_books(limit=5)
            assert len(featured) >= 1

    def test_get_book_by_id(self, app, db, sample_book):
        with app.app_context():
            book = SearchService.get_book_by_id(sample_book.id)
            assert book is not None
            assert book.title == 'Cien años de soledad'

    def test_get_book_by_id_not_found(self, app, db):
        with app.app_context():
            book = SearchService.get_book_by_id(9999)
            assert book is None


class TestPaymentService:
    def test_create_token(self):
        token = PaymentService.create_payment_token('1234', 50.00)
        assert token.startswith('tok_')
        assert len(token) > 10

    def test_process_payment_success(self):
        token = PaymentService.create_payment_token('5678', 25.00)
        result = PaymentService.process_payment(token, 25.00)
        assert result['success'] is True
        assert result['amount'] == 25.00

    def test_validate_card_valid(self):
        result = PaymentService.validate_card_input('4111111111111111')
        assert result['valid'] is True
        assert result['last_four'] == '1111'

    def test_validate_card_invalid_short(self):
        result = PaymentService.validate_card_input('123')
        assert result['valid'] is False

    def test_validate_card_invalid_letters(self):
        result = PaymentService.validate_card_input('abcdefghijklmnop')
        assert result['valid'] is False

    def test_validate_card_with_spaces(self):
        result = PaymentService.validate_card_input('4111 1111 1111 1111')
        assert result['valid'] is True
