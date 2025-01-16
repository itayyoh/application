import pytest
from app import create_app
from flask import json

@pytest.fixture
def client():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'MONGO_URI': 'mongodb://mongodb_admin:admin_password_123@mongodb:27017/urlshortener?authSource=urlshortener'
    })
    with app.test_client() as client:
        yield client

def test_create_shorturl(client):
    response = client.post('/shorturl/test123', 
                         json={'originalUrl': 'https://www.example.com'},
                         content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['id'] == 'test123'

def test_get_shorturl_not_found(client):
    response = client.get('/shorturl/nonexistent')
    assert response.status_code == 404

def test_list_shorturls(client):
    response = client.get('/shorturl')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'urls' in data