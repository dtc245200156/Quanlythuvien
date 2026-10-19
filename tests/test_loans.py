from datetime import date, timedelta
import pytest
from app.extensions import db
from app.models.book import Book
from app.models.reader import Reader
from app.models.loan import Loan, LoanDetail
from app.services.library_service import LibraryService

def test_create_loan_success(client, app):
    """Test creating a loan ticket successfully."""
    with app.app_context():
        reader = Reader.query.filter_by(reader_code='DGTEST001').first()
        book = Book.query.filter_by(isbn='978-604-0-99991-0').first()
        initial_available = book.available_quantity
        reader_id = reader.id
        book_id = book.id

    response = client.post('/loans/create', data={
        'reader_id': reader_id,
        'borrow_date': date.today().isoformat(),
        'due_date': (date.today() + timedelta(days=14)).isoformat(),
        'book_ids': [book_id],
        f'qty_{book_id}': 2,
        'notes': 'Test loan creation'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert 'Tạo phiếu mượn' in response.data.decode('utf-8')

    with app.app_context():
        updated_book = Book.query.get(book_id)
        assert updated_book.available_quantity == initial_available - 2
        loan = Loan.query.filter_by(reader_id=reader_id).order_by(Loan.id.desc()).first()
        assert loan is not None
        assert loan.status == 'borrowing'
        assert len(loan.details) == 1
        assert loan.details[0].quantity == 2
        assert loan.details[0].returned is False

def test_reject_loan_when_out_of_stock(client, app):
    """Test rejection when attempting to borrow an out of stock book."""
    with app.app_context():
        reader = Reader.query.filter_by(reader_code='DGTEST001').first()
        empty_book = Book.query.filter_by(isbn='978-604-0-99993-0').first()
        reader_id = reader.id
        book_id = empty_book.id

    response = client.post('/loans/create', data={
        'reader_id': reader_id,
        'due_date': (date.today() + timedelta(days=7)).isoformat(),
        'book_ids': [book_id],
        f'qty_{book_id}': 1
    }, follow_redirects=True)
    assert response.status_code == 200
    assert 'không đủ để mượn' in response.data.decode('utf-8')

def test_reject_loan_when_quantity_exceeds_available(client, app):
    """Test rejection when requesting more than available quantity."""
    with app.app_context():
        reader = Reader.query.filter_by(reader_code='DGTEST001').first()
        book = Book.query.filter_by(isbn='978-604-0-99992-0').first()  # total 2
        reader_id = reader.id
        book_id = book.id

    response = client.post('/loans/create', data={
        'reader_id': reader_id,
        'due_date': (date.today() + timedelta(days=7)).isoformat(),
        'book_ids': [book_id],
        f'qty_{book_id}': 99  # Exceeds 2
    }, follow_redirects=True)
    assert response.status_code == 200
    assert 'không đủ để mượn' in response.data.decode('utf-8')

def test_reject_loan_for_inactive_reader(client, app):
    """Test rejection when reader is inactive."""
    with app.app_context():
        inactive_reader = Reader.query.filter_by(reader_code='DGTEST002').first()
        book = Book.query.filter_by(isbn='978-604-0-99991-0').first()
        reader_id = inactive_reader.id
        book_id = book.id

    response = client.post('/loans/create', data={
        'reader_id': reader_id,
        'due_date': (date.today() + timedelta(days=7)).isoformat(),
        'book_ids': [book_id],
        f'qty_{book_id}': 1
    }, follow_redirects=True)
    assert response.status_code == 200
    assert 'ngừng hoạt động' in response.data.decode('utf-8')

def test_return_book_item_and_prevent_duplicate_return(client, app):
    """Test returning a book item and ensuring it cannot be returned twice."""
    with app.app_context():
        reader = Reader.query.filter_by(reader_code='DGTEST001').first()
        book = Book.query.filter_by(isbn='978-604-0-99991-0').first()
        initial_available = book.available_quantity
        reader_id = reader.id
        book_id = book.id

        loan = LibraryService.create_loan(
            reader_id=reader_id,
            book_items=[{'book_id': book_id, 'quantity': 1}],
            borrow_date=date.today(),
            due_date=date.today() + timedelta(days=7)
        )
        detail_id = loan.details[0].id
        loan_id = loan.id

    # 1. First return: should succeed
    response = client.post(f'/loans/return-item/{detail_id}', follow_redirects=True)
    assert response.status_code == 200
    assert 'Đã trả sách' in response.data.decode('utf-8')

    with app.app_context():
        item = db.session.get(LoanDetail, detail_id)
        assert item.returned is True
        assert item.return_date == date.today()
        # Verify book stock returned
        updated_book = db.session.get(Book, book_id)
        assert updated_book.available_quantity == initial_available

        # Verify loan status updated to 'returned'
        loan_refreshed = db.session.get(Loan, loan_id)
        assert loan_refreshed.status == 'returned'

    # 2. Second return on same item: must be rejected!
    response2 = client.post(f'/loans/return-item/{detail_id}', follow_redirects=True)
    assert response2.status_code == 200
    assert 'Không thể trả lần hai' in response2.data.decode('utf-8')
