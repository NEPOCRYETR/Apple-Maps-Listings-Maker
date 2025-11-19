from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import random
import time
import database as db

app = Flask(__name__)
CORS(app)

# Initialize database on startup
db.init_database()

# Service-specific business name components
SERVICE_NAMES = {
    "Locksmith": {
        "prefixes": ["Secure", "Iron Gate", "Fortress", "Sentry", "Guardian", "Citadel", "Ironclad",
                    "Fortify", "Shield", "Centurion", "Sentinel", "SafeGuard", "KeyMaster", "LockPro",
                    "Access Control", "SecureKey", "Premier", "Elite", "Professional", "Expert"],
        "core": ["Lock & Key", "Locksmith", "Lock Services", "Key Services", "Security Systems",
                "Lock Solutions", "Lock & Safe", "Security Services", "Lock Repair", "Key Rescue",
                "Lock Change", "Lock Masters", "Security Solutions", "Access Systems"],
        "suffixes": ["Services", "Solutions", "Pros", "Masters", "Experts", "Specialists",
                    "Near You", "Near Me", "Company", "Group", "Team", "Inc", "LLC"],
        "locations": ["Downtown", "Uptown", "Midtown", "Metro", "City", "Central", "District",
                     "Plaza", "Square", "Avenue", "Street", "Boulevard", "Park"]
    },
    "Chimney Cleaning": {
        "prefixes": ["Clean", "Clear", "Pure", "Pristine", "Elite", "Master", "Summit", "Guardian",
                    "Swift", "Precision", "A1", "FlueMaster", "ChimneyShield", "CleanFlue", "FlueBright",
                    "ClearFlame", "SkyHigh", "Guardian", "SwiftPath", "FlueGuard", "Professional"],
        "core": ["Chimney Sweep", "Chimney Services", "Flue Cleaners", "Hearth Care", "Chimney Care",
                "Flue Sweep", "Chimney Cleaners", "Hearth Sweep", "Chimney Shine", "Flue Masters",
                "Sweep Services", "Chimney Maintenance"],
        "suffixes": ["Services", "Pros", "Care", "Cleaners", "Masters", "Specialists", "Solutions",
                    "Company", "Team", "Experts", "Group"],
        "locations": ["Summit", "Highland", "Ridgeline", "Skyline", "Valley", "Creek", "Mountain"]
    },
    "Garage Door": {
        "prefixes": ["Reliable", "Premier", "Expert", "Quick Fix", "Precision", "Apex", "Prime",
                    "Skillful", "A+", "Speedy", "Dependable", "Custom", "Accessible", "Amazing",
                    "Professional", "Elite", "Superior"],
        "core": ["Garage Door", "Overhead Door", "Garage Door Repair", "Garage Door Services",
                "Gate and Door", "Garage Doors", "Door Services", "Door Installations",
                "Garage Door Care", "Door Solutions", "Garage Door Systems"],
        "suffixes": ["Services", "Masters", "Repairs", "Fixers", "Technicians", "Pros", "Solutions",
                    "Installations", "Care", "Specialists", "Experts", "Company"],
        "locations": ["City", "Metro", "Local", "Area", "Downtown", "District", "Central"]
    },
    "Sliding Doors": {
        "prefixes": ["Premier", "Elite", "Custom", "Precision", "Expert", "Professional", "Quality",
                    "Master", "Superior", "Advanced", "Modern", "Perfect", "Smooth", "Glide"],
        "core": ["Sliding Door", "Patio Door", "Glass Door", "Door Solutions", "Sliding Systems",
                "Door Services", "Sliding Door Repair", "Door Installation", "Sliding Glass",
                "Door Specialists"],
        "suffixes": ["Services", "Pros", "Solutions", "Repair", "Specialists", "Masters", "Experts",
                    "Installation", "Care", "Company", "Team"],
        "locations": ["City", "Metro", "Local", "Downtown", "Central", "District"]
    },
    "Towing Service": {
        "prefixes": ["Fast", "Quick", "Rapid", "Swift", "Express", "Metro", "City", "Reliable",
                    "Premier", "24/7", "Emergency", "Roadside", "Mobile", "All-City"],
        "core": ["Towing", "Tow Service", "Towing Service", "Roadside Assistance", "Auto Towing",
                "Towing & Recovery", "Tow Truck Service", "Vehicle Recovery", "Emergency Towing",
                "Tow Pros", "Towing Solutions"],
        "suffixes": ["Services", "Pros", "Masters", "Solutions", "Experts", "Company", "Near You",
                    "Near Me", "For You", "24/7", "Inc", "Team", "Group"],
        "locations": ["Downtown", "Metro", "City", "Central", "District", "Uptown", "Midtown",
                     "Riverside", "Lakeside", "Highway", "Interstate"]
    },
    "Air Duct Cleaning": {
        "prefixes": ["Fresh", "Clean", "Clear", "Pure", "Prime", "Apex", "Elite", "Master", "Pro",
                    "BreezeClear", "FreshFlow", "PureStream", "CleanVent", "AirPath", "ClearVent",
                    "FreshBreeze", "PureBreeze", "CleanAir", "AirMaster"],
        "core": ["Duct Cleaning", "Air Duct Services", "Duct & Dryer Clean", "Vent Cleaning",
                "HVAC Cleaning", "Air Duct Cleaning", "Ventilation Services", "Duct Solutions",
                "Airflow Services", "Duct Services", "Air Quality Services"],
        "suffixes": ["Services", "Solutions", "Cleaners", "Pros", "Specialists", "Experts",
                    "Near Me", "Near You", "Company", "Team", "Masters"],
        "locations": ["Metro", "City", "Local", "Area", "Central", "District"]
    }
}

