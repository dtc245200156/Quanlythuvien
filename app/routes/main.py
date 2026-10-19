from datetime import datetime
from flask import Blueprint, render_template, jsonify
from sqlalchemy import text
from app.extensions import db
from app.services.library_service import LibraryService

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def dashboard():
    stats = LibraryService.get_dashboard_stats()
    return render_template('dashboard.html', stats=stats)

@main_bp.route('/health')
def health_check():
    """Healthcheck endpoint for Docker healthcheck and container orchestrators."""
    db_status = "healthy"
    status_code = 200
    try:
        db.session.execute(text('SELECT 1'))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
        status_code = 503

    return jsonify({
        "status": "healthy" if status_code == 200 else "degraded",
        "service": "library-management",
        "timestamp": datetime.utcnow().isoformat(),
        "database": db_status
    }), status_code
