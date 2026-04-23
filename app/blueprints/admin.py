"""Admin blueprint — inventory CRUD and order management."""
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models.book import Book, Genre, Author
from app.models.order import Order

admin_bp = Blueprint('admin', __name__, template_folder='templates', url_prefix='/admin')


def admin_required(f):
    """Decorator: restrict access to admin users."""
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/')
@admin_required
def dashboard():
    total_books = Book.query.count()
    total_orders = Order.query.count()
    total_genres = Genre.query.count()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    return render_template('admin/dashboard.html',
                           total_books=total_books,
                           total_orders=total_orders,
                           total_genres=total_genres,
                           recent_orders=recent_orders)


# --- Book CRUD ---

@admin_bp.route('/books')
@admin_required
def book_list():
    page = request.args.get('page', 1, type=int)
    books = Book.query.order_by(Book.title).paginate(page=page, per_page=20)
    return render_template('admin/book_list.html', pagination=books)


@admin_bp.route('/books/new', methods=['GET', 'POST'])
@admin_required
def book_create():
    genres = Genre.query.order_by(Genre.name).all()
    authors = Author.query.order_by(Author.name).all()

    if request.method == 'POST':
        # Handle author — create if new
        author_name = request.form.get('author_name', '').strip()
        author_id = request.form.get('author_id', type=int)
        if author_name and not author_id:
            author = Author.query.filter_by(name=author_name).first()
            if not author:
                author = Author(name=author_name)
                db.session.add(author)
                db.session.flush()
            author_id = author.id

        book = Book(
            title=request.form['title'],
            isbn=request.form.get('isbn') or None,
            description=request.form.get('description', ''),
            price=float(request.form['price']),
            stock=int(request.form.get('stock', 0)),
            format=request.form.get('format', 'physical'),
            file_path=request.form.get('file_path') or None,
            genre_id=request.form.get('genre_id', type=int),
            author_id=author_id,
        )
        db.session.add(book)
        db.session.commit()
        flash('Libro creado.', 'success')
        return redirect(url_for('admin.book_list'))

    return render_template('admin/book_form.html', book=None,
                           genres=genres, authors=authors)


@admin_bp.route('/books/<int:book_id>/edit', methods=['GET', 'POST'])
@admin_required
def book_edit(book_id):
    book = Book.query.get_or_404(book_id)
    genres = Genre.query.order_by(Genre.name).all()
    authors = Author.query.order_by(Author.name).all()

    if request.method == 'POST':
        book.title = request.form['title']
        book.isbn = request.form.get('isbn') or None
        book.description = request.form.get('description', '')
        book.price = float(request.form['price'])
        book.stock = int(request.form.get('stock', 0))
        book.format = request.form.get('format', 'physical')
        book.file_path = request.form.get('file_path') or None
        book.genre_id = request.form.get('genre_id', type=int)

        author_name = request.form.get('author_name', '').strip()
        author_id = request.form.get('author_id', type=int)
        if author_name and not author_id:
            author = Author.query.filter_by(name=author_name).first()
            if not author:
                author = Author(name=author_name)
                db.session.add(author)
                db.session.flush()
            author_id = author.id
        book.author_id = author_id

        db.session.commit()
        flash('Libro actualizado.', 'success')
        return redirect(url_for('admin.book_list'))

    return render_template('admin/book_form.html', book=book,
                           genres=genres, authors=authors)


@admin_bp.route('/books/<int:book_id>/delete', methods=['POST'])
@admin_required
def book_delete(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('Libro eliminado.', 'success')
    return redirect(url_for('admin.book_list'))


# --- Genre CRUD ---

@admin_bp.route('/genres', methods=['GET', 'POST'])
@admin_required
def genre_list():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if name and not Genre.query.filter_by(name=name).first():
            db.session.add(Genre(name=name))
            db.session.commit()
            flash('Género creado.', 'success')
        else:
            flash('Género inválido o ya existe.', 'warning')
    genres = Genre.query.order_by(Genre.name).all()
    return render_template('admin/genre_list.html', genres=genres)


@admin_bp.route('/genres/<int:genre_id>/delete', methods=['POST'])
@admin_required
def genre_delete(genre_id):
    genre = Genre.query.get_or_404(genre_id)
    db.session.delete(genre)
    db.session.commit()
    flash('Género eliminado.', 'success')
    return redirect(url_for('admin.genre_list'))


# --- Order Management ---

@admin_bp.route('/orders')
@admin_required
def order_list():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status')
    q = Order.query
    if status:
        q = q.filter_by(status=status)
    orders = q.order_by(Order.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('admin/order_list.html', pagination=orders, current_status=status)


@admin_bp.route('/orders/<int:order_id>')
@admin_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_detail.html', order=order)


@admin_bp.route('/orders/<int:order_id>/status', methods=['POST'])
@admin_required
def order_update_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    if new_status in ('pending', 'paid', 'shipped', 'delivered', 'cancelled'):
        order.status = new_status
        db.session.commit()
        flash(f'Estado actualizado a {new_status}.', 'success')
    return redirect(url_for('admin.order_detail', order_id=order_id))
