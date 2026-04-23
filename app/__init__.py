"""Flask application factory."""
import os
from flask import Flask, render_template
from app.config import config_by_name
from app.extensions import db, login_manager, cache, csrf, migrate


def create_app(config_name=None):
    """Create and configure the Flask application."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    cache.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    # Create upload folder
    os.makedirs(app.config.get('UPLOAD_FOLDER', 'ebooks'), exist_ok=True)

    # Register blueprints
    from app.blueprints.auth import auth_bp
    from app.blueprints.catalog import catalog_bp
    from app.blueprints.cart import cart_bp
    from app.blueprints.download import download_bp
    from app.blueprints.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(catalog_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(download_bp)
    app.register_blueprint(admin_bp)

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    # Create tables in dev/test
    with app.app_context():
        from app.models import User, Book, Genre, Author, CartItem, Order, OrderItem
        db.create_all()

    return app
