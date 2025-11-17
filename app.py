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
        "prefixes": ["24/7", "Emergency", "Quick", "Reliable", "Master", "Professional", "Expert",
                    "Secure", "Swift", "Premier", "Elite", "Trusted", "Advanced", "Precision"],
        "core": ["Lock & Key", "Locksmith", "Security", "Lock Services", "Key Services",
                "Lock Solutions", "Security Systems", "Lock & Security"],
        "suffixes": ["Pros", "Experts", "Services", "Solutions", "Specialists", "Team",
                    "Company", "Group", "Associates", "Co"]
    },
    "Chimney Cleaning": {
        "prefixes": ["Professional", "Master", "Expert", "Premier", "Elite", "Certified",
                    "Quality", "Top", "Superior", "Advanced", "Reliable", "Trusted"],
        "core": ["Chimney Sweep", "Chimney Cleaning", "Chimney Services", "Chimney Care",
                "Fireplace & Chimney", "Chimney Maintenance", "Chimney Solutions"],
        "suffixes": ["Pros", "Experts", "Services", "Specialists", "Company", "Team",
                    "Solutions", "Group", "Associates", "Co"]
    },
    "Garage Door": {
        "prefixes": ["24/7", "Emergency", "Quick", "Reliable", "Professional", "Expert",
                    "Premier", "Elite", "Precision", "Quality", "Superior", "Advanced"],
        "core": ["Garage Door", "Garage Door Repair", "Garage Door Services", "Door Solutions",
                "Overhead Door", "Garage Door Systems", "Door & Opener"],
        "suffixes": ["Pros", "Experts", "Services", "Repair", "Solutions", "Specialists",
                    "Company", "Team", "Group", "Co"]
    },
    "Sliding Doors": {
        "prefixes": ["Professional", "Expert", "Premier", "Elite", "Quality", "Precision",
                    "Custom", "Modern", "Superior", "Advanced", "Reliable", "Master"],
        "core": ["Sliding Door", "Patio Door", "Glass Door", "Sliding Door Repair",
                "Door Solutions", "Sliding Door Services", "Door Systems"],
        "suffixes": ["Pros", "Experts", "Services", "Repair", "Solutions", "Specialists",
                    "Company", "Team", "Group", "Co"]
    },
    "Towing Service": {
        "prefixes": ["24/7", "Emergency", "Fast", "Quick", "Reliable", "Rapid", "Express",
                    "Premier", "Professional", "Roadside", "Mobile", "Swift"],
        "core": ["Towing", "Tow Service", "Auto Towing", "Vehicle Towing", "Roadside Assistance",
                "Towing & Recovery", "Tow Truck Service"],
        "suffixes": ["Pros", "Services", "Company", "Solutions", "Team", "Group",
                    "Specialists", "Experts", "Co", "Inc"]
    },
    "Air Duct Cleaning": {
        "prefixes": ["Professional", "Expert", "Premier", "Elite", "Quality", "Certified",
                    "Advanced", "Superior", "Clean", "Fresh", "Pure", "Healthy"],
        "core": ["Air Duct Cleaning", "Duct Cleaning", "HVAC Cleaning", "Air Quality",
                "Vent Cleaning", "Duct Services", "Indoor Air Solutions"],
        "suffixes": ["Pros", "Experts", "Services", "Specialists", "Solutions", "Company",
                    "Team", "Group", "Associates", "Co"]
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
        # Randomly choose format:
        # Format 1: Prefix + Core (e.g., "24/7 Locksmith")
        # Format 2: Prefix + Core + Suffix (e.g., "24/7 Lock Services Pros")
        # Format 3: Core + Suffix (e.g., "Lock & Key Services")

        format_choice = random.randint(1, 3)

        if format_choice == 1:
            prefix = random.choice(service_data["prefixes"])
            core = random.choice(service_data["core"])
            name = f"{prefix} {core}"
        elif format_choice == 2:
            prefix = random.choice(service_data["prefixes"])
            core = random.choice(service_data["core"])
            suffix = random.choice(service_data["suffixes"])
            name = f"{prefix} {core} {suffix}"
        else:
            core = random.choice(service_data["core"])
            suffix = random.choice(service_data["suffixes"])
            name = f"{core} {suffix}"

        # Check if this name has been used before
        if not db.is_business_name_used(name):
            return name

        attempts += 1

    # If all combinations are exhausted, add a numeric suffix
    prefix = random.choice(service_data["prefixes"])
    core = random.choice(service_data["core"])
    suffix = random.randint(100, 999)
    return f"{prefix} {core} {suffix}"

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
                # For demo purposes, generate a placeholder
                # In production, you'd use Nominatim reverse geocoding
                street = f"Commercial Ave"
                house_number = str(random.randint(100, 9999))

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
