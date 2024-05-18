from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
import folium
import os
import warnings
from pymongo import MongoClient
from webscrapping import scrape_tender_data, store_to_mongo_new
from config import tender_data, city_coordinates
import json
from geopy.geocoders import Nominatim
from flask_bcrypt import Bcrypt
from functools import wraps

# Initialize Nominatim API
geolocator = Nominatim(user_agent="openstreetmap.org")

# Define a filter function to ignore specific warnings
def ignore_warnings(message, category, filename, lineno, file=None, line=None):
    if "Permissions-Policy header" in str(message):
        return True
    return False

warnings.showwarning = ignore_warnings
warnings.simplefilter("ignore")

# Create a Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key
bcrypt = Bcrypt(app)

# Connect to MongoDB
client = MongoClient('mongodb+srv://deepvpatel47:RwqVQSYMJ6sjLB85@etender.d0y4ftk.mongodb.net/')
db = client['Etender']  # Replace 'Etender' with your actual database name

# Load cities from JSON file
def load_cities():
    with open('cities.json') as f:
        return json.load(f)

# Save cities to JSON file
def save_cities(cities):
    with open('cities.json', 'w') as f:
        json.dump(cities, f, indent=4)

# Fetch latitude and longitude using geopy
def get_city_coordinates(city_name):
    location = geolocator.geocode(city_name)
    if location:
        return [location.latitude, location.longitude]
    return None

# Decorator to check if user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('index'))
    return redirect(url_for('login'))

@app.route('/index')
@login_required
def index():
    cities_data = load_cities()
    # Create a map centered around Gujarat
    m = folium.Map(location=[22.2587, 71.1924], zoom_start=7)

    # Add markers for each city with coordinates
    for city, tenders in tender_data.items():
        # Create HTML content for the popup
        popup_content = f"""
            <div style="width: 200px;">
                <h3>{city} Tender Details</h3>
                <p>Open Tenders: {tenders['open']}</p>
                <p>Closed Tenders: {tenders['closed']}</p>
                <a href="{url_for('city_details', city_name=city)}" style="text-decoration: none;">
                    <button style="background-color: #4CAF50; 
                                    border: none;
                                    color: white;
                                    padding: 5px 10px;
                                    text-align: center;
                                    text-decoration: none;
                                    display: inline-block;
                                    font-size: 14px;
                                    cursor: pointer;
                                    border-radius: 5px;">
                        View ALL Tenders
                    </button>
                </a>
            </div>
        """
        # Add markers with popup content
        folium.Marker(
            location=city_coordinates[city],
            popup=folium.Popup(popup_content, max_width=250),
            icon=folium.Icon(color='green', icon='info-sign')
        ).add_to(m)
    return render_template('index.html', cities=json.dumps(cities_data['cities']))

@app.route('/add_city', methods=['POST'])
def add_city():
    data = request.get_json()
    city_name = data.get('city')
    print(city_name)
    if not city_name:
        return jsonify({"success": False, "error": "City name is required"}), 400

    # Fetch latitude and longitude
    city_coords = get_city_coordinates(city_name)
    print(city_coords)
    if not city_coords:
        return jsonify({"success": False, "error": "Could not find coordinates for the city"}), 400
    try:
        cities_data = load_cities()
        cities_data['cities'][city_name] = city_coords
        save_cities(cities_data)
        # city_details(city_name)
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/city/<city_name>')
@login_required
def city_details(city_name):
    tender_details = tender_data.get(city_name, {'closed': 0})
    collection_name = f'E_tender_{city_name.lower()}'

    if collection_name in db.list_collection_names():
        collection = db[collection_name]
        data = list(collection.find())
    else:
        data = scrape_tender_data(city_name)
        store_to_mongo_new(data, city_name)
        collection = db[collection_name]
        data = list(collection.find())

    open_tenders = len(data)
    return render_template('city_details.html', city_name=city_name, tender_details=tender_details, data=data, open_tenders=open_tenders)

@app.route('/city_latest/<city_name>', methods=['GET', 'POST'])
@login_required
def city_details_reloaded(city_name):
    if request.method == 'POST':
        tender_details = tender_data.get(city_name, {'closed': 0})
        collection_name = f'E_tender_{city_name.lower()}'

        # Scrape new tender data
        new_data = scrape_tender_data(city_name)

        # Check if new records are added
        if not new_data.empty:
            # Store new data in the database
            store_to_mongo_new(new_data, city_name)
            # Fetch all data from the database
            collection = db[collection_name]
            data = list(collection.find())
            open_tenders = len(data)
            return render_template('city_details.html', city_name=city_name, tender_details=tender_details, data=data, open_tenders=open_tenders)
        else:
            # No new records found
            return "No new records to insert"
    else:
        # Handle GET request
        tender_details = tender_data.get(city_name, {'closed': 0})
        collection_name = f'E_tender_{city_name.lower()}'

        # Fetch all data from the database
        collection = db[collection_name]
        data = list(collection.find())
        open_tenders = len(data)

        return render_template('city_details.html', city_name=city_name, tender_details=tender_details, data=data, open_tenders=open_tenders)

@app.route('/download_pdf', methods=['GET'])
def download_pdf():
    city_name = request.args.get('city')
    tender_id = request.args.get('id')
    print(city_name, tender_id)
    # Process the city_name and tender_id as needed

    return render_template('download_pdf.html', city_name=city_name, tender_id=tender_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db['User_details'].find_one({'username': username})
        if user and bcrypt.check_password_hash(user['password'], password):
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = {'username': username, 'password': hashed_password}
        db['User_details'].insert_one(user)
        flash('Account created successfully! Please log in.')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
