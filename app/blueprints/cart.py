"""Cart blueprint — add, update, remove items and checkout (≤3 steps)."""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.cart import CartItem
from app.models.book import Book
from app.models.order import Order, OrderItem
from app.services.payment_service import PaymentService

cart_bp = Blueprint('cart', __name__, template_folder='templates')


@cart_bp.route('/cart')
@login_required
def view_cart():
    """Step 1: Review cart."""
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.subtotal for item in items)
    return render_template('cart/view.html', items=items, total=total)


@cart_bp.route('/cart/add/<int:book_id>', methods=['POST'])
@login_required
def add_to_cart(book_id):
    """Add book to cart — if already in cart, increment quantity."""
    book = db.session.get(Book, book_id)
    if not book:
        flash('Libro no encontrado.', 'danger')
        return redirect(url_for('catalog.book_list'))

    if not book.in_stock:
        flash('Libro sin stock disponible.', 'warning')
        return redirect(url_for('catalog.book_detail', book_id=book_id))

    existing = CartItem.query.filter_by(
        user_id=current_user.id, book_id=book_id
    ).first()

    if existing:
        existing.quantity += 1
        flash('Cantidad actualizada en el carrito.', 'info')
    else:
        item = CartItem(user_id=current_user.id, book_id=book_id, quantity=1)
        db.session.add(item)
        flash('Libro agregado al carrito.', 'success')

    db.session.commit()
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_quantity(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        flash('Acción no permitida.', 'danger')
        return redirect(url_for('cart.view_cart'))

    qty = request.form.get('quantity', 1, type=int)
    if qty < 1:
        db.session.delete(item)
    else:
        item.quantity = qty
    db.session.commit()
    flash('Carrito actualizado.', 'info')
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        flash('Acción no permitida.', 'danger')
        return redirect(url_for('cart.view_cart'))

    db.session.delete(item)
    db.session.commit()
    flash('Libro eliminado del carrito.', 'success')
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Step 2: Shipping + payment info → Step 3: Confirmation."""
    items = CartItem.query.filter_by(user_id=current_user.id).all()

    if not items:
        flash('Tu carrito está vacío.', 'warning')
        return redirect(url_for('catalog.book_list'))

    total = sum(item.subtotal for item in items)

    if request.method == 'POST':
        # Step 3: Process payment
        card_number = request.form.get('card_number', '')
        shipping_address = request.form.get('shipping_address', '').strip()

        validation = PaymentService.validate_card_input(card_number)
        if not validation['valid']:
            flash(validation['error'], 'danger')
            return render_template('cart/checkout.html', items=items, total=total)

        token = PaymentService.create_payment_token(validation['last_four'], total)
        result = PaymentService.process_payment(token, total)

        if not result['success']:
            flash('Error al procesar el pago.', 'danger')
            return render_template('cart/checkout.html', items=items, total=total)

        # Create order
        order = Order(
            user_id=current_user.id,
            status='paid',
            total=total,
            payment_token=token,
            shipping_address=shipping_address,
        )
        db.session.add(order)
        db.session.flush()

        for cart_item in items:
            order_item = OrderItem(
                order_id=order.id,
                book_id=cart_item.book_id,
                quantity=cart_item.quantity,
                unit_price=cart_item.book.price,
            )
            db.session.add(order_item)

            # Decrease stock for physical books
            if cart_item.book.is_physical:
                cart_item.book.stock = max(0, cart_item.book.stock - cart_item.quantity)

            db.session.delete(cart_item)

        db.session.commit()
        flash('¡Compra realizada con éxito!', 'success')
        return render_template('cart/confirmation.html', order=order)

    # Step 2: Show checkout form
    return render_template('cart/checkout.html', items=items, total=total)
