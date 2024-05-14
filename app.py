from flask import Flask, render_template
from pymongo import MongoClient

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('mongodb+srv://deepvpatel47:RwqVQSYMJ6sjLB85@etender.d0y4ftk.mongodb.net/')
db = client['Etender']  # Replace 'Etender' with your actual database name

@app.route('/')
def index():
    # Get list of collection names from MongoDB
    collection_names = db.list_collection_names()
    return render_template('index.html', collection_names=collection_names)

@app.route('/collection/<collection_name>')
def display_collection(collection_name):
    # Retrieve data from selected collection
    collection = db[collection_name]
    data = list(collection.find())
    return render_template('collection.html', collection_name=collection_name, data=data)

if __name__ == '__main__':
    app.run(debug=True)
