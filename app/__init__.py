import os
import logging
from flask import Flask, render_template
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_wtf.csrf import CSRFError

from app.extensions import db, csrf
from app.metrics import init_metrics
from app.routes import register_blueprints

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )

    # Base configuration
    secret_key = os.getenv('SECRET_KEY', 'dev-insecure-secret-key-replace-in-env')
    db_uri = os.getenv('DATABASE_URL')
    
    if not db_uri:
        # Construct from components if DATABASE_URL not set directly
        pg_user = os.getenv('POSTGRES_USER', 'library_user')
        pg_pass = os.getenv('POSTGRES_PASSWORD', 'LibrarySecret2025!')
        pg_host = os.getenv('POSTGRES_HOST', 'localhost')
        pg_port = os.getenv('POSTGRES_PORT', '5432')
        pg_db = os.getenv('POSTGRES_DB', 'library_db')
        db_uri = f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"

    app.config.from_mapping(
        SECRET_KEY=secret_key,
        SQLALCHEMY_DATABASE_URI=db_uri,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        WTF_CSRF_ENABLED=True,
        WTF_CSRF_TIME_LIMIT=3600
    )

    if test_config:
        app.config.update(test_config)

    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)

    # Configure Reverse Proxy headers trust (Nginx)
    # x_for=1, x_proto=1, x_host=1 trusts 1 proxy layer (our Nginx container)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    # Register Metrics
    init_metrics(app)

    # Exempt health and metrics from CSRF
    csrf.exempt(app.view_functions.get('metrics_endpoint', lambda: None))

    # Register blueprints
    register_blueprints(app)

    # Exempt /health and /metrics specifically
    with app.app_context():
        if 'main.health_check' in app.view_functions:
            csrf.exempt(app.view_functions['main.health_check'])

    # Error Handlers without leaking stack traces
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        app.logger.error(f"Internal server error: {str(e)}")
        return render_template('errors/500.html'), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        app.logger.warning(f"CSRF token validation failed: {str(e.description)}")
        return render_template('errors/400.html', error_message="Phiên làm việc hoặc mã xác thực bảo mật (CSRF) không hợp lệ. Vui lòng tải lại trang và thử lại."), 400

    # Create tables if not exist in app context (safe for bootstrap)
    with app.app_context():
        try:
            db.create_all()
        except Exception as ex:
            app.logger.warning(f"Database tables could not be initialized at start: {ex}")

    return app
