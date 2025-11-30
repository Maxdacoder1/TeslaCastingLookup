# Tesla Casting Lookup

A web application for querying, browsing, and searching casting information for Tesla vehicle parts. This tool provides both a REST API backend (powered by FastAPI) and a user-friendly web interface (powered by Flask) to access detailed information about Tesla castings from various models including Model Y, Cybertruck, Model S, and more.

## Features

- **Casting Lookup**: Search for specific castings by unique ID to retrieve detailed information including applicable years, configurations, and materials.
- **Browse All Castings**: Paginated view of all available castings with basic details and navigation.
- **Full-Text Search**: Search across multiple fields (ID, description, years, comments) for comprehensive results.
- **Export Functionality**: Download individual casting data as JSON files for external analysis or record-keeping.
- **Responsive Web UI**: Clean, Bootstrap-powered interface that works on desktop and mobile devices.

## Data Source

The application uses casting data from Tesla's vehicle platforms, including:
- Model Y and Model 3 megacastings
- Cybertruck exoskeleton components
- Model S/X Plaid structural parts
- Tesla Semi and Robotaxi prototypes
- Battery and energy product enclosures

Data is stored in an SQLite database populated from a CSV source.

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Maxdacoder1/TeslaCastingLookup.git
   cd TeslaCastingLookup
   ```

2. **Set up virtual environment** (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database**:
   ```bash
   python src/db_setup.py
   ```
   This will create `castings.db` and populate it with data from `data/tesla_castings.csv`.

## Usage

### Running the Application

1. **Start the FastAPI backend** (provides API endpoints):
   ```bash
   uvicorn src.main:app --reload
   ```
   - Backend will run on `http://localhost:8000`
   - API documentation available at `http://localhost:8000/docs`

2. **Start the Flask web app** (provides web interface):
   ```bash
   python src/web_app.py
   ```
   - Web interface available at `http://localhost:5000`

3. **Access the application**:
   - Open `http://localhost:5000` in your browser
   - Use the lookup form, browse pages, or search functionality

### API Endpoints

- `GET /lookup/{casting}`: Retrieve details for a specific casting ID
- `GET /castings?page={page}&limit={limit}`: Get paginated list of all castings (default limit: 50, max: 100)
- `GET /search?q={query}`: Search castings across all text fields

Example API usage:
```bash
curl http://localhost:8000/lookup/682B20C75BBD
```

## Project Structure

```
TeslaCastingLookup/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── tesla_castings.csv  # Source CSV data
│   └── teslamotors.png     # Tesla logo
├── src/
│   ├── main.py             # FastAPI backend application
│   ├── web_app.py          # Flask web interface
│   └── db_setup.py         # Database setup script
├── static/
│   └── styles.css          # Custom CSS styles
├── templates/
│   ├── index.html          # Lookup page template
│   ├── browse.html         # Browse page template
│   └── search.html         # Search page template
└── castings.db             # Generated SQLite database (not in version control)
```

## Development

- Source code is organized in the `src/` directory for better project structure.
- Database can be reset by re-running `python src/db_setup.py`.
- CSS and HTML templates can be modified in `static/` and `templates/` respectively.

## Contributing

Contributions are welcome! Please submit issues or pull requests on GitHub.

## License

This project is provided as-is for educational and research purposes. Tesla trademarks and data copyrights apply.

## Disclaimer

This application and associated data is for informational purposes only. Tesla casting information may change and should not be used for manufacturing or critical applications without verification.
