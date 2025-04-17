# Weather App

A web application built with Flask that displays weather information based on city name. The app provides current weather data through an interactive interface.

## Features

- Get real-time weather data by searching for any city name
- Clean and responsive user interface
- Visual representation of weather conditions
- Support for temperature, humidity, wind speed, and other weather metrics

## Prerequisites

Before running the application, make sure you have the following installed:
- Python 3+
- Flask
- requests library
- Any modern web browser

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/weather-app.git
cd weather-app
```

2. Install the required dependencies:
```bash
pip3 install -r requirements.txt
```

## Running the Application

1. Ensure you're in the project directory and your virtual environment is activated
2. Start the Flask development server:
```bash
python main.py
```
3. Open your web browser and navigate to `http://localhost:5001`

## Project Structure

```
weather-app/
├── main.py              # Flask application file
├── static/
│   ├── css/           # Stylesheet files
│      └── style.css
├── templates/          # HTML templates
│   └── index.html
└── README.md
```

## Usage

1. Open the application in your web browser
2. Enter a city name (e.g., "London", "Tokyo", "New York") in the input field
3. Click the "Get Weather" button to fetch weather information
4. View the weather details displayed on the screen

## API Reference

The application uses the following endpoint:

```
GET /weather
Parameters:
- city: City name (string)
  OR
- lat: Latitude (float)
- lon: Longitude (float)

Response: JSON object containing weather information
```

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request


## Acknowledgments

- Weather data provided by Open Weather app
- Built with Flask framework