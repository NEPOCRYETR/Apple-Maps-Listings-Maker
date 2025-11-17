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

## How It Works

1. User inputs:
   - Phone number (will be applied to all listings)
   - City name
   - State name
   - Number of locations needed

2. System processes:
   - Queries OpenStreetMap Overpass API for commercial locations
   - Retrieves real commercial addresses (shops, offices, restaurants, etc.)
   - Generates anonymous business names for each location
   - Combines data with provided phone number

3. Output:
   - Table view of all listings
   - Each listing includes: ID, Business Name, Address, Phone Number
   - Download as CSV file

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

1. **Fill in the form**:
   - Enter a phone number (e.g., +1 (555) 123-4567)
   - Enter city name (e.g., New York)
   - Enter state name (e.g., New York)
   - Specify number of locations (1-100)

2. **Click "Generate Listings"**:
   - Watch the progress bar as the system works
   - Results will appear automatically when ready

3. **View Results**:
   - See statistics summary at the top
   - Browse listings in the table
   - Click "Download CSV" to export data

## Technical Details

### Backend (app.py)
- **Framework**: Flask
- **API**: OpenStreetMap Overpass API
- **Features**:
  - Commercial address fetching
  - Anonymous name generation
  - Fallback data for API failures
  - CORS enabled for development

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

## API Endpoints

### POST /api/generate
Generates business listings based on input parameters.

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