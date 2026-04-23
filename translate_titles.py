"""Script to translate/regenerate book titles into proper Spanish."""
from app import create_app
from app.extensions import db
from app.models.book import Book
from faker import Faker
import json

fake = Faker('es_CO')

def reformat_titles():
    app = create_app()
    with app.app_context():
        # Get all books
        books = Book.query.all()
        
        # Spanish sounding book title generation
        # We can use a mix of adjectives, nouns to make it feel like real book titles.
        words = ['El eco de', 'Sombras en', 'La luz de', 'Memorias de', 'Viaje a', 'Cuentos de', 'El secreto de', 'Historia de', 'El misterio de', 'El último']
        
        count = 0
        for book in books:
            # The first 20 books were the hardcoded proper Spanish ones in seed_data.py
            if book.id > 20:
                new_title = f"{fake.random_element(words)} {fake.word().capitalize()}"
                book.title = new_title
                count += 1
                
        db.session.commit()
        print(f"Updated {count} book titles to Spanish style.")

if __name__ == '__main__':
    reformat_titles()