def generate_business_name(service_type):
    """Generate a service-specific anonymous business name that hasn't been used before"""
    max_attempts = 1000  # Prevent infinite loop
    attempts = 0

    if service_type not in SERVICE_NAMES:
        service_type = "Locksmith"  # Default fallback

    service_data = SERVICE_NAMES[service_type]

    while attempts < max_attempts:
        # Randomly choose format with more variety:
        # Format 1: Prefix + Core (e.g., "Elite Locksmith")
        # Format 2: Prefix + Core + Suffix (e.g., "Elite Lock Services Pros")
        # Format 3: Core + Suffix (e.g., "Lock & Key Services")
        # Format 4: Location + Core (e.g., "Metro Towing")
        # Format 5: Location + Core + Suffix (e.g., "Metro Towing Services")
        # Format 6: Prefix + Location + Core (e.g., "Premier Downtown Locksmith")

        format_choice = random.randint(1, 6)

        if format_choice == 1:
            prefix = random.choice(service_data["prefixes"])
            core = random.choice(service_data["core"])
            name = f"{prefix} {core}"
        elif format_choice == 2:
            prefix = random.choice(service_data["prefixes"])
            core = random.choice(service_data["core"])
            suffix = random.choice(service_data["suffixes"])
            name = f"{prefix} {core} {suffix}"
        elif format_choice == 3:
            core = random.choice(service_data["core"])
            suffix = random.choice(service_data["suffixes"])
            name = f"{core} {suffix}"
        elif format_choice == 4:
            location = random.choice(service_data["locations"])
            core = random.choice(service_data["core"])
            name = f"{location} {core}"
        elif format_choice == 5:
            location = random.choice(service_data["locations"])
            core = random.choice(service_data["core"])
            suffix = random.choice(service_data["suffixes"])
            name = f"{location} {core} {suffix}"
        else:  # format_choice == 6
            prefix = random.choice(service_data["prefixes"])
            location = random.choice(service_data["locations"])
            core = random.choice(service_data["core"])
            name = f"{prefix} {location} {core}"

        # Check if this name has been used before
        if not db.is_business_name_used(name):
            return name

        attempts += 1

    # If all combinations are exhausted, add a numeric suffix
    prefix = random.choice(service_data["prefixes"])
    core = random.choice(service_data["core"])
    suffix = random.randint(100, 999)
    return f"{prefix} {core} {suffix}"

