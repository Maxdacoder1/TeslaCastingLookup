from flask import Flask, request, render_template
import requests

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        casting = request.form.get('casting')
        if not casting:
            error = "Please enter a casting number"
            return render_template('index.html', error=error)

        try:
            response = requests.get(f'http://localhost:8000/lookup/{casting.strip()}', timeout=5)
            if response.status_code == 200:
                data = response.json()
                return render_template('index.html', data=data)
            elif response.status_code == 404:
                error = "Casting not found"
                return render_template('index.html', error=error)
            else:
                try:
                    error_data = response.json()
                    error = error_data.get('detail', f'API Error: {response.status_code}')
                except:
                    error = f'API Error: {response.status_code}'
                return render_template('index.html', error=error)
        except requests.exceptions.RequestException as e:
            error = f"Unable to connect to API: {str(e)}"
            return render_template('index.html', error=error)
    return render_template('index.html')

@app.route('/browse')
def browse():
    try:
        page = request.args.get('page', 1, type=int)
        limit = 20  # items per page
        response = requests.get(f'http://localhost:8000/castings?page={page}&limit={limit}', timeout=10)
        if response.status_code == 200:
            data = response.json()
            return render_template('browse.html', **data)
        else:
            error = f"API Error: {response.status_code}"
            return render_template('browse.html', error=error)
    except requests.exceptions.RequestException as e:
        error = f"Unable to connect to API: {str(e)}"
        return render_template('browse.html', error=error)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form.get('query')
        if query:
            try:
                response = requests.get(f'http://localhost:8000/search?q={query}', timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    return render_template('search.html', query=query, **data)
                else:
                    error = f"API Error: {response.status_code}"
                    return render_template('search.html', error=error, query=query)
            except requests.exceptions.RequestException as e:
                error = f"Unable to connect to API: {str(e)}"
                return render_template('search.html', error=error)
    return render_template('search.html')

@app.route('/export/<casting>')
def export(casting):
    try:
        response = requests.get(f'http://localhost:8000/lookup/{casting}', timeout=5)
        if response.status_code == 200:
            data = response.json()
            from flask import jsonify, make_response
            export_response = make_response(jsonify(data))
            export_response.headers['Content-Disposition'] = f'attachment; filename=tesla_casting_{casting}.json'
            export_response.headers['Content-type'] = 'application/json'
            return export_response
        else:
            return f"Error: Casting not found", 404
    except requests.exceptions.RequestException:
        return f"Error: Unable to fetch data", 500

if __name__ == '__main__':
    app.run(debug=True)
