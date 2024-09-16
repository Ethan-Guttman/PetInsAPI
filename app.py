from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from config import Config
from dotenv import load_dotenv
import openai
from openai import OpenAI
import os
from flask_cors import CORS
import string

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)
app.config.from_object(Config)

CORS(app)

client = OpenAI(
    api_key=os.getenv('OPEN_API_KEY')
)

# Initialize MongoDB connection using Flask-PyMongo
mongo = PyMongo(app)
customerCollection = mongo.db.customers  # Use 'customers' collection
petCollection = mongo.db.pets

# Routes
@app.route('/api/customers', methods=['GET'])
def get_customers():
    customers = list(customerCollection.find({}, {'_id': 0}))  # Get all customers, hide MongoDB `_id`
    return jsonify(customers)

@app.route('/api/customers', methods=['POST'])
def create_customer():
    data = request.json
    result = customerCollection.insert_one({
        'First_Name': data['first_name'],
        'Last_Name': data['last_name'],
        'Date_of_birth': data['date_of_birth'],
        'Insurance_provider': data['insurance_provider'],
        'Policy_number': data['policy_number'],
        })
    #print(result.inserted_id)
    return jsonify({"message": "customer created!", "id": str(result.inserted_id)}), 201

@app.route('/api/customers/<name>', methods=['DELETE'])
def delete_customer(name):
    result = customerCollection.delete_one({'name': name})
    if result.deleted_count == 0:
        return jsonify({"error": "customer not found"}), 404
    return jsonify({"message": "customer deleted!"})


@app.route('/api/pets', methods=['GET'])
def get_pets():
    pets = list(petCollection.find({}, {'_id': 0}))  # Get all pets, hide MongoDB `_id`
    return jsonify(pets)

@app.route('/api/pets', methods=['POST'])
def create_pet():
    data = request.json
    petCollection.insert_one({
        'name': data['name'],
        'owner': data['owner'],
        'age': data['age'],
        'weight': data['weight'],
        })
    return jsonify({"message": "pet created!"}), 201

@app.route('/api/pets/<name>', methods=['DELETE'])
def delete_pet(name):
    result = petCollection.delete_one({'name': name})
    if result.deleted_count == 0:
        return jsonify({"error": "pet not found"}), 404
    return jsonify({"message": "pet deleted!"})

@app.route('/api/add', methods=['POST'])
def calculate_cost():
    try:
        # Parse the request body to get numbers
        data = request.json
        numbers = data.get('numbers', [])

        if not isinstance(numbers, list) or not all(isinstance(n, (int, float)) for n in numbers):
            return jsonify({"error": "Invalid input, 'numbers' should be a list of numbers"}), 400

        # Compute the sum of numbers
        total_sum = sum(numbers)

        # Check if sum exceeds the hard limit
        if total_sum > 200:
            return jsonify({"error": f"Sum exceeds the limit of {200}"}), 400

        # Ask ChatGPT to confirm the sum or provide additional processing
        prompt = f"The sum of the numbers {numbers} is {total_sum}. Please confirm this addition. Return only a number"
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use the appropriate GPT model
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ]
        )

        # Extract ChatGPT response
        answer = response['choices'][0]['text'].strip()

        # Return the result as JSON
        return jsonify({
            "numbers": numbers,
            "sum": total_sum,
            "chatgpt_confirmation": answer
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
