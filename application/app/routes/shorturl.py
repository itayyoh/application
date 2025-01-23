from flask import Blueprint, jsonify, request, render_template
from app import mongo
from prometheus_flask_exporter import PrometheusMetrics

shorturl_bp = Blueprint('shorturl', __name__)
prometheus_metrics = None

def init_metrics(app):
    global prometheus_metrics
    prometheus_metrics = PrometheusMetrics(app)

    def register_metrics():
        prometheus_metrics.counter('shorturl_create_total', 'Number of short URLs created')(create_short_url)
        prometheus_metrics.counter('shorturl_get_total', 'Number of short URL retrievals')(get_short_url)
    
    register_metrics()

@shorturl_bp.route('/')
def index():
   return render_template('index.html')

@shorturl_bp.route('/shorturl/<id>', methods=['POST'])
def create_short_url(id):
   data = request.get_json()
   if not data or 'originalUrl' not in data:
       return jsonify({'error': 'originalUrl is required'}), 400
       
   url_mapping = {
       '_id': id,
       'original_url': data['originalUrl']
   }
   
   try:
       mongo.db.urls.insert_one(url_mapping)
       return jsonify({'message': 'Short URL created', 'id': id}), 201
   except Exception as e:
       return jsonify({'error': 'URL already exists'}), 400

@shorturl_bp.route('/shorturl/<id>', methods=['GET'])
def get_short_url(id):
   url = mongo.db.urls.find_one({'_id': id})
   if url:
       url_data = {
           'id': url['_id'],
           'originalUrl': url['original_url']
       }
       return render_template('url_details.html', url_data=url_data)
   return jsonify({'error': 'URL not found'}), 404

@shorturl_bp.route('/shorturl', methods=['GET'])
def list_short_urls():
   urls = mongo.db.urls.find()
   return jsonify({
       'urls': [url['_id'] for url in urls]
   })

@shorturl_bp.route('/shorturl/<id>', methods=['PUT'])
def update_short_url(id):
   data = request.get_json()
   if not data or 'originalUrl' not in data:
       return jsonify({'error': 'originalUrl is required'}), 400
       
   result = mongo.db.urls.update_one(
       {'_id': id},
       {'$set': {'original_url': data['originalUrl']}}
   )
   
   if result.modified_count:
       return jsonify({'message': 'URL updated'})
   return jsonify({'error': 'URL not found'}), 404

@shorturl_bp.route('/shorturl/<id>', methods=['DELETE'])
def delete_short_url(id):
   result = mongo.db.urls.delete_one({'_id': id})
   if result.deleted_count:
       return jsonify({'message': 'URL deleted'})
   return jsonify({'error': 'URL not found'}), 404

@shorturl_bp.route('/metrics')
def get_url_metrics():
   total_urls = mongo.db.urls.count_documents({})
   return jsonify({
       'total_urls': total_urls
   })