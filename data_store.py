import json
import os
from datetime import datetime

# File to store locations
LOCATIONS_FILE = 'locations.json'

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
    """Save locations to file"""
    with open(LOCATIONS_FILE, 'w') as f:
        json.dump(locations, f, indent=2)

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
    for i, location in enumerate(locations):
        if location['id'] == location_id:
            # Update fields
            for key, value in update_data.items():
                if key in location:
                    location[key] = value
            
            location['updated_at'] = datetime.now().isoformat()
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
