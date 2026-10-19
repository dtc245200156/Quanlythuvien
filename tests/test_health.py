import json

def test_health_check_endpoint(client):
    """Test that the /health endpoint returns 200 and healthy status."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data.decode('utf-8'))
    assert data.get('status') == 'healthy'
    assert data.get('service') == 'library-management'
    assert 'timestamp' in data

def test_metrics_endpoint(client):
    """Test that the /metrics endpoint returns 200 and valid Prometheus metrics."""
    response = client.get('/metrics')
    assert response.status_code == 200
    content = response.data.decode('utf-8')
    assert 'http_requests_total' in content
    assert 'library_db_connection_up' in content

def test_dashboard_route(client):
    """Test that the main dashboard route loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert 'Bảng Điều Khiển' in response.data.decode('utf-8')
    assert 'Tổng số sách' in response.data.decode('utf-8')
