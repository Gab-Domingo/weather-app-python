import json
import os
import tempfile
import shutil
from datetime import datetime

# File to store locations
LOCATIONS_FILE = 'locations.json'

# Ensure data directory exists and has proper permissions
def ensure_data_directory():
    data_dir = os.path.dirname(LOCATIONS_FILE)
    if data_dir and not os.path.exists(data_dir):
        os.makedirs(data_dir, mode=0o700)  # Only owner can read/write/execute

def get_all_locations():
    """Get all saved locations"""
    if not os.path.exists(LOCATIONS_FILE):
        return []

    try:
        with open(LOCATIONS_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_locations(locations):
    """Save locations to file securely using atomic write"""
    # Ensure directory exists
    ensure_data_directory()

    # Create a temporary file in the same directory
    fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(LOCATIONS_FILE) or '.')

    try:
        with os.fdopen(fd, 'w') as temp_file:
            json.dump(locations, temp_file, indent=2)

        # Flush to disk and fsync
        temp_file.flush()
        os.fsync(temp_file.fileno())

        # Atomic rename
        shutil.move(temp_path, LOCATIONS_FILE)

        # Set secure permissions
        os.chmod(LOCATIONS_FILE, 0o600)  # Only owner can read/write
    except Exception as e:
        # Clean up the temp file if something goes wrong
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise e

def get_location_by_id(location_id):
    """Get a location by ID"""
    locations = get_all_locations()
    for location in locations:
        if location['id'] == location_id:
            return location
    return None

def add_location(location_data):
    """Add a new location"""
    locations = get_all_locations()

    # Check if location already exists
    for loc in locations:
        if loc['city_name'].lower() == location_data['city_name'].lower():
            return None

    # Generate ID
    new_id = 1
    if locations:
        new_id = max(loc['id'] for loc in locations) + 1

    # Create new location
    now = datetime.now().isoformat()
    new_location = {
        'id': new_id,
        'city_name': location_data['city_name'],
        'country_code': location_data.get('country_code', ''),
        'latitude': location_data.get('latitude'),
        'longitude': location_data.get('longitude'),
        'notes': location_data.get('notes', ''),
        'is_favorite': location_data.get('is_favorite', False),
        'created_at': now,
        'updated_at': now
    }

    locations.append(new_location)
    save_locations(locations)
    return new_location

def update_location(location_id, update_data):
    """Update a location"""
    locations = get_all_locations()
    for index, location in enumerate(locations):
        if location['id'] == location_id:
            # Update fields
            for key, value in update_data.items():
                if key in location:
                    location[key] = value

            location['updated_at'] = datetime.now().isoformat()
            # Update the location in the list
            locations[index] = location
            save_locations(locations)
            return location
    return None

def delete_location(location_id):
    """Delete a location"""
    locations = get_all_locations()
    for i, location in enumerate(locations):
        if location['id'] == location_id:
            del locations[i]
            save_locations(locations)
            return True
    return False

def get_favorites():
    """Get favorite locations"""
    locations = get_all_locations()
    return [loc for loc in locations if loc.get('is_favorite', False)]

def search_locations(query):
    """Search locations by name"""
    locations = get_all_locations()
    query = query.lower()
    return [loc for loc in locations if query in loc['city_name'].lower()]
