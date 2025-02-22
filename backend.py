from flask import Flask, request, jsonify
from flask_cors import CORS
import pymongo
import time
import hashlib
import os
import binascii

app = Flask(__name__)
CORS(app)

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://tlmanees2006:mongo2006@cluster0.5gseg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["UserBehaviorDB"]
users_collection = db["users"]
behavior_collection = db["behavior_logs"]

# Thresholds for fraud detection
THRESHOLDS = {
    "typing_speed_variation": 0.2,  # Allowed change in typing speed
    "mouse_speed_variation": 10     # Allowed change in mouse speed
}

# Generate password hash (PBKDF2)
def generate_pbkdf2_hash(password: str, iterations: int = 100000) -> str:
    salt = os.urandom(16)
    salt_hex = binascii.hexlify(salt).decode()
    hash_bytes = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations)
    hash_hex = binascii.hexlify(hash_bytes).decode()
    return f"{salt_hex}${hash_hex}${iterations}"  # Format: salt$hash$iterations

# Verify password hash
def verify_pbkdf2_hash(password: str, stored_hash: str) -> bool:
    try:
        salt_hex, hash_hex, iterations = stored_hash.split("$")
        salt = binascii.unhexlify(salt_hex)
        iterations = int(iterations)
        hash_bytes = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations)
        return binascii.hexlify(hash_bytes).decode() == hash_hex
    except:
        return False

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if users_collection.find_one({"username": username}):
        return jsonify({"error": "Username already exists"}), 400

    hashed_password = generate_pbkdf2_hash(password)
    users_collection.insert_one({"username": username, "password_hash": hashed_password})
    
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = users_collection.find_one({"username": username})
    if not user or not verify_pbkdf2_hash(password, user["password_hash"]):
        return jsonify({"error": "Invalid username or password"}), 401

    return jsonify({"message": "Login successful"}), 200

@app.route('/track', methods=['POST'])
def track_behavior():
    data = request.json
    user_id = data.get("user_id")
    keyboard_intervals = data.get("keyboard_intervals", [])
    mouse_movements = data.get("mouse_movements", [])

    avg_typing_speed = sum(keyboard_intervals) / len(keyboard_intervals) if keyboard_intervals else float('inf')
    avg_mouse_speed = sum(mouse_movements) / len(mouse_movements) if mouse_movements else float('inf')

    last_entry = behavior_collection.find_one({"user_id": user_id}, sort=[("timestamp", -1)])

    if last_entry:
        prev_typing_speed = last_entry.get("typing_speed", avg_typing_speed)
        prev_mouse_speed = last_entry.get("mouse_speed", avg_mouse_speed)

        if abs(avg_typing_speed - prev_typing_speed) > THRESHOLDS["typing_speed_variation"] or \
           abs(avg_mouse_speed - prev_mouse_speed) > THRESHOLDS["mouse_speed_variation"]:
            status = "Fraudulent"
        else:
            status = "Normal"
    else:
        status = "Normal"

    behavior_collection.insert_one({
        "user_id": user_id,
        "typing_speed": avg_typing_speed,
        "mouse_speed": avg_mouse_speed,
        "status": status,
        "timestamp": time.time()
    })

    return jsonify({"user_id": user_id, "status": status, "typing_speed": avg_typing_speed, "mouse_speed": avg_mouse_speed})


