from flask import Flask
from flask_pymongo import PyMongo
from prometheus_flask_exporter import PrometheusMetrics

# Initialize MongoDB
mongo = PyMongo()
metrics = PrometheusMetrics(app=None)

def create_app():
    app = Flask(__name__)
    
    # Configure MongoDB
    app.config["MONGO_URI"] = "mongodb://mongodb:27017/urlshortener"
    
    # Initialize extensions
    mongo.init_app(app)
    metrics.init_app(app)
    
    # Register blueprints
    from app.routes.shorturl import shorturl_bp
    app.register_blueprint(shorturl_bp)
    
    return app