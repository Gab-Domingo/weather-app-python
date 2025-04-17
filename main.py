from flask import Flask, render_template, jsonify ,request
from flask_cors import CORS
import requests
app = Flask(__name__)
CORS(app)

WEATHER_API_KEY = "664b18aa8c610d3c3d0f65f548cda956"
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"

@app.route('/')
def get_route():
    return render_template('index.html')

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


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)