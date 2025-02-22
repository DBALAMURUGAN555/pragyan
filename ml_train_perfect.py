import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib

# Normal behavior samples (keystroke timing + mouse speed)
normal_data = [
    [120, 140, 160, 0.5],
    [110, 130, 150, 0.6],
    [115, 135, 155, 0.4],
    [130, 145, 165, 0.45],
    [125, 140, 160, 0.55]
]

# Fraudulent behavior samples (abnormally fast or slow keystrokes & erratic mouse movement)
fraud_data = [
    [300, 500, 700, 2.5],  # Very slow typing, very fast erratic mouse
    [50, 60, 70, 3.0],     # Too fast typing, highly erratic mouse
    [20, 25, 30, 4.0],     # Bot-like typing, extremely fast movement
    [400, 450, 500, 0.1],  # Very slow typing, no mouse movement
    [80, 100, 120, 2.2]    # Unusual mix of fast typing & high mouse speed
]

# Combine normal and fraud data
data = normal_data + fraud_data

# Convert to DataFrame
df = pd.DataFrame(data, columns=['key_time_1', 'key_time_2', 'key_time_3', 'mouse_speed'])

# Train Isolation Forest Model (adjust contamination to detect more anomalies)
model = IsolationForest(contamination=0.3, random_state=42)
model.fit(df)

# Save trained model
joblib.dump(model, "behavior_model.pkl")
print("✅ Model trained and saved as 'behavior_model.pkl'")
