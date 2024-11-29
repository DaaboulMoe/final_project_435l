from flask import Flask, request, jsonify
import requests
from models import Sale
from db import db, init_db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db/sales_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
init_db(app)

CUSTOMERS_SERVICE_URL = 'http://customers_service:5000'
INVENTORY_SERVICE_URL = 'http://inventory_service:5000'

@app.route('/goods', methods=['GET'])
def display_goods():
    response = requests.get(f'{INVENTORY_SERVICE_URL}/inventory')
    if response.status_code == 200:
        products = response.json()
        goods = [{"name": product["name"], "price": product["price_per_item"]} for product in products]
        return jsonify(goods), 200
    return jsonify({"error": "Unable to fetch goods"}), 500

@app.route('/goods/<int:product_id>', methods=['GET'])
def get_goods_details(product_id):
    response = requests.get(f'{INVENTORY_SERVICE_URL}/inventory/{product_id}')
    if response.status_code == 200:
        return jsonify(response.json()), 200
    return jsonify({"error": "Product was not found"}), 404


@app.route('/sale', methods=['POST'])
def make_sale():
    try:
        data = request.json
        product_name = data.get('product_name')
        username = data.get('username')
        quantity = data.get('quantity', 1)

        product_response = requests.get(f'{INVENTORY_SERVICE_URL}/inventory')
        if product_response.status_code != 200:
            return jsonify({"error": "Failed to fetch products from inventory"}), 500

        products = product_response.json()
        product = next((p for p in products if p["name"].lower() == product_name.lower()), None)
        if not product:
            return jsonify({"error": "Product not found"}), 404

        customer_response = requests.get(f'{CUSTOMERS_SERVICE_URL}/customers/{username}')
        if customer_response.status_code != 200:
            return jsonify({"error": "Customer not found"}), 404
        customer = customer_response.json()

        if product["count_in_stock"] < quantity:
            return jsonify({"error": "Insufficient stock"}), 400
        total_price = product["price_per_item"] * quantity
        if customer["wallet_balance"] < total_price:
            return jsonify({"error": "Insufficient funds"}), 400

        wallet_deduction_response = requests.post(
            f'{CUSTOMERS_SERVICE_URL}/customers/{username}/deduct',
            json={'amount': total_price}
        )
        if wallet_deduction_response.status_code != 200:
            return jsonify({"error": "Failed to update customer wallet"}), 500

        stock_update_response = requests.put(
            f'{INVENTORY_SERVICE_URL}/inventory/{product["id"]}',
            json={'count_in_stock': product["count_in_stock"] - quantity}
        )
        if stock_update_response.status_code != 200:
            requests.post(f'{CUSTOMERS_SERVICE_URL}/customers/{username}/add', json={'amount': total_price})
            return jsonify({"error": "Failed to update product stock"}), 500

        sale = Sale(
            customer_id=customer["id"],
            product_id=product["id"],
            quantity=quantity,
            total_price=total_price
        )
        db.session.add(sale)
        db.session.commit()

        return jsonify({
            "message": "Sale successful",
            "balance": customer["wallet_balance"] - total_price
        }), 200

    except Exception as e:
        db.session.rollback() 
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)