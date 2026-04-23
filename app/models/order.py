"""Order and OrderItem models."""
from datetime import datetime
from zoneinfo import ZoneInfo
from app.extensions import db


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, paid, shipped, delivered, cancelled
    total = db.Column(db.Float, nullable=False, default=0.0)
    payment_token = db.Column(db.String(200), nullable=True)  # tokenized, PCI-compliant
    shipping_address = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(ZoneInfo('America/Bogota')))

    items = db.relationship('OrderItem', backref='order', lazy='select',
                            cascade='all, delete-orphan')

    def calculate_total(self):
        self.total = sum(item.subtotal for item in self.items)
        return self.total

    def __repr__(self):
        return f'<Order {self.id} status={self.status}>'

    @property
    def status_es(self):
        translations = {
            'pending': 'Pendiente',
            'paid': 'Pagado',
            'shipped': 'Enviado',
            'delivered': 'Entregado',
            'cancelled': 'Cancelado'
        }
        return translations.get(self.status, self.status)


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)

    book = db.relationship('Book')

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    def __repr__(self):
        return f'<OrderItem order={self.order_id} book={self.book_id}>'
