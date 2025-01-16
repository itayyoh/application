import os
import sys
import pytest
import time
from pymongo import MongoClient

# Add application directory to Python path
app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, app_dir)

@pytest.fixture(scope='session')
def mongodb():
    # Start MongoDB using docker-compose
    os.system('docker-compose up -d mongodb')
    time.sleep(10)  # Give MongoDB time to start
    
    # Initialize test database
    client = MongoClient(
        'mongodb://mongodb_admin:admin_password_123@localhost:27017/urlshortener?authSource=urlshortener'
    )
    db = client.urlshortener
    
    yield db
    
    # Cleanup
    client.drop_database('urlshortener')
    client.close()
    os.system('docker-compose down')