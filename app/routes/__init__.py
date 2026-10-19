from app.routes.main import main_bp
from app.routes.books import books_bp
from app.routes.readers import readers_bp
from app.routes.loans import loans_bp

def register_blueprints(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(readers_bp)
    app.register_blueprint(loans_bp)
