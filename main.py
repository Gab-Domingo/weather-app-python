from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
import data_store

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# API Keys
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "664b18aa8c610d3c3d0f65f548cda956")
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"

@app.route('/')
def get_route():
    return render_template('index.html')

@app.route('/locations')
def locations_page():
    return render_template('locations.html')

@app.route('/weather', methods=['GET'])
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
def create_location():
    """Save a new location"""
    data = request.json

    # Create new location
    new_location = data_store.add_location(data)
    if not new_location:
        return jsonify({'error': 'Location already saved'}), 400

    return jsonify(new_location), 201

@app.route('/locations/<int:location_id>', methods=['PUT'])
def update_location(location_id):
    """Update a saved location"""
    data = request.json
    updated_location = data_store.update_location(location_id, data)

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

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)