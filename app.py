from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import random
import time

app = Flask(__name__)
CORS(app)

# List of business name prefixes and suffixes for generating anonymous names
BUSINESS_PREFIXES = [
    "Summit", "Premier", "Elite", "Grand", "Royal", "Central", "Metro", "Urban",
    "Downtown", "Main Street", "City", "Capitol", "Plaza", "Gateway", "Harbor",
    "Riverside", "Parkway", "Highland", "Valley", "Coastal", "Mountain", "Sunrise",
    "Sunset", "Golden", "Silver", "Diamond", "Platinum", "Prime", "First Rate"
]

BUSINESS_TYPES = [
    "Services", "Solutions", "Group", "Associates", "Company", "Corporation",
    "Enterprises", "Partners", "Consulting", "Agency", "Center", "Hub", "Shop",
    "Store", "Outlet", "Market", "Emporium", "Gallery", "Studio", "Office",
    "Clinic", "Practice", "Firm", "Workshop", "Boutique", "Depot"
]

def generate_business_name():
    """Generate a random anonymous business name"""
    prefix = random.choice(BUSINESS_PREFIXES)
    business_type = random.choice(BUSINESS_TYPES)
    return f"{prefix} {business_type}"

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
    """API endpoint to generate business listings"""
    try:
        data = request.json
        phone_number = data.get('phone_number')
        city = data.get('city')
        state = data.get('state')
        count = int(data.get('count', 30))

        # Validate inputs
        if not all([phone_number, city, state]):
            return jsonify({'error': 'Missing required fields'}), 400

        if count < 1 or count > 100:
            return jsonify({'error': 'Count must be between 1 and 100'}), 400

        # Fetch commercial addresses
        locations = fetch_commercial_addresses(city, state, count)

        # Generate listings with anonymous business names
        listings = []
        for i, location in enumerate(locations[:count]):
            listings.append({
                'id': i + 1,
                'name': generate_business_name(),
                'address': location['address'],
                'phone': phone_number,
                'latitude': location.get('lat', 0),
                'longitude': location.get('lon', 0)
            })

        return jsonify({
            'success': True,
            'count': len(listings),
            'listings': listings
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
