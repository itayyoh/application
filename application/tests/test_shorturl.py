import pytest
from app import create_app
from flask import json
import mongomock

@pytest.fixture
def app(mongodb):
    app = create_app()
    # Override the PyMongo instance with our mock
    app.config['MONGO_URI'] = 'mongomock://localhost'
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_create_shorturl(client):
    # Create a URL
    response = client.post('/shorturl/test123', 
                         json={'originalUrl': 'https://www.example.com'},
                         content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['id'] == 'test123'

def test_get_shorturl_not_found(client):
    response = client.get('/shorturl/nonexistent')
    assert response.status_code == 404

def test_list_shorturls(client, mongodb):
    # Insert test data directly into mock database
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
    assert sorted(data['urls']) == ['test1', 'test2']