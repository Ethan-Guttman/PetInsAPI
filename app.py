from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize MongoDB connection using Flask-PyMongo
mongo = PyMongo(app)
collection = mongo.db.items  # Use 'items' collection

# Routes
@app.route('/api/items', methods=['GET'])
def get_items():
    items = list(collection.find({}, {'_id': 0}))  # Get all items, hide MongoDB `_id`
    return jsonify(items)

@app.route('/api/items', methods=['POST'])
def create_item():
    data = request.json
    collection.insert_one({'name': data['name']})
    return jsonify({"message": "Item created!"}), 201

@app.route('/api/items/<name>', methods=['DELETE'])
def delete_item(name):
    result = collection.delete_one({'name': name})
    if result.deleted_count == 0:
        return jsonify({"error": "Item not found"}), 404
    return jsonify({"message": "Item deleted!"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
