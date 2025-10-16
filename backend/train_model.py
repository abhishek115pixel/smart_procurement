# train_model.py
import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib
import os

# Ensure model folder exists
os.makedirs("model", exist_ok=True)

# Sample training data
data = {
    "demand_index": [80, 60, 90, 70, 85, 40, 100, 50],
    "supply_index": [50, 80, 40, 60, 45, 90, 30, 75],
    "base_price": [200, 180, 220, 190, 210, 170, 240, 175],
    "future_price": [220, 185, 250, 200, 230, 160, 270, 180]
}

df = pd.DataFrame(data)

# Train the model
X = df[["demand_index", "supply_index", "base_price"]]
y = df["future_price"]

model = LinearRegression()
model.fit(X, y)

# Save the model
joblib.dump(model, "model/price_predictor.pkl")

print("✅ Model trained and saved as model/price_predictor.pkl")