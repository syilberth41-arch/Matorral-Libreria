"""Seed script — populate database with sample data for development."""
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.book import Book, Genre, Author

GENRES = [
    'Ficción', 'No ficción', 'Ciencia ficción', 'Fantasía', 'Misterio',
    'Romance', 'Terror', 'Historia', 'Biografía', 'Ciencia',
    'Tecnología', 'Negocios', 'Autoayuda', 'Poesía', 'Infantil',
]

AUTHORS = [
    'Gabriel García Márquez', 'Isabel Allende', 'Jorge Luis Borges',
    'Mario Vargas Llosa', 'Julio Cortázar', 'Pablo Neruda',
    'Carlos Ruiz Zafón', 'Laura Esquivel', 'Octavio Paz',
    'Roberto Bolaño', 'Elena Poniatowska', 'Horacio Quiroga',
    'Ernesto Sabato', 'Juan Rulfo', 'Miguel de Cervantes',
]

SAMPLE_BOOKS = [
    ('Cien años de soledad', 'Gabriel García Márquez', 'Ficción', 24.99, 'both', 50),
    ('La casa de los espíritus', 'Isabel Allende', 'Ficción', 19.99, 'physical', 30),
    ('Ficciones', 'Jorge Luis Borges', 'Ficción', 15.99, 'digital', 0),
    ('La ciudad y los perros', 'Mario Vargas Llosa', 'Ficción', 18.50, 'physical', 25),
    ('Rayuela', 'Julio Cortázar', 'Ficción', 22.00, 'both', 40),
    ('Veinte poemas de amor', 'Pablo Neruda', 'Poesía', 12.99, 'digital', 0),
    ('La sombra del viento', 'Carlos Ruiz Zafón', 'Misterio', 21.50, 'physical', 35),
    ('Como agua para chocolate', 'Laura Esquivel', 'Romance', 16.99, 'both', 20),
    ('El laberinto de la soledad', 'Octavio Paz', 'No ficción', 14.99, 'digital', 0),
    ('2666', 'Roberto Bolaño', 'Ficción', 28.00, 'physical', 15),
    ('La noche de Tlatelolco', 'Elena Poniatowska', 'Historia', 13.50, 'digital', 0),
    ('Cuentos de amor de locura y de muerte', 'Horacio Quiroga', 'Terror', 11.99, 'both', 45),
    ('El túnel', 'Ernesto Sabato', 'Misterio', 10.99, 'physical', 60),
    ('Pedro Páramo', 'Juan Rulfo', 'Fantasía', 9.99, 'both', 55),
    ('Don Quijote de la Mancha', 'Miguel de Cervantes', 'Ficción', 35.00, 'physical', 20),
    ('El amor en los tiempos del cólera', 'Gabriel García Márquez', 'Romance', 20.99, 'both', 30),
    ('La fiesta del chivo', 'Mario Vargas Llosa', 'Historia', 23.50, 'physical', 18),
    ('Bestiario', 'Julio Cortázar', 'Fantasía', 14.50, 'digital', 0),
    ('Los detectives salvajes', 'Roberto Bolaño', 'Ficción', 26.00, 'physical', 12),
    ('Crónica de una muerte anunciada', 'Gabriel García Márquez', 'Misterio', 13.99, 'both', 40),
]


def seed():
    app = create_app()
    with app.app_context():
        # Genres
        genre_map = {}
        for name in GENRES:
            g = Genre.query.filter_by(name=name).first()
            if not g:
                g = Genre(name=name)
                db.session.add(g)
                db.session.flush()
            genre_map[name] = g

        # Authors
        author_map = {}
        for name in AUTHORS:
            a = Author.query.filter_by(name=name).first()
            if not a:
                a = Author(name=name)
                db.session.add(a)
                db.session.flush()
            author_map[name] = a

        # Books
        for title, author_name, genre_name, price, fmt, stock in SAMPLE_BOOKS:
            if not Book.query.filter_by(title=title).first():
                book = Book(
                    title=title,
                    price=price,
                    stock=stock,
                    format=fmt,
                    genre_id=genre_map[genre_name].id,
                    author_id=author_map[author_name].id,
                    description=f'Una obra maestra de {author_name}.',
                    file_path=f'{title.lower().replace(" ", "_")}.pdf' if fmt != 'physical' else None,
                )
                db.session.add(book)

        # Admin user
        if not User.query.filter_by(email='admin@bookstore.com').first():
            admin = User(username='admin', email='admin@bookstore.com', is_admin=True)
            admin.set_password('admin1234')
            db.session.add(admin)

        # Regular user
        if not User.query.filter_by(email='user@test.com').first():
            user = User(username='testuser', email='user@test.com')
            user.set_password('test1234')
            db.session.add(user)

        db.session.commit()
        print('🟢 Seed data loaded successfully!')
        print(f'   📚 {Book.query.count()} books')
        print(f'   🏷️  {Genre.query.count()} genres')
        print(f'   ✍️  {Author.query.count()} authors')
        print(f'   👤 {User.query.count()} users')
        print(f'   Admin: admin@bookstore.com / admin1234')


if __name__ == '__main__':
    seed()
