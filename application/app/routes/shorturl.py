from flask import Blueprint, jsonify, request, render_template
from app import mongodb
from prometheus_flask_exporter import PrometheusMetrics
from functools import wraps

shorturl_bp = Blueprint('shorturl', __name__)
prometheus_metrics = None

# Define metrics at module level
create_counter = None
get_counter = None
update_counter = None
delete_counter = None
url_gauge = None

def metric_decorator(counter):
    """Wrapper function for metrics"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if counter:
                counter.inc()
            return f(*args, **kwargs)
        return wrapped
    return decorator

def init_metrics(app):
    """Initialize Prometheus metrics for the application."""
    global prometheus_metrics, create_counter, get_counter, update_counter, delete_counter, url_gauge
    
    if prometheus_metrics is None:
        prometheus_metrics = PrometheusMetrics(app)
        
        # Initialize counters with descriptions
        create_counter = prometheus_metrics.counter(
            'shorturl_create_total',
            'Number of short URLs created'
        )
        get_counter = prometheus_metrics.counter(
            'shorturl_get_total',
            'Number of short URL retrievals'
        )
        update_counter = prometheus_metrics.counter(
            'shorturl_update_total',
            'Number of URL updates'
        )
        delete_counter = prometheus_metrics.counter(
            'shorturl_delete_total',
            'Number of URL deletions'
        )
        url_gauge = prometheus_metrics.gauge(
            'shorturl_current_urls',
            'Current number of URLs in the system'
        )

@shorturl_bp.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@shorturl_bp.route('/shorturl/<id>', methods=['POST'])
@metric_decorator(create_counter)
def create_short_url(id):
    """Create a new short URL."""
    data = request.get_json()
    print(f"Received data: {data}")
    
    if not data or 'originalUrl' not in data:
        print("Data validation failed")
        return jsonify({'error': 'originalUrl is required'}), 400
    
    url_mapping = {
        '_id': id,
        'original_url': data['originalUrl']
    }
    print(f"URL mapping: {url_mapping}") 
    
    existing_url = mongodb.db.urls.find_one({'_id': id})
    print(f"Existing URL check: {existing_url}")
    if existing_url:
        print("URL exists")
        return jsonify({'error': 'URL already exists'}), 400
    
    try:
        mongodb.db.urls.insert_one(url_mapping)
        if url_gauge:
            total_urls = mongodb.db.urls.count_documents({})
            url_gauge.set(total_urls)
        return jsonify({'message': 'Short URL created', 'id': id}), 201
    except Exception as e:
        return jsonify({'error': 'URL already exists'}), 400

@shorturl_bp.route('/shorturl/<id>', methods=['GET'])
@metric_decorator(get_counter)
def get_short_url(id):
    """Retrieve a short URL by ID."""
    url = mongodb.db.urls.find_one({'_id': id})
    if url:
        url_data = {
            'id': url['_id'],
            'originalUrl': url['original_url']
        }
        return render_template('url_details.html', url_data=url_data)
    return jsonify({'error': 'URL not found'}), 404

@shorturl_bp.route('/shorturl', methods=['GET'])
def list_short_urls():
    """List all short URLs."""
    urls = mongodb.db.urls.find()
    return jsonify({
        'urls': [url['_id'] for url in urls]
    })

@shorturl_bp.route('/shorturl/<id>', methods=['PUT'])
@metric_decorator(update_counter)
def update_short_url(id):
    """Update an existing short URL."""
    data = request.get_json()
    if not data or 'originalUrl' not in data:
        return jsonify({'error': 'originalUrl is required'}), 400
    
    result = mongodb.db.urls.update_one(
        {'_id': id},
        {'$set': {'original_url': data['originalUrl']}}
    )
    
    if result.modified_count:
        return jsonify({'message': 'URL updated'})
    return jsonify({'error': 'URL not found'}), 404

@shorturl_bp.route('/shorturl/<id>', methods=['DELETE'])
@metric_decorator(delete_counter)
def delete_short_url(id):
    """Delete a short URL."""
    result = mongodb.db.urls.delete_one({'_id': id})
    if result.deleted_count:
        if url_gauge:
            total_urls = mongodb.db.urls.count_documents({})
            url_gauge.set(total_urls)
        return jsonify({'message': 'URL deleted'})
    return jsonify({'error': 'URL not found'}), 404