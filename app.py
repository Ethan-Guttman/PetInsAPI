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
        'first_name': data['first_name'],
        'last_name': data['last_name'],
        'date_of_birth': data['date_of_birth'],
        'insurance_provider': data['insurance_provider'],
        'policy_number': data['policy_number'],
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

@app.route('/api/calculatecost', methods=['POST'])
def calculate_cost():
    try:
        data = request.json
        
        prompt = "<cost settings>Checkups are $10, vaccinations $20, blood tests $30, oral health exams $40 and orthopedic surgeries are $50. "
        prompt += "All insurance providers have a deductible of $10 except for united healthcare having one of $30. All providers will refuse to pay for pets above 12 years old </cost settings>"
        prompt += f"You are an insurance adjuster. Given the following information about the pet, the treatment and the customers provider, please give a cost minus the reimbursed amount. Please confirm this addition. Return only a number"
        prompt += f"<provider>{data['provider']}</provider><treatment>{data['treatment']}</treatment><age>{data['age']}</age>"

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ]
        )

        answer = response.choices[0].message.content

        return jsonify({
            "chatgpt_confirmation": answer
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
