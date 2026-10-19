from app.models.book import Book
from app.services.library_service import LibraryService

def test_books_index(client):
    """Test book listing page."""
    response = client.get('/books/')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert 'Python' in html
    assert 'Linux' in html

def test_books_search(client):
    """Test searching books by keyword."""
    # Search title
    response = client.get('/books/?q=Python')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert 'Lập Trình Python' in html
    assert 'Quản Trị Hệ Thống Linux' not in html

    # Search ISBN
    response = client.get('/books/?q=978-604-0-99992-0')
    assert response.status_code == 200
    assert 'Linux' in response.data.decode('utf-8')

def test_create_book_success(client, app):
    """Test successfully creating a new book."""
    response = client.post('/books/create', data={
        'isbn': '978-604-0-12345-6',
        'title': 'Kiến Trúc Đám Mây Mới',
        'author': 'Vũ Cloud',
        'category': 'DevOps & Cloud',
        'publisher': 'NXB Khoa Học',
        'publish_year': '2024',
        'total_quantity': '10'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert 'Thêm sách' in response.data.decode('utf-8')

    with app.app_context():
        book = Book.query.filter_by(isbn='978-604-0-12345-6').first()
        assert book is not None
        assert book.available_quantity == 10

def test_create_book_duplicate_isbn(client):
    """Test rejection when creating a book with duplicate ISBN."""
    response = client.post('/books/create', data={
        'isbn': '978-604-0-99991-0',  # already in seed
        'title': 'Sách Trùng ISBN',
        'author': 'Tác Giả Khác',
        'category': 'Khác',
        'total_quantity': '5'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert 'đã tồn tại' in response.data.decode('utf-8')

def test_create_book_negative_quantity(client):
    """Test rejection when quantity is negative."""
    response = client.post('/books/create', data={
        'isbn': '978-604-0-88888-8',
        'title': 'Sách Lỗi Số Lượng',
        'author': 'Tác Giả Lỗi',
        'category': 'Khác',
        'total_quantity': '-3'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert 'không được là số âm' in response.data.decode('utf-8')

def test_update_book(client, app):
    """Test updating existing book."""
    with app.app_context():
        book = Book.query.filter_by(isbn='978-604-0-99991-0').first()
        book_id = book.id

    response = client.post(f'/books/{book_id}/edit', data={
        'isbn': '978-604-0-99991-0',
        'title': 'Lập Trình Python Cập Nhật Mới',
        'author': 'Nguyễn Văn Test',
        'category': 'Công nghệ thông tin',
        'publisher': 'NXB Giáo Dục',
        'publish_year': '2025',
        'total_quantity': '8'
    }, follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        updated = Book.query.get(book_id)
        assert updated.title == 'Lập Trình Python Cập Nhật Mới'
        assert updated.total_quantity == 8
        assert updated.available_quantity == 8

def test_delete_book_without_loans(client, app):
    """Test deleting a book that has never been loaned."""
    with app.app_context():
        book = Book.query.filter_by(isbn='978-604-0-99992-0').first()
        book_id = book.id

    response = client.post(f'/books/{book_id}/delete', follow_redirects=True)
    assert response.status_code == 200
    assert 'Đã xóa sách' in response.data.decode('utf-8')

    with app.app_context():
        assert Book.query.get(book_id) is None
