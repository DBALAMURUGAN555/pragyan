import numpy as np
import pandas as pd
import joblib
from flask import Flask, request, jsonify
from flask_cors import CORS

# Load trained model
model = joblib.load("behavior_model.pkl")

app = Flask(__name__)
CORS(app)

@app.route('/analyze', methods=['POST'])
def analyze_behavior():
    """
    Receives real-time keystroke & mouse data from frontend and classifies behavior.
    """
    data = request.json
    keystrokes = data.get("keystrokes", [])
    mouse_speed = data.get("mouse_speed", 0)

    if not keystrokes and mouse_speed == 0:
        return jsonify({"status": "❌ No valid input received"})

    while len(keystrokes) < 3:
        keystrokes.append(0)

    test_sample = pd.DataFrame([keystrokes + [mouse_speed]], columns=['key_time_1', 'key_time_2', 'key_time_3', 'mouse_speed'])

    prediction = model.predict(test_sample)
    result = "🟢 Normal" if prediction[0] == 1 else "🔴 Fraud"

    print(f"🔍 Live Detection: {result} (Keystrokes: {keystrokes}, Mouse Speed: {mouse_speed})")

    # If fraud detected, simulate sending OTP verification
    if result == "🔴 Fraud":
        send_otp_verification()

    return jsonify({"status": result})

def send_otp_verification():
    print("📲 Sending OTP to User... (Simulated)")

if __name__ == "__main__":
    app.run(debug=True)
