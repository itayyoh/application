import os
import sys
import pytest
from mongomock import MongoClient
from app import create_app, mongodb

# Add application directory to Python path
app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, app_dir)

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'MONGO_URI': 'mongomock://localhost'
    })
    
    # Create a mongomock client
    mock_client = MongoClient()
    with app.app_context():
        mongodb.cx = mock_client
        mongodb.db = mock_client.test_database
        # Clear any existing data
        mongodb.db.urls.delete_many({})
    
    yield app
    
    # Cleanup after tests
    mock_client.drop_database('test_database')

@pytest.fixture
def client(app):
    return app.test_client()