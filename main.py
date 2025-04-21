from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_cors import CORS
import requests
import os
import time
from functools import wraps
from dotenv import load_dotenv
import data_store

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Simple rate limiting implementation
class RateLimiter:
    def __init__(self, max_calls, time_frame):
        self.max_calls = max_calls
        self.time_frame = time_frame  # in seconds
        self.calls = {}

    def is_allowed(self, key):
        current_time = time.time()
        # Clean up old entries
        self.calls = {k: v for k, v in self.calls.items()
                     if current_time - v[-1] < self.time_frame}

        # Check if key exists
        if key not in self.calls:
            self.calls[key] = [current_time]
            return True

        # Check if max calls exceeded
        if len(self.calls[key]) < self.max_calls:
            self.calls[key].append(current_time)
            return True

        # Check if oldest call is outside time frame
        if current_time - self.calls[key][0] > self.time_frame:
            self.calls[key] = self.calls[key][1:] + [current_time]
            return True

        return False

# Create rate limiters
weather_limiter = RateLimiter(max_calls=10, time_frame=60)  # 10 calls per minute
locations_limiter = RateLimiter(max_calls=30, time_frame=60)  # 30 calls per minute

# Rate limiting decorator
def rate_limit(limiter):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client IP
            client_ip = request.remote_addr

            if not limiter.is_allowed(client_ip):
                return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429

            return f(*args, **kwargs)
        return decorated_function
    return decorator

# API Keys
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
if not WEATHER_API_KEY:
    raise ValueError("WEATHER_API_KEY environment variable is not set. Please add it to your .env file.")
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"

@app.route('/')
def get_route():
    return render_template('index.html')

@app.route('/locations')
def locations_page():
    return render_template('locations.html')

@app.route('/weather', methods=['GET'])
@rate_limit(weather_limiter)
def get_weather():
    city = request.args.get("city")
    lat = request.args.get("lat")
    lon = request.args.get("lon")

    params = {"appid": WEATHER_API_KEY, "units":"metric"}

    if city:
        # Search by city name
        params["q"] = city
    elif lat and lon:
        # Search by coordinates
        params["lat"] = lat
        params["lon"] = lon
    else:
        return jsonify({'error': "Provide a city name or coordinates"}), 400

    print(f"Fetching weather from: {WEATHER_API_URL}?{params}")
    response = requests.get(WEATHER_API_URL, params = params)

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch weather data"}), response.status_code
    return jsonify(response.json())


# CRUD Routes for Saved Locations

@app.route('/locations', methods=['GET'])
@rate_limit(locations_limiter)
def get_locations():
    """Get all saved locations"""
    locations = data_store.get_all_locations()
    return jsonify(locations)

@app.route('/locations/<int:location_id>', methods=['GET'])
def get_location(location_id):
    """Get a specific saved location"""
    location = data_store.get_location_by_id(location_id)
    if not location:
        return jsonify({'error': 'Location not found'}), 404
    return jsonify(location)

@app.route('/locations', methods=['POST'])
@rate_limit(locations_limiter)
def create_location():
    """Save a new location"""
    data = request.json

    # Validate input data
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    if 'city_name' not in data or not data['city_name']:
        return jsonify({'error': 'City name is required'}), 400

    # Sanitize inputs
    city_name = data['city_name'].strip()
    if len(city_name) > 100:
        return jsonify({'error': 'City name too long (max 100 characters)'}), 400

    # Sanitize other fields
    sanitized_data = {
        'city_name': city_name,
        'country_code': data.get('country_code', '').strip()[:10] if data.get('country_code') else '',
        'latitude': float(data['latitude']) if data.get('latitude') is not None else None,
        'longitude': float(data['longitude']) if data.get('longitude') is not None else None,
        'notes': data.get('notes', '').strip()[:500] if data.get('notes') else '',
        'is_favorite': bool(data.get('is_favorite', False))
    }

    # Create new location
    new_location = data_store.add_location(sanitized_data)
    if not new_location:
        return jsonify({'error': 'Location already saved'}), 400

    return jsonify(new_location), 201

@app.route('/locations/<int:location_id>', methods=['PUT'])
def update_location(location_id):
    """Update a saved location"""
    data = request.json

    # Validate input data
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Sanitize inputs
    sanitized_data = {}

    if 'notes' in data:
        sanitized_data['notes'] = data['notes'].strip()[:500] if data['notes'] else ''

    if 'is_favorite' in data:
        sanitized_data['is_favorite'] = bool(data['is_favorite'])

    if 'city_name' in data:
        city_name = data['city_name'].strip()
        if len(city_name) > 100:
            return jsonify({'error': 'City name too long (max 100 characters)'}), 400
        sanitized_data['city_name'] = city_name

    if 'country_code' in data:
        sanitized_data['country_code'] = data['country_code'].strip()[:10] if data['country_code'] else ''

    # Update location
    updated_location = data_store.update_location(location_id, sanitized_data)

    if not updated_location:
        return jsonify({'error': 'Location not found'}), 404

    return jsonify(updated_location)

@app.route('/locations/<int:location_id>', methods=['DELETE'])
def delete_location(location_id):
    """Delete a saved location"""
    success = data_store.delete_location(location_id)

    if not success:
        return jsonify({'error': 'Location not found'}), 404

    return jsonify({'message': 'Location deleted successfully'})

@app.route('/favorites', methods=['GET'])
def get_favorites():
    """Get all favorite locations"""
    favorites = data_store.get_favorites()
    return jsonify(favorites)

@app.route('/locations/search', methods=['GET'])
def search_locations():
    """Search saved locations"""
    query = request.args.get('q', '')
    locations = data_store.search_locations(query)
    return jsonify(locations)

# Add security headers to all responses
@app.after_request
def add_security_headers(response):
    # Prevent MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'DENY'
    # Enable XSS protection in browsers
    response.headers['X-XSS-Protection'] = '1; mode=block'
    # Strict HTTPS (when deployed with HTTPS)
    # response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    # Content Security Policy
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; object-src 'none'"
    return response

# Global error handler
@app.errorhandler(Exception)
def handle_exception(e):
    # Log the error
    app.logger.error(f"Unhandled exception: {str(e)}")

    # Return a generic error message in production
    return jsonify({
        'error': 'An unexpected error occurred. Please try again later.'
    }), 500

if __name__ == "__main__":
    # In production, set debug=False
    app.run(debug=True, host="0.0.0.0", port=5001)