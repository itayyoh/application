# app/__init__.py
from flask import Flask
from flask_pymongo import PyMongo
import os

mongodb = PyMongo()

def create_app():
    app = Flask(__name__)
    
    if app.config.get('TESTING'):
        # Use test configuration if provided
        mongodb.init_app(app)
    else:
        # Regular configuration for non-test environment
        username = os.getenv('MONGO_USERNAME', 'url_shortener_user')
        password = os.getenv('MONGO_PASSWORD', 'app_password_123')
        database = os.getenv('MONGO_DATABASE', 'urlshortener')
        
        app.config["MONGO_URI"] = f"mongodb://{username}:{password}@url-shortener-mongodb:27017/{database}?authSource={database}"
        mongodb.init_app(app)
    
    from app.routes.shorturl import shorturl_bp, init_metrics
    
    # Initialize metrics before registering blueprint
    init_metrics(app)
    app.register_blueprint(shorturl_bp)

    return app