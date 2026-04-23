"""Cart model with unique constraint to prevent duplicates."""
from app.extensions import db


class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)

    book = db.relationship('Book', backref='cart_items')

    # Prevent duplicate book entries in the same user's cart
    __table_args__ = (
        db.UniqueConstraint('user_id', 'book_id', name='uq_user_book_cart'),
    )

    @property
    def subtotal(self):
        return self.book.price * self.quantity

    def __repr__(self):
        return f'<CartItem user={self.user_id} book={self.book_id} qty={self.quantity}>'
