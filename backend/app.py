from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import datetime
import random
import joblib
import os
from openai import OpenAI

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key="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")

# Load the trained model
MODEL_PATH = "model/price_predictor.pkl"
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
else:
    model = None

@app.route('/chat', methods=['POST'])
def chat_ai():
    user_msg = request.json.get('message', '')

    if not user_msg:
        return jsonify({"reply": "Please type a message."})

    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a helpful assistant for a factory procurement dashboard."},
                      {"role": "user", "content": user_msg}],
            max_tokens=150
        )
        reply = response.choices[0].message.content
    except Exception as e:
        reply = "Error: " + str(e)

    return jsonify({"reply": reply})    

@app.route("/")
def home():
    return "<h2>✅ Smart Procurement Backend Running Successfully!</h2><p>Use /prices/latest, /inventory, etc.</p>"

# Load data
with open("data/prices.json") as f:
    prices = json.load(f)

with open("data/inventory.json") as f:
    inventory = json.load(f)

with open("data/suppliers.json") as f:
    suppliers = json.load(f)

orders = []  # store purchase orders

# 1️⃣ Get current prices
@app.route("/prices/latest", methods=["GET"])
def get_prices():
    return jsonify(prices)

# 2️⃣ Update prices (simulated) every call for demo
@app.route("/prices/update", methods=["POST"])
def update_prices():
    global prices
    for mat in prices:
        prices[mat] += random.uniform(-2, 2)
        prices[mat] = round(prices[mat], 2)
    return jsonify(prices)

# 3️⃣ Inventory endpoint
@app.route("/inventory", methods=["GET"])
def get_inventory():
    return jsonify(inventory)

# 4️⃣ Suppliers endpoint
@app.route("/suppliers/<material>", methods=["GET"])
def get_suppliers(material):
    return jsonify(suppliers.get(material, []))

# 5️⃣ Prediction (simple linear trend)
@app.route("/predict/<material>", methods=["GET"])
def predict(material):
    current_price = prices.get(material, 0)
    predicted_price = current_price + random.uniform(-5, 5)
    recommendation = "BUY_NOW" if predicted_price > current_price else "WAIT"
    return jsonify({
        "material": material,
        "current_price": current_price,
        "predicted_price": round(predicted_price,2),
        "recommendation": recommendation
    })

# 6️⃣ Create a purchase order
@app.route("/orders", methods=["POST"])
def create_order_api():
    data = request.json
    data["timestamp"] = datetime.datetime.utcnow().isoformat()
    orders.append(data)
    return jsonify({"status": "success", "order": data})

# 7️⃣ Get all orders
@app.route("/orders", methods=["GET"])
def get_orders_api():
    return jsonify(orders)

orders = []  # temporary list to store purchase orders

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    order = {
        "material": data["material"],
        "quantity": data["quantity"],
        "supplier": data["supplier"],
        "status": "Pending"
    }
    orders.append(order)
    return jsonify({"message": "Order created successfully", "order": order}), 201

@app.route('/orders', methods=['GET'])
def get_orders():
    return jsonify(orders)

@app.route('/predict/<material>')
def predict_price(material):
    global model
    if model is None:
        return jsonify({"error": "Model not trained yet"}), 500

    # Example input for prediction (you can improve this later)
    demand_index = 70
    supply_index = 60
    with open("data/prices.json") as f:
        current_prices = json.load(f)
    base_price = current_prices.get(material, 100)

    predicted_price = model.predict([[demand_index, supply_index, base_price]])[0]

    response = {
        "material": material,
        "current_price": base_price,
        "predicted_price": round(predicted_price, 2),
        "recommendation": "Buy" if predicted_price > base_price else "Wait"
    }
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
