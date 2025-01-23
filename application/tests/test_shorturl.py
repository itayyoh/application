import pytest
from app import create_app, mongodb
from flask import json
import mongomock
from pymongo import MongoClient

@pytest.fixture
def app():
    app = create_app()
    # Override the Flask-PyMongo instance with our mock
    app.config.update({
        'TESTING': True,
        'MONGO_URI': 'mongomock://localhost'
    })
    
    # Create a mongomock client
    mock_client = mongomock.MongoClient()
    mongodb.cx = mock_client
    mongodb.db = mock_client.db
    
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_create_shorturl(client):
    # Create a URL
    response = client.post('/shorturl/test123', 
                         json={'originalUrl': 'https://www.example.com'},
                         content_type='application/json')
    print(f"Response data: {response.data}")
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['id'] == 'test123'

    # Verify URL exists
    get_response = client.get('/shorturl/test123')
    assert get_response.status_code == 200

def test_get_shorturl_not_found(client):
    response = client.get('/shorturl/nonexistent')
    assert response.status_code == 404

def test_list_shorturls(client):
    # First, add some URLs
    client.post('/shorturl/test1', 
                json={'originalUrl': 'https://example1.com'},
                content_type='application/json')
    client.post('/shorturl/test2', 
                json={'originalUrl': 'https://example2.com'},
                content_type='application/json')
    
    # Test listing
    response = client.get('/shorturl')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'urls' in data
    assert sorted(data['urls']) == ['test1', 'test2']