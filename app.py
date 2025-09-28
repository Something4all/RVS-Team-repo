# app.py (Flask Backend)
from flask import Flask, request, jsonify, render_template
import datetime
import uuid
import re # For basic NLP simulation

app = Flask(__name__)

# --- In-memory Datastores (replace with a proper database like PostgreSQL/MongoDB) ---
needs = [] # Stores reported needs
resources = [] # Stores available resources (volunteers, supplies, etc.)
users = {} # Stores user information (simplified)

# --- Helper Functions ---
def get_timestamp():
    return datetime.datetime.now().isoformat()

def simple_nlp_priority(message):
    message_lower = message.lower()
    if "medical" in message_lower or "injured" in message_lower or "pain" in message_lower:
        return "Critical - Medical"
    if "shelter" in message_lower or "home" in message_lower or "roof" in message_lower:
        return "High - Shelter"
    if "food" in message_lower or "eat" in message_lower or "hungry" in message_lower:
        return "High - Food"
    if "water" in message_lower or "drink" in message_lower or "thirsty" in message_lower:
        return "High - Water"
    return "Medium - General"

def match_need_to_resource(need):
    # This is a very basic matching algorithm
    # In a real system, this would involve geospatial proximity, skill matching, capacity, etc.
    for resource in resources:
        if resource['type'] == 'volunteer' and need['priority'] != 'Medium - General':
            return resource # Found a generic volunteer for a non-general need
        if 'medical' in need['priority'].lower() and resource['type'] == 'medical_volunteer':
            return resource
    return None

# --- API Endpoints ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/report_need', methods=['POST'])
def report_need():
    data = request.json
    if not data or not all(k in data for k in ['reporter_id', 'message', 'location']):
        return jsonify({"error": "Missing data"}), 400

    need_id = str(uuid.uuid4())
    priority = simple_nlp_priority(data['message'])

    new_need = {
        "id": need_id,
        "reporter_id": data['reporter_id'],
        "message": data['message'],
        "location": data['location'], # e.g., {"lat": 34.0522, "lon": -118.2437}
        "priority": priority,
        "status": "reported",
        "timestamp": get_timestamp()
    }
    needs.append(new_need)
    print(f"New Need Reported: {new_need}")

    # Simulate immediate matching attempt
    matched_resource = match_need_to_resource(new_need)
    if matched_resource:
        new_need['status'] = 'matched'
        # In a real app, you'd notify both reporter and resource
        return jsonify({"message": "Need reported and matched!", "need": new_need, "matched_resource": matched_resource}), 201
    
    return jsonify({"message": "Need reported, awaiting match", "need": new_need}), 201

@app.route('/offer_resource', methods=['POST'])
def offer_resource():
    data = request.json
    if not data or not all(k in data for k in ['provider_id', 'type', 'description', 'location']):
        return jsonify({"error": "Missing data"}), 400

    resource_id = str(uuid.uuid4())
    new_resource = {
        "id": resource_id,
        "provider_id": data['provider_id'],
        "type": data['type'], # e.g., "volunteer", "shelter", "water_supply", "medical_volunteer"
        "description": data['description'],
        "location": data['location'],
        "capacity": data.get('capacity', 1), # For shelters, supplies
        "timestamp": get_timestamp(),
        "status": "available"
    }
    resources.append(new_resource)
    print(f"New Resource Offered: {new_resource}")
    return jsonify({"message": "Resource offered", "resource": new_resource}), 201

@app.route('/get_needs', methods=['GET'])
def get_needs():
    status_filter = request.args.get('status')
    if status_filter:
        filtered_needs = [n for n in needs if n['status'] == status_filter]
        return jsonify(filtered_needs)
    return jsonify(needs)

@app.route('/get_resources', methods=['GET'])
def get_resources():
    type_filter = request.args.get('type')
    if type_filter:
        filtered_resources = [r for r in resources if r['type'] == type_filter]
        return jsonify(filtered_resources)
    return jsonify(resources)

# Placeholder for user registration/login
@app.route('/register', methods=['POST'])
def register_user():
    data = request.json
    user_id = str(uuid.uuid4())
    users[user_id] = {"username": data['username'], "role": data['role']}
    return jsonify({"message": "User registered", "user_id": user_id}), 201


if __name__ == '__main__':
    app.run(debug=True)