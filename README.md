# Apple Maps Listings Generator

A web application that generates commercial business listings with real addresses for surveys and data analysis purposes. The system features a modern dashboard interface where users can input parameters and receive anonymous business listings with real commercial addresses from OpenStreetMap.

## Features

- **Modern Web Dashboard**: Clean, responsive UI with real-time progress tracking
- **Real Commercial Addresses**: Fetches actual commercial locations from OpenStreetMap
- **Anonymous Business Names**: Generates realistic but anonymous business names
- **Bulk Generation**: Create up to 100 listings at once
- **CSV Export**: Download results as CSV for easy data analysis
- **Progress Tracking**: Visual feedback during listing generation
- **Statistics Display**: View summary statistics of generated listings
- **Duplicate Prevention**: Automatic tracking to ensure no business names or addresses are repeated across runs
- **Run History**: View all previous generation runs with complete details
- **Persistent Database**: SQLite database stores all historical data across sessions

## How It Works

1. User inputs:
   - Phone number (will be applied to all listings)
   - City name
   - State name
   - Number of locations needed

2. System processes:
   - Queries OpenStreetMap Overpass API for commercial locations
   - Retrieves real commercial addresses (shops, offices, restaurants, etc.)
   - **Checks database for duplicate addresses** and filters them out
   - Generates unique anonymous business names that haven't been used before
   - **Saves all data to persistent database** for future duplicate checking
   - Combines data with provided phone number

3. Output:
   - Table view of all listings
   - Each listing includes: ID, Business Name, Address, Phone Number
   - Download as CSV file
   - **All data stored in history for tracking**

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. Clone the repository:
```bash
git clone <repository-url>
cd Apple-Maps-Listings-Maker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

1. **View Database Statistics** (top of page):
   - See total runs, unique business names, unique addresses
   - Monitor how many listings have been generated historically
   - Access "View History" to see all previous runs
   - Use "Clear All Data" to reset the database (careful!)

2. **Fill in the form**:
   - Enter a phone number (e.g., +1 (555) 123-4567)
   - Enter city name (e.g., New York)
   - Enter state name (e.g., New York)
   - Specify number of locations (1-100)

3. **Click "Generate Listings"**:
   - System automatically checks for duplicate names/addresses
   - Watch the progress bar as the system works
   - Results will appear automatically when ready
   - Statistics update in real-time

4. **View Results**:
   - See statistics summary at the top
   - Browse listings in the table
   - Click "Download CSV" to export data
   - All listings are saved to history automatically

5. **View History** (optional):
   - Click "View History" button to see all previous runs
   - Each run shows timestamp, location, counts, and phone number
   - Use this to track your generation history

## Technical Details

### Backend (app.py)
- **Framework**: Flask
- **API**: OpenStreetMap Overpass API
- **Database**: SQLite with contextual connections
- **Features**:
  - Commercial address fetching
  - Anonymous name generation with uniqueness checking
  - Duplicate prevention for addresses and names
  - Fallback data for API failures
  - CORS enabled for development
  - Complete run history tracking

### Database (database.py)
- **Storage**: SQLite (listings_history.db)
- **Tables**:
  - `runs`: Tracks each generation session
  - `used_business_names`: All unique business names ever generated
  - `used_addresses`: All unique addresses ever used (with coordinates)
  - `generated_listings`: Complete history of all listings
- **Indexes**: Optimized for fast duplicate checking

### Frontend (templates/index.html)
- **Tech**: HTML5, CSS3, Vanilla JavaScript
- **Features**:
  - Responsive design
  - Real-time progress tracking
  - Interactive table display
  - CSV export functionality

### Data Sources
- **OpenStreetMap**: Free, open-source map data
- **Overpass API**: Query service for OSM data
- No API key required

## Duplicate Prevention System

The application maintains a persistent SQLite database that tracks:

1. **Business Names**: Every generated name is checked against the database before use
   - 600+ possible unique combinations (26 prefixes × 24 types)
   - If all combinations exhausted, adds numeric suffix
   - Guarantees no duplicate names across all runs

2. **Commercial Addresses**: Every address is verified for uniqueness
   - Tracks by latitude/longitude coordinates
   - Also tracks by full address text as fallback
   - Automatically filters out previously used locations

3. **Run History**: Complete audit trail of all generations
   - Timestamp of each run
   - Input parameters (phone, city, state, count)
   - All listings generated in each run
   - Viewable through the dashboard

## API Endpoints

### POST /api/generate
Generates business listings with duplicate checking.

**Request Body**:
```json
{
  "phone_number": "+1 (555) 123-4567",
  "city": "New York",
  "state": "New York",
  "count": 30
}
```

**Response**:
```json
{
  "success": true,
  "count": 30,
  "run_id": 5,
  "listings": [
    {
      "id": 1,
      "name": "Summit Services",
      "address": "123 Main Street, New York, New York 10001",
      "phone": "+1 (555) 123-4567",
      "latitude": 40.7128,
      "longitude": -74.0060
    }
  ]
}
```

### GET /api/statistics
Returns overall database statistics.

**Response**:
```json
{
  "success": true,
  "statistics": {
    "total_runs": 15,
    "total_unique_business_names": 450,
    "total_unique_addresses": 450,
    "total_listings_generated": 450
  }
}
```

### GET /api/history
Returns all previous generation runs.

**Response**:
```json
{
  "success": true,
  "runs": [
    {
      "id": 1,
      "timestamp": "2025-11-17 10:30:00",
      "phone_number": "+1 (555) 123-4567",
      "city": "New York",
      "state": "New York",
      "requested_count": 30,
      "generated_count": 30
    }
  ]
}
```

### GET /api/history/{run_id}
Returns detailed information about a specific run.

### POST /api/clear-history
Clears all historical data from the database (use with caution!).

## Use Cases

- Business surveys and market research
- Testing and development
- Data analysis projects
- Educational purposes
- Geographic data studies

## Important Notes

- This tool is for legitimate business surveys and data analysis only
- Generated business names are anonymous and fictional
- Addresses are real commercial locations from OpenStreetMap
- Respects OpenStreetMap usage policies
- Rate limiting applies to Overpass API (60 second timeout)

## Troubleshooting

**Issue**: No addresses returned
- **Solution**: Try a larger city or verify city/state spelling

**Issue**: API timeout
- **Solution**: Reduce number of locations or try again later

**Issue**: Port 5000 already in use
- **Solution**: Change port in app.py: `app.run(port=5001)`

## License

This project is for educational and research purposes.

## Contributing

Contributions are welcome! Please ensure any changes maintain the ethical use guidelines.

## Disclaimer

This tool generates data for surveys and analysis purposes. Users are responsible for ensuring their use complies with local regulations and terms of service of any platforms where data may be used.