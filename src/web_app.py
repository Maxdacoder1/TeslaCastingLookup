"""
Tesla Casting Web Application

This Flask application provides a modern web interface for querying Tesla casting data
through a FastAPI backend. Features include casting lookup, browsing, searching, and
exporting functionality with a responsive Bootstrap UI.

The application communicates with the FastAPI server running on localhost:8000
to retrieve casting information from an SQLite database.
"""

from flask import Flask, request, render_template, jsonify, make_response, send_from_directory
import requests

# Initialize Flask application instance
app = Flask(__name__)

# Configure Flask to serve files from data directory (for TESLA logo)
app.config['ROOT_PATH'] = 'data'

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Main route for casting lookup functionality.

    GET: Displays the search form
    POST: Processes casting lookup request and displays results

    Returns:
        Renders index.html template with optional data or error information
    """
    # Handle POST request with form submission
    if request.method == 'POST':
        # Get the casting number from form data and validate it's not empty
        casting = request.form.get('casting')
        if not casting:
            error = "Please enter a casting number"
            return render_template('index.html', error=error)

        # Attempt to fetch casting data from the API
        try:
            response = requests.get(f'http://localhost:8000/lookup/{casting.strip()}', timeout=5)
            if response.status_code == 200:
                # Success: parse JSON data and render with results
                data = response.json()
                return render_template('index.html', data=data)
            elif response.status_code == 404:
                # Casting not found in database
                error = "Casting not found"
                return render_template('index.html', error=error)
            else:
                # Other API errors - try to extract detailed error message
                try:
                    error_data = response.json()
                    error = error_data.get('detail', f'API Error: {response.status_code}')
                except:
                    error = f'API Error: {response.status_code}'
                return render_template('index.html', error=error)
        except requests.exceptions.RequestException as e:
            # Handle connection timeouts, network errors, etc.
            error = f"Unable to connect to API: {str(e)}"
            return render_template('index.html', error=error)

    # GET request - display empty form
    return render_template('index.html')

@app.route('/browse')
def browse():
    """
    Browse route for paginated viewing of all castings.

    Retrieves a page of castings from the API and displays them in a table
    with pagination controls. Each casting shows basic info with links to
    detailed view.

    Query Parameters:
        page (int): Page number to display (defaults to 1)

    Returns:
        Renders browse.html template with casting list and pagination data
    """
    try:
        # Get page number from URL parameters, default to 1
        page = request.args.get('page', 1, type=int)
        limit = 20  # items per page for readability

        # Fetch paginated casting data from API
        response = requests.get(f'http://localhost:8000/castings?page={page}&limit={limit}', timeout=10)

        if response.status_code == 200:
            data = response.json()
            # Unpack API data (castings, total, page, limit, total_pages) into template
            return render_template('browse.html', **data)
        else:
            error = f"API Error: {response.status_code}"
            return render_template('browse.html', error=error)
    except requests.exceptions.RequestException as e:
        # Handle network/API connection errors
        error = f"Unable to connect to API: {str(e)}"
        return render_template('browse.html', error=error)

@app.route('/search', methods=['GET', 'POST'])
def search():
    """
    Search route for full-text search across casting data.

    GET: Displays the search form
    POST: Processes search query and displays matching results

    Form Data:
        query (str): Search term to match against casting fields

    Returns:
        Renders search.html template with search results or error information
    """
    # Handle search form submission
    if request.method == 'POST':
        query = request.form.get('query')
        if query:
            try:
                # Call API search endpoint with user query
                response = requests.get(f'http://localhost:8000/search?q={query}', timeout=10)

                if response.status_code == 200:
                    # Success: unpack API response (results, query, count) into template
                    data = response.json()
                    return render_template('search.html', **data)
                else:
                    error = f"API Error: {response.status_code}"
                    return render_template('search.html', error=error, query=query)
            except requests.exceptions.RequestException as e:
                # Handle connection/network errors gracefully
                error = f"Unable to connect to API: {str(e)}"
                return render_template('search.html', error=error, query=query)

    # GET request - display empty search form
    return render_template('search.html')

@app.route('/export/<casting>')
def export(casting):
    """
    Export route to download individual casting data as JSON.

    Fetches casting details from the API and returns them as a downloadable
    JSON file attachment. Useful for data analysis or record keeping.

    Path Parameters:
        casting (str): Casting ID to export

    Returns:
        JSON file download response, or error message for not found/invalid requests
    """
    try:
        # Fetch casting data from main lookup API
        response = requests.get(f'http://localhost:8000/lookup/{casting}', timeout=5)

        if response.status_code == 200:
            data = response.json()

            # Create HTTP response with JSON content and download headers
            # Note: Local imports here to avoid circular imports in module
            from flask import jsonify, make_response
            export_response = make_response(jsonify(data))
            export_response.headers['Content-Disposition'] = f'attachment; filename=tesla_casting_{casting}.json'
            export_response.headers['Content-type'] = 'application/json'
            return export_response
        else:
            # Casting not found - return plain text error
            return f"Error: Casting not found", 404
    except requests.exceptions.RequestException:
        # Network/API errors during export
        return f"Error: Unable to fetch data", 500

@app.route('/teslamotors.png')
def serve_tesla_logo():
    """
    Serve the Tesla Motors logo image from project root.

    Required for displaying the logo in the sidebar on desktop views.
    """
    return send_from_directory('.', 'teslamotors.png')

if __name__ == '__main__':
    app.run(debug=True)
