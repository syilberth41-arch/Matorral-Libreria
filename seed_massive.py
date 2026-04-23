"""Massive seed script for generating 10k books and 2k users."""
import random
import string
from werkzeug.security import generate_password_hash
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.book import Book, Genre, Author
from faker import Faker

fake = Faker('es_CO')

def seed_massive():
    app = create_app()
    with app.app_context():
        genres = Genre.query.all()
        if not genres:
            genre_names = ['Ficción', 'No ficción', 'Ciencia ficción', 'Fantasía', 'Misterio', 'Romance', 'Terror', 'Historia', 'Biografía', 'Ciencia']
            for name in genre_names:
                g = Genre(name=name)
                db.session.add(g)
            db.session.commit()
            genres = Genre.query.all()
            
        authors = Author.query.all()
        if not authors:
            for _ in range(50):
                a = Author(name=fake.name())
                db.session.add(a)
            db.session.commit()
            authors = Author.query.all()

        print("Generating 2,000 users...")
        users_to_add = []
        default_pwd = generate_password_hash('password123')
        for i in range(2000):
            email = f"user{random.randint(100000, 999999)}_{i}@example.com"
            username = f"user_{random.randint(100000, 999999)}_{i}"
            user = User(
                username=username,
                email=email,
                password_hash=default_pwd
            )
            users_to_add.append(user)
            if len(users_to_add) == 1000:
                db.session.bulk_save_objects(users_to_add)
                db.session.commit()
                users_to_add = []
        
        if users_to_add:
            db.session.bulk_save_objects(users_to_add)
            db.session.commit()
            
        print("Generated 2,000 users.")

        print("Generating 10,000 books...")
        books_to_add = []
        for i in range(10000):
            # Prices in COP: between 20k and 150k
            price_cop = random.randint(20, 150) * 1000
            
            title = fake.catch_phrase()
            isbn = ''.join(random.choices(string.digits, k=13))
            
            fmt_choices = ['physical', 'digital', 'both']
            fmt = random.choice(fmt_choices)
            
            book = Book(
                title=title,
                isbn=isbn,
                description=fake.text(max_nb_chars=200),
                price=price_cop,
                stock=random.randint(0, 100) if fmt != 'digital' else 0,
                format=fmt,
                cover_url=f"https://picsum.photos/seed/{random.randint(1, 100000)}/300/400",
                genre_id=random.choice(genres).id,
                author_id=random.choice(authors).id,
                file_path=f"sample_{i}.pdf" if fmt != 'physical' else None
            )
            books_to_add.append(book)
            
            if len(books_to_add) == 1000:
                db.session.bulk_save_objects(books_to_add)
                db.session.commit()
                books_to_add = []
                print(f"  ...inserted {(i+1)} books")

        if books_to_add:
            db.session.bulk_save_objects(books_to_add)
            db.session.commit()
            
        print("Generated 10,000 books.")
        print(f"Total Users in DB: {User.query.count()}")
        print(f"Total Books in DB: {Book.query.count()}")

if __name__ == '__main__':
    seed_massive()
