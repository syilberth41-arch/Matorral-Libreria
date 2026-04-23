"""Download service — secure e-book file delivery."""
import os
from flask import current_app, send_file, abort
from app.models.order import Order, OrderItem
from app.models.book import Book
from app.extensions import db


class DownloadService:
    """Serve digital books only to users who have purchased them."""

    @staticmethod
    def can_download(user_id: int, book_id: int) -> bool:
        """Check if user has a paid order containing this digital book."""
        book = db.session.get(Book, book_id)
        if not book or not book.is_digital:
            return False

        order_exists = (
            db.session.query(Order)
            .join(OrderItem)
            .filter(
                Order.user_id == user_id,
                Order.status == 'paid',
                OrderItem.book_id == book_id,
            )
            .first()
        )
        return order_exists is not None

    @staticmethod
    def get_file_path(book_id: int) -> str | None:
        """Return absolute path to the e-book file."""
        book = db.session.get(Book, book_id)
        if not book or not book.file_path:
            return None

        upload_folder = current_app.config['UPLOAD_FOLDER']
        full_path = os.path.join(upload_folder, book.file_path)
        if os.path.isfile(full_path):
            return full_path
        return None
