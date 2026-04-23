"""Catalog blueprint — book listing, search, and detail views."""
from flask import Blueprint, render_template, request
from app.services.search_service import SearchService
from flask import current_app

catalog_bp = Blueprint('catalog', __name__, template_folder='templates')


@catalog_bp.route('/')
def index():
    """Homepage with featured books and genre navigation."""
    featured = SearchService.get_featured_books(limit=8)
    genres = SearchService.get_genres()
    return render_template('catalog/index.html', featured=featured, genres=genres)


@catalog_bp.route('/books')
def book_list():
    """Paginated catalog with advanced search filters."""
    query = request.args.get('q', '').strip()
    genre_id = request.args.get('genre', type=int)
    author_name = request.args.get('author', '').strip()
    price_min = request.args.get('price_min', type=float)
    price_max = request.args.get('price_max', type=float)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 20)

    pagination = SearchService.search_books(
        query=query or None,
        genre_id=genre_id,
        author_name=author_name or None,
        price_min=price_min,
        price_max=price_max,
        page=page,
        per_page=per_page,
    )

    genres = SearchService.get_genres()

    return render_template(
        'catalog/book_list.html',
        books=pagination.items,
        pagination=pagination,
        genres=genres,
        filters={
            'q': query, 'genre': genre_id, 'author': author_name,
            'price_min': price_min, 'price_max': price_max,
        },
    )


@catalog_bp.route('/books/<int:book_id>')
def book_detail(book_id):
    """Individual book detail page."""
    book = SearchService.get_book_by_id(book_id)
    if not book:
        return render_template('errors/404.html'), 404
    return render_template('catalog/book_detail.html', book=book)