def reverse_geocode(lat, lon):
    """
    Use Nominatim reverse geocoding to get address from coordinates
    """
    try:
        # Nominatim API endpoint
        nominatim_url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            'format': 'json',
            'lat': lat,
            'lon': lon,
            'addressdetails': 1
        }
        headers = {
            'User-Agent': 'AppleMapsListingsMaker/1.0'  # Required by Nominatim usage policy
        }

        response = requests.get(nominatim_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if 'address' in data:
            addr = data['address']
            house_number = addr.get('house_number', str(random.randint(100, 9999)))
            road = addr.get('road') or addr.get('street') or addr.get('pedestrian') or 'Commercial Ave'
            return house_number, road

        # Fallback if no address found
        return str(random.randint(100, 9999)), "Commercial Ave"

    except Exception as e:
        print(f"Reverse geocoding failed: {str(e)}")
        # Return placeholder on error
        return str(random.randint(100, 9999)), "Commercial Ave"

def fetch_commercial_addresses(city, state, count):
    """
    Fetch commercial addresses from OpenStreetMap using Overpass API
    """
    # Overpass API endpoint
    overpass_url = "http://overpass-api.de/api/interpreter"

    # Build Overpass query to find commercial buildings, shops, offices
    # We'll search for various commercial amenities and shops
    overpass_query = f"""
    [out:json][timeout:60];
    area["name"="{city}"]["admin_level"="8"]["is_in:state"="{state}"]->.searchArea;
    (
      node["shop"](area.searchArea);
      node["office"](area.searchArea);
      node["amenity"~"restaurant|cafe|bank|pharmacy|clinic|hospital|dentist|veterinary|library|post_office|fuel"](area.searchArea);
      way["shop"](area.searchArea);
      way["office"](area.searchArea);
      way["amenity"~"restaurant|cafe|bank|pharmacy|clinic|hospital|dentist|veterinary|library|post_office|fuel"](area.searchArea);
    );
    out center {count * 3};
    """

    try:
        response = requests.post(overpass_url, data={'data': overpass_query}, timeout=60)
        response.raise_for_status()
        data = response.json()

        locations = []
        seen_coords = set()  # To avoid duplicates

        for element in data.get('elements', []):
            if len(locations) >= count:
                break

            # Get coordinates
            if 'lat' in element and 'lon' in element:
                lat = element['lat']
                lon = element['lon']
            elif 'center' in element:
                lat = element['center']['lat']
                lon = element['center']['lon']
            else:
                continue

            # Skip if we've seen these coordinates
            coord_key = f"{lat:.5f},{lon:.5f}"
            if coord_key in seen_coords:
                continue
            seen_coords.add(coord_key)

            # Get address information
            tags = element.get('tags', {})

            # Build address
            house_number = tags.get('addr:housenumber', '')
            street = tags.get('addr:street', '')
            city_name = tags.get('addr:city', city)
            state_name = tags.get('addr:state', state)
            postcode = tags.get('addr:postcode', '')

            # If we don't have street info, use reverse geocoding
            if not street:
                # Use Nominatim reverse geocoding to get real address
                house_number, street = reverse_geocode(lat, lon)
                # Add small delay to respect Nominatim usage policy (max 1 request/second)
                time.sleep(1.1)

            # Build full address
            if house_number and street:
                address = f"{house_number} {street}, {city_name}, {state_name} {postcode}".strip()
            elif street:
                address = f"{street}, {city_name}, {state_name} {postcode}".strip()
            else:
                address = f"{city_name}, {state_name} {postcode}".strip()

            locations.append({
                'lat': lat,
                'lon': lon,
                'address': address
            })

        return locations

    except Exception as e:
        print(f"Error fetching from Overpass API: {str(e)}")
        # Fallback: return mock data for demonstration
        return generate_fallback_addresses(city, state, count)

def generate_fallback_addresses(city, state, count):
    """Generate fallback addresses if API fails"""
    locations = []
    street_names = [
        "Main Street", "Oak Avenue", "Maple Drive", "Park Boulevard", "Washington Street",
        "Lincoln Avenue", "Jefferson Road", "Commerce Way", "Business Parkway", "Industrial Drive",
        "Market Street", "Broadway", "Center Street", "First Avenue", "Second Street"
    ]

    for i in range(count):
        street = random.choice(street_names)
        number = random.randint(100, 9999)
        zipcode = random.randint(10000, 99999)

        locations.append({
            'lat': 0,
            'lon': 0,
            'address': f"{number} {street}, {city}, {state} {zipcode}"
        })

    return locations

@app.route('/')
def index():
    """Serve the main dashboard page"""
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate_listings():
    """API endpoint to generate business listings with duplicate checking"""
    try:
        data = request.json
        phone_number = data.get('phone_number')
        city = data.get('city')
        state = data.get('state')
        service_type = data.get('service_type')
        count = int(data.get('count', 30))

        # Validate inputs
        if not all([phone_number, city, state, service_type]):
            return jsonify({'error': 'Missing required fields (phone, city, state, service)'}), 400

        # Validate service type
        if service_type not in SERVICE_NAMES:
            return jsonify({'error': f'Invalid service type. Must be one of: {", ".join(SERVICE_NAMES.keys())}'}), 400

        if count < 1 or count > 100:
            return jsonify({'error': 'Count must be between 1 and 100'}), 400

        # Fetch commercial addresses (request more than needed to account for duplicates)
        all_locations = fetch_commercial_addresses(city, state, count * 3)

        # Filter out addresses that have already been used
        unique_locations = []
        for location in all_locations:
            lat = location.get('lat', 0)
            lon = location.get('lon', 0)
            address = location.get('address', '')

            # Check if address has been used before
            if lat != 0 and lon != 0:
                if not db.is_address_used(lat, lon):
                    unique_locations.append(location)
            else:
                # For fallback addresses without coordinates, check by text
                if not db.is_address_used_by_text(address, city, state):
                    unique_locations.append(location)

            # Stop when we have enough unique locations
            if len(unique_locations) >= count:
                break

        # If we don't have enough unique locations, notify the user
        if len(unique_locations) < count:
            print(f"Warning: Only found {len(unique_locations)} unique addresses out of {count} requested")

        # Create a new run record in the database
        run_id = db.create_run(phone_number, city, state, service_type, count, len(unique_locations))

        # Generate listings with unique business names
        listings = []
        for i, location in enumerate(unique_locations[:count]):
            # Generate unique business name for the service type
            business_name = generate_business_name(service_type)

            listing = {
                'id': i + 1,
                'name': business_name,
                'address': location['address'],
                'phone': phone_number,
                'latitude': location.get('lat', 0),
                'longitude': location.get('lon', 0)
            }
            listings.append(listing)

            # Save to database
            db.add_business_name(business_name, run_id)
            db.add_address(
                location['address'],
                location.get('lat', 0),
                location.get('lon', 0),
                city,
                state,
                run_id
            )
            db.save_listing(
                run_id,
                business_name,
                location['address'],
                phone_number,
                location.get('lat', 0),
                location.get('lon', 0)
            )

        return jsonify({
            'success': True,
            'count': len(listings),
            'listings': listings,
            'run_id': run_id
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """API endpoint to get all previous runs"""
    try:
        runs = db.get_all_runs()
        return jsonify({
            'success': True,
            'runs': runs
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/<int:run_id>', methods=['GET'])
def get_run_details(run_id):
    """API endpoint to get detailed information about a specific run"""
    try:
        details = db.get_run_details(run_id)
        if not details:
            return jsonify({'error': 'Run not found'}), 404

        return jsonify({
            'success': True,
            'details': details
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """API endpoint to get overall statistics"""
    try:
        stats = db.get_statistics()
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear-history', methods=['POST'])
def clear_history():
    """API endpoint to clear all historical data (use with caution!)"""
    try:
        db.clear_all_data()
        return jsonify({
            'success': True,
            'message': 'All historical data has been cleared'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
