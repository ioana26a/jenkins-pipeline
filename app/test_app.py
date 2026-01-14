from app import app


def test_home():
    """Test the home endpoint."""
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    # The message now includes the environment
    is_prod = (
        app.config.get('ENV') == 'prod' or
        app.config.get('FLASK_ENV') == 'prod'
    )
    if is_prod:
        expected_env = 'PRODUCTION ENVIRONMENT'
    else:
        expected_env = 'DEVELOPMENT ENVIRONMENT'
    expected_message = (
        f'Flask API running on port 5000 - {expected_env}'
    )
    assert response.json == {'message': expected_message}


def test_health_check_db_disconnected(monkeypatch):
    """Test health check when DB is disconnected."""
    def fake_get_db_connection():
        return None
    monkeypatch.setattr('app.get_db_connection', fake_get_db_connection)
    client = app.test_client()
    response = client.get('/api/health')
    assert response.status_code == 500
    assert (
        response.json['status'] == 'unhealthy'
        or response.json['database'] == 'disconnected'
    )


def test_get_data_db_disconnected(monkeypatch):
    """Test /api/data when DB is disconnected."""
    def fake_get_db_connection():
        return None
    monkeypatch.setattr('app.get_db_connection', fake_get_db_connection)
    client = app.test_client()
    response = client.get('/api/data')
    assert response.status_code == 500
    assert 'error' in response.json
