from flask import Flask, request, jsonify
from sqlalchemy.exc import IntegrityError
from models import Customer
from db import db, init_db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db/customers_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
init_db(app)

@app.route('/auth', methods=['POST'])
def authenticate_customer():
    try:
        data = request.json 
        username = data.get("username")
        password = data.get("password")
        customer = Customer.query.filter_by(username=username).first()
        if password == customer.password:
            return jsonify({"id": customer.id}), 200
    except :
        db.session.rollback()
        return jsonify({"error": "Customer not authenticated or does not exist."}), 400

@app.route('/customers', methods=['POST'])
def register_customer():
    try:
        data = request.json
        customer = Customer(**data)
        db.session.add(customer)
        db.session.commit()
        return jsonify({"message": "Customer registered successfully"}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Username already exists"}), 400

@app.route('/customers/<username>', methods=['DELETE'])
def delete_customer(username):
    customer = Customer.query.filter_by(username=username).first()
    if customer:
        db.session.delete(customer)
        db.session.commit()
        return jsonify({"message": "Customer deleted"}), 200
    return jsonify({"error": "Customer not found"}), 404

@app.route('/customers/<username>', methods=['PUT'])
def update_customer(username):
    customer = Customer.query.filter_by(username=username).first()
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    data = request.json
    for key, value in data.items():
        setattr(customer, key, value)
    db.session.commit()
    return jsonify({"message": "Customer updated"}), 200

@app.route('/customers', methods=['GET'])
def get_all_customers():
    customers = Customer.query.all()
    return jsonify([customer.to_dict() for customer in customers]), 200

@app.route('/customers/<username>', methods=['GET'])
def get_customer(username):
    customer = Customer.query.filter_by(username=username).first()
    if customer:
        return jsonify(customer.to_dict()), 200
    return jsonify({"error": "Customer not found"}), 404

@app.route('/customers/<username>/charge', methods=['POST'])
def charge_wallet(username):
    data = request.json
    customer = Customer.query.filter_by(username=username).first()
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    customer.wallet_balance += data.get('amount', 0)
    db.session.commit()
    return jsonify({"message": "Wallet charged", "balance": customer.wallet_balance}), 200

@app.route('/customers/<username>/deduct', methods=['POST'])
def deduct_wallet(username):
    data = request.json
    customer = Customer.query.filter_by(username=username).first()
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    amount = data.get('amount', 0)
    if customer.wallet_balance < amount:
        return jsonify({"error": "Insufficient funds"}), 400
    customer.wallet_balance -= amount
    db.session.commit()
    return jsonify({"message": "Wallet deducted", "balance": customer.wallet_balance}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
