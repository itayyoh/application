from flask import Flask
from flask_pymongo import PyMongo
import os

mongo = PyMongo()

def create_app():
   app = Flask(__name__)
   
   username = os.getenv('MONGO_USERNAME', 'url_shortener_user')
   password = os.getenv('MONGO_PASSWORD', 'app_password_123')
   database = os.getenv('MONGO_DATABASE', 'urlshortener')
   
   app.config["MONGO_URI"] = f"mongodb://{username}:{password}@url-shortener-mongodb:27017/{database}?authSource={database}"
   
   mongo.init_app(app)
   
   from app.routes.shorturl import shorturl_bp, init_metrics
   app.register_blueprint(shorturl_bp)
   init_metrics(app)

   return app