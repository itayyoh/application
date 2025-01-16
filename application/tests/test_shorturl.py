import pytest
from app import create_app
from flask import json

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_create_shorturl(client):
    response = client.post('/shorturl/test123', 
                         json={'originalUrl': 'https://www.example.com'},
                         content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['id'] == 'test123'

def test_get_shorturl(client):
    # First create a URL
    client.post('/shorturl/test456', 
                json={'originalUrl': 'https://www.example.com'},
                content_type='application/json')
    
    # Then retrieve it
    response = client.get('/shorturl/test456')
    assert response.status_code == 200

def test_invalid_create_shorturl(client):
    response = client.post('/shorturl/test789',
                         json={},  # Missing originalUrl
                         content_type='application/json')
    assert response.status_code == 400

def test_list_shorturls(client):
    response = client.get('/shorturl')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'urls' in data