import time
from flask import request
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# Metrics definitions
HTTP_REQUESTS_TOTAL = Counter(
    'http_requests_total',
    'Total count of HTTP requests processed',
    ['method', 'endpoint', 'status']
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
)

DB_CONNECTION_STATUS = Gauge(
    'library_db_connection_up',
    'Database connection health status (1 for connected, 0 for disconnected)'
)

ACTIVE_LOANS_COUNT = Gauge(
    'library_active_loans_count',
    'Current number of active library loans'
)

BOOKS_IN_STOCK_COUNT = Gauge(
    'library_books_in_stock_count',
    'Current count of books available in inventory'
)

def init_metrics(app):
    """Register request hooks and metrics endpoint to Flask application."""
    
    @app.before_request
    def before_request_hook():
        request._start_time = time.time()

    @app.after_request
    def after_request_hook(response):
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            endpoint = request.endpoint or 'unknown'
            # Avoid high-cardinality label explosion by sanitizing static requests
            if endpoint.startswith('static'):
                endpoint = 'static'
            
            HTTP_REQUESTS_TOTAL.labels(
                method=request.method,
                endpoint=endpoint,
                status=response.status_code
            ).inc()
            
            HTTP_REQUEST_DURATION_SECONDS.labels(
                method=request.method,
                endpoint=endpoint
            ).observe(duration)
            
        return response

    @app.route('/metrics')
    def metrics_endpoint():
        """Prometheus metrics scrape target."""
        # Update database check
        try:
            from app.extensions import db
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            DB_CONNECTION_STATUS.set(1)
        except Exception:
            DB_CONNECTION_STATUS.set(0)

        # Update loan counts
        try:
            from app.models.loan import Loan
            from app.models.book import Book
            active_count = Loan.query.filter(Loan.status.in_(['borrowing', 'overdue'])).count()
            ACTIVE_LOANS_COUNT.set(active_count)
            available_books = db.session.query(db.func.sum(Book.available_quantity)).scalar() or 0
            BOOKS_IN_STOCK_COUNT.set(available_books)
        except Exception:
            pass

        return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}
