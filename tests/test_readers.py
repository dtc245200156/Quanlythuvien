from app.models.reader import Reader

def test_readers_index(client):
    """Test readers index page."""
    response = client.get('/readers/')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert 'Phạm Thị Test' in html
    assert 'DGTEST001' in html

def test_create_reader_success(client, app):
    """Test creating a new reader."""
    response = client.post('/readers/create', data={
        'reader_code': 'DGTEST999',
        'full_name': 'Lê Hoàng Nam',
        'email': 'nam.le@example.com',
        'phone': '0901234567',
        'address': 'K21-CNTT',
        'registered_date': '2025-01-01'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert 'Thêm độc giả' in response.data.decode('utf-8')

    with app.app_context():
        reader = Reader.query.filter_by(reader_code='DGTEST999').first()
        assert reader is not None
        assert reader.full_name == 'Lê Hoàng Nam'

def test_create_reader_duplicate_code(client):
    """Test rejection when creating duplicate reader code."""
    response = client.post('/readers/create', data={
        'reader_code': 'DGTEST001',
        'full_name': 'Người Trùng Mã',
        'email': 'trungma@example.com'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert 'đã tồn tại' in response.data.decode('utf-8')

def test_create_reader_duplicate_email(client):
    """Test rejection when creating duplicate email."""
    response = client.post('/readers/create', data={
        'reader_code': 'DGNEW123',
        'full_name': 'Người Trùng Email',
        'email': 'phamthitest@example.com'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert 'đã được đăng ký' in response.data.decode('utf-8')

def test_deactivate_reader(client, app):
    """Test reader deactivation / soft deletion."""
    with app.app_context():
        reader = Reader.query.filter_by(reader_code='DGTEST002').first()
        reader_id = reader.id

    response = client.post(f'/readers/{reader_id}/delete', follow_redirects=True)
    assert response.status_code == 200
