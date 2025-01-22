from flask import Flask
from flask_pymongo import PyMongo
from prometheus_flask_exporter import PrometheusMetrics
import os

# Initialize MongoDB
mongo = PyMongo()
metrics = PrometheusMetrics(app=None)

def create_app():
    app = Flask(__name__)
    
    # Get MongoDB credentials from environment
    username = os.getenv('MONGO_USERNAME', 'url_shortener_user')
    password = os.getenv('MONGO_PASSWORD', 'app_password_123')
    database = os.getenv('MONGO_DATABASE', 'urlshortener')
    
    # Configure MongoDB with authentication
    app.config["MONGO_URI"] = f"mongodb://{username}:{password}@url-shortener-mongodb:27017/{database}?authSource={database}"
    
    # Initialize extensions
    mongo.init_app(app)
    metrics.init_app(app)
    
    # Register blueprints
    from app.routes.shorturl import shorturl_bp
    app.register_blueprint(shorturl_bp)
    
    return app