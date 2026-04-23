"""Book, Genre, and Author models."""
from datetime import datetime
from zoneinfo import ZoneInfo
from app.extensions import db


class Genre(db.Model):
    __tablename__ = 'genres'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    books = db.relationship('Book', backref='genre', lazy='dynamic')

    def __repr__(self):
        return f'<Genre {self.name}>'


class Author(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    books = db.relationship('Book', backref='author', lazy='dynamic')

    def __repr__(self):
        return f'<Author {self.name}>'


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False, index=True)
    isbn = db.Column(db.String(13), unique=True, nullable=True)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    format = db.Column(db.String(20), nullable=False, default='physical')  # physical, digital, both
    file_path = db.Column(db.String(500), nullable=True)  # path for digital books
    cover_url = db.Column(db.String(500), nullable=True)
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'), nullable=True, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(ZoneInfo('America/Bogota')))

    __table_args__ = (
        db.Index('ix_books_price', 'price'),
        db.Index('ix_books_format', 'format'),
    )

    @property
    def is_digital(self):
        return self.format in ('digital', 'both')

    @property
    def is_physical(self):
        return self.format in ('physical', 'both')

    @property
    def in_stock(self):
        if self.format == 'digital':
            return True
        return self.stock > 0

    def __repr__(self):
        return f'<Book {self.title}>'
