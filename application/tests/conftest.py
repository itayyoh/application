import os
import sys
import pytest
from mongomock import MongoClient

# Add application directory to Python path
app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, app_dir)

@pytest.fixture(scope='function')
def mongodb():
    client = MongoClient()
    db = client.test_database
    yield db
    client.drop_database('test_database')