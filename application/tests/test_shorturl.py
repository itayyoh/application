import pytest
from app import create_app
from flask import json

@pytest.fixture
def app(mongodb):
    app = create_app()
    app.config.update({
        'TESTING': True,
        'MONGO_URI': 'mongodb://mongodb_admin:admin_password_123@localhost:27017/urlshortener?authSource=urlshortener'
    })
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_create_shorturl(client):
    # First create a URL
    response = client.post('/shorturl/test123', 
                         json={'originalUrl': 'https://www.example.com'},
                         content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['id'] == 'test123'

    # Verify URL exists
    get_response = client.get('/shorturl/test123')
    assert get_response.status_code == 200

def test_get_shorturl_not_found(client):
    response = client.get('/shorturl/nonexistent')
    assert response.status_code == 404

def test_list_shorturls(client, mongodb):
    # Clear existing data
    mongodb.urls.delete_many({})
    
    # Create some test URLs
    urls = [
        {'_id': 'test1', 'original_url': 'https://example1.com'},
        {'_id': 'test2', 'original_url': 'https://example2.com'}
    ]
    mongodb.urls.insert_many(urls)
    
    # Test listing
    response = client.get('/shorturl')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'urls' in data
    assert len(data['urls']) == 2
    assert set(data['urls']) == {'test1', 'test2'}