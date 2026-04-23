"""Search service with caching for catalog queries."""
from sqlalchemy.orm import joinedload
from app.extensions import db, cache
from app.models.book import Book, Genre, Author


class SearchService:
    """Optimized search with caching and pagination."""

    @staticmethod
    @cache.memoize(timeout=60)
    def get_genres():
        """Cached list of all genres."""
        return Genre.query.order_by(Genre.name).all()

    @staticmethod
    def search_books(query=None, genre_id=None, author_name=None,
                     price_min=None, price_max=None, page=1, per_page=20):
        """Build and execute an optimized catalog query with filters."""
        q = Book.query.options(joinedload(Book.author), joinedload(Book.genre))

        if query:
            q = q.filter(Book.title.ilike(f'%{query}%'))

        if genre_id:
            q = q.filter(Book.genre_id == int(genre_id))

        if author_name:
            q = q.join(Author).filter(Author.name.ilike(f'%{author_name}%'))

        if price_min is not None:
            q = q.filter(Book.price >= float(price_min))

        if price_max is not None:
            q = q.filter(Book.price <= float(price_max))

        q = q.order_by(Book.title)
        return q.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_book_by_id(book_id):
        return db.session.get(Book, book_id)

    @staticmethod
    @cache.memoize(timeout=60)
    def get_featured_books(limit=8):
        """Return newest books for homepage."""
        return Book.query.options(joinedload(Book.author), joinedload(Book.genre)).order_by(Book.created_at.desc()).limit(limit).all()
