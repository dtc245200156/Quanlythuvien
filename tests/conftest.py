import pytest
from datetime import date, timedelta
from app import create_app
from app.extensions import db
from app.models.book import Book
from app.models.reader import Reader
from app.models.loan import Loan, LoanDetail

@pytest.fixture
def app():
    """Create and configure a clean Flask application instance for testing."""
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False,  # Disable CSRF in tests for direct form submission
        'SECRET_KEY': 'test-secret-key-12345'
    }
    app = create_app(test_config=test_config)

    with app.app_context():
        db.create_all()

        # Seed initial test data
        b1 = Book(
            isbn='978-604-0-99991-0',
            title='Lập Trình Python Cơ Bản Đến Nâng Cao',
            author='Nguyễn Văn Test',
            category='Công nghệ thông tin',
            publisher='NXB Giáo Dục',
            publish_year=2023,
            total_quantity=5,
            available_quantity=5
        )
        b2 = Book(
            isbn='978-604-0-99992-0',
            title='Quản Trị Hệ Thống Linux Toàn Tập',
            author='Trần Văn Test',
            category='Hệ điều hành & Mạng',
            publisher='NXB Bách Khoa',
            publish_year=2024,
            total_quantity=2,
            available_quantity=2
        )
        b_empty = Book(
            isbn='978-604-0-99993-0',
            title='Sách Đã Hết Trong Kho',
            author='Lê Hết Hàng',
            category='Khác',
            publisher='NXB Thử Nghiệm',
            publish_year=2022,
            total_quantity=1,
            available_quantity=0  # Out of stock
        )

        r1 = Reader(
            reader_code='DGTEST001',
            full_name='Phạm Thị Test',
            email='phamthitest@example.com',
            phone='0987111222',
            address='Lớp K21-CNTT',
            status='active',
            registered_date=date.today() - timedelta(days=10)
        )
        r_inactive = Reader(
            reader_code='DGTEST002',
            full_name='Độc Giả Bị Khóa',
            email='locked@example.com',
            phone='0987333444',
            address='Lớp Cựu sinh viên',
            status='inactive',
            registered_date=date.today() - timedelta(days=30)
        )

        db.session.add_all([b1, b2, b_empty, r1, r_inactive])
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Test client for making HTTP requests."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Test CLI runner."""
    return app.test_cli_runner()
