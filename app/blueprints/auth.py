"""Auth blueprint — registration, login, logout, 2FA (TOTP)."""
import io
import base64
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
import qrcode
from app.extensions import db
from app.models.user import User

auth_bp = Blueprint('auth', __name__, template_folder='templates')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('catalog.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        errors = []
        if not username or len(username) < 3:
            errors.append('El nombre de usuario debe tener al menos 3 caracteres.')
        if not email or '@' not in email:
            errors.append('Email inválido.')
        if len(password) < 8:
            errors.append('La contraseña debe tener al menos 8 caracteres.')
        if password != confirm:
            errors.append('Las contraseñas no coinciden.')
        if User.query.filter_by(username=username).first():
            errors.append('Ese nombre de usuario ya está registrado.')
        if User.query.filter_by(email=email).first():
            errors.append('Ese email ya está registrado.')

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('auth/register.html')

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registro exitoso. Inicia sesión.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('catalog.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash('Credenciales inválidas.', 'danger')
            return render_template('auth/login.html')

        # If MFA is enabled, redirect to TOTP verification
        if user.mfa_enabled:
            session['mfa_user_id'] = user.id
            return redirect(url_for('auth.verify_2fa'))

        login_user(user)
        flash(f'Bienvenido, {user.username}!', 'success')
        next_page = request.args.get('next')
        return redirect(next_page or url_for('catalog.index'))

    return render_template('auth/login.html')


@auth_bp.route('/verify-2fa', methods=['GET', 'POST'])
def verify_2fa():
    user_id = session.get('mfa_user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        token = request.form.get('token', '').strip()
        user = db.session.get(User, user_id)

        if user and user.verify_totp(token):
            session.pop('mfa_user_id', None)
            login_user(user)
            flash(f'Bienvenido, {user.username}!', 'success')
            return redirect(url_for('catalog.index'))
        else:
            flash('Código 2FA inválido.', 'danger')

    return render_template('auth/verify_2fa.html')


@auth_bp.route('/setup-2fa', methods=['GET', 'POST'])
@login_required
def setup_2fa():
    if request.method == 'POST':
        token = request.form.get('token', '').strip()
        if current_user.verify_totp(token):
            current_user.mfa_enabled = True
            db.session.commit()
            flash('Autenticación de doble factor activada.', 'success')
            return redirect(url_for('auth.profile'))
        else:
            flash('Código inválido. Intenta de nuevo.', 'danger')

    if not current_user.totp_secret:
        current_user.generate_totp_secret()
        db.session.commit()

    totp_uri = current_user.get_totp_uri()

    # Generate QR code as base64 PNG
    img = qrcode.make(totp_uri)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    qr_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    return render_template('auth/setup_2fa.html', totp_uri=totp_uri,
                           secret=current_user.totp_secret, qr_code=qr_b64)


@auth_bp.route('/profile')
@login_required
def profile():
    from app.models.order import Order
    orders = current_user.orders.order_by(Order.created_at.desc()).all()
    return render_template('auth/profile.html', orders=orders)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada.', 'info')
    return redirect(url_for('auth.login'))
