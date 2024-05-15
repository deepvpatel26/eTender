from flask import Flask, render_template, url_for
import folium
import os
from pymongo import MongoClient
from webscrapping import *
import warnings
from config import tender_data, city_coordinates

# Define a filter function to ignore specific warnings
def ignore_warnings(message, category, filename, lineno, file=None, line=None):
    if "Permissions-Policy header" in str(message):
        return True
    return False

warnings.showwarning = ignore_warnings
warnings.simplefilter("ignore")
# Create a Flask app
app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('mongodb+srv://deepvpatel47:RwqVQSYMJ6sjLB85@etender.d0y4ftk.mongodb.net/')
db = client['Etender']  # Replace 'Etender' with your actual database name

@app.route('/')
# def index():
#     # Create a map centered around Gujarat
#     m = folium.Map(location=[22.2587, 71.1924], zoom_start=7)

#     # Add markers for each city with tender data
#     for city, tenders in tender_data.items():
#         tooltip_content = f"{city}<br>Open Tenders: {tenders['open']}<br>Closed Tenders: {tenders['closed']}"
#         popup_content = f"""
#             <div style="width: 100px;">
#                 <b>{city}</b><br>
#                 <a href="{url_for('city_details', city_name=city)}" style="text-decoration: none;">
#                     <button style="background-color: #4CAF50; /* Green */
#                                     border: none;
#                                     color: white;
#                                     padding: 1px 2px;
#                                     text-align: center;
#                                     text-decoration: none;
#                                     display: inline-block;
#                                     font-size: 10px;
#                                     margin: 4px 2px;
#                                     transition-duration: 0.4s;
#                                     cursor: pointer;
#                                     border-radius: 5px;
#                                     box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2), 0 6px 20px 0 rgba(0,0,0,0.19);">
#                         Detailed View
#                     </button>
#                 </a>
#             </div>
#             """
#         folium.Marker(
#             location=city_coordinates[city],
#             popup=popup_content,
#             tooltip=tooltip_content,  # Display city name, open, and closed tenders counts on hover
#             parse_html=True
#         ).add_to(m)

#     # Save the map as an HTML file in the static directory
#     map_html = os.path.join('static', 'map.html')
#     m.save(map_html)

#     # Pass the route to the map HTML file to the template
#     return render_template('index.html', map_html='static/map.html')
def index():
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
                        Detailed View
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

    # Pass the map HTML directly to the template
    map_html = m.get_root().render()
    
    return render_template('index.html', map_html=map_html)

@app.route('/city/<city_name>')
def city_details(city_name):
    # Retrieve city details based on the city name
    tender_details = tender_data.get(city_name, {})
    
    collection_name = city_name.lower()
    collection_name = 'E_tender_'+collection_name
    if collection_name in db.list_collection_names():
        print(f"Collection {collection_name} already exists.")
        collection_name = city_name.lower()
        collection_name = 'E_tender_'+collection_name
        collection = db[collection_name]
        data = list(collection.find())
    
    else:
        data= scrape_tender_data(city_name)
        store_to_mongo_new(data,city_name)
        # Retrieve data from MongoDB collection corresponding to the city
        collection = db[collection_name]
        data = list(collection.find())
        
    # Render the city details template with tender details and data from MongoDB
    open_tenders = len(data)
    
    # Render the city details template with tender details, data from MongoDB, and the number of open tenders
    return render_template('city_details.html', city_name=city_name, tender_details=tender_details, data=data, open_tenders=open_tenders)

@app.route('/city_latest/<city_name>')
def city_details_reloaded(city_name):
    # Retrieve city details based on the city name
    tender_details = tender_data.get(city_name, {})
    # keep the tender_details.closed as 0 
    tender_details['closed'] = 0
    collection_name = city_name.lower()
    collection_name = 'E_tender_'+collection_name
    data= scrape_tender_data(city_name)
    store_to_mongo_new(data,city_name)
    # Retrieve data from MongoDB collection corresponding to the city
    collection = db[collection_name]
    data = list(collection.find())
        
    # Render the city details template with tender details and data from MongoDB
    open_tenders = len(data)
    
    # Render the city details template with tender details, data from MongoDB, and the number of open tenders
    return render_template('city_details.html', city_name=city_name, tender_details=tender_details, data=data, open_tenders=open_tenders)

if __name__ == '__main__':
    app.run(debug=True)
