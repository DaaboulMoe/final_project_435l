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
    """
    Authenticate a customer based on username and password.

    This route validates the customer's credentials by checking the provided
    username and password against the stored data in the database. If the
    credentials are correct, the customer's ID is returned as a response.

    **Request Body**:
    - `username`: The username of the customer (string).
    - `password`: The password of the customer (string).

    **Response**:
    - If authentication is successful: `{"id": customer.id}` with a 200 status code.
    - If authentication fails: `{"error": "Customer not authenticated or does not exist."}` with a 400 status code.
    """
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
    """
    Register a new customer.

    This route allows a new customer to be registered by providing necessary
    details. If the registration is successful, a confirmation message is returned.

    **Request Body**:
    - Customer details (JSON object with attributes like username, password, etc.).

    **Response**:
    - If registration is successful: `{"message": "Customer registered successfully"}` with a 201 status code.
    - If the username already exists: `{"error": "Username already exists"}` with a 400 status code.
    """
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
    """
    Delete a customer by username.

    This route deletes a customer's account from the system based on the provided
    username. If the customer exists, they are removed from the database. If the
    customer is not found, an error message is returned.

    **Response**:
    - If the customer is deleted successfully: `{"message": "Customer deleted"}` with a 200 status code.
    - If the customer is not found: `{"error": "Customer not found"}` with a 404 status code.
    """
    customer = Customer.query.filter_by(username=username).first()
    if customer:
        db.session.delete(customer)
        db.session.commit()
        return jsonify({"message": "Customer deleted"}), 200
    return jsonify({"error": "Customer not found"}), 404

@app.route('/customers/<username>', methods=['PUT'])
def update_customer(username):
    """
    Update customer details by username.

    This route allows the customer details to be updated. The provided JSON body
    should contain the fields to be updated. If the customer is not found, an error
    message is returned.

    **Request Body**:
    - Customer details to be updated (JSON object).

    **Response**:
    - If the update is successful: `{"message": "Customer updated"}` with a 200 status code.
    - If the customer is not found: `{"error": "Customer not found"}` with a 404 status code.
    """
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
    """
    Retrieve a list of all customers.

    This route returns all customers from the database in JSON format.

    **Response**:
    - A list of all customers' details (JSON array).
    """
    customers = Customer.query.all()
    return jsonify([customer.to_dict() for customer in customers]), 200

@app.route('/customers/<username>', methods=['GET'])
def get_customer(username): 
    """
    Retrieve details of a specific customer by username.

    This route returns the details of a customer based on the provided username.
    If the customer is found, their details are returned. Otherwise, an error message is returned.

    **Response**:
    - If the customer is found: Customer details in JSON format with a 200 status code.
    - If the customer is not found: `{"error": "Customer not found"}` with a 404 status code.
    """
    customer = Customer.query.filter_by(username=username).first()
    if customer:
        return jsonify(customer.to_dict()), 200
    return jsonify({"error": "Customer not found"}), 404

@app.route('/customers/<username>/charge', methods=['POST'])
def charge_wallet(username):
    """
    Charge a customer's wallet.

    This route allows a customer to add funds to their wallet. The amount is provided
    in the request body. If the customer is not found, an error message is returned.

    **Request Body**:
    - `amount`: The amount to be added to the wallet (float).

    **Response**:
    - If successful: `{"message": "Wallet charged", "balance": updated_balance}` with a 200 status code.
    - If the customer is not found: `{"error": "Customer not found"}` with a 404 status code.
    """
    data = request.json
    customer = Customer.query.filter_by(username=username).first()
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    customer.wallet_balance += data.get('amount', 0)
    db.session.commit()
    return jsonify({"message": "Wallet charged", "balance": customer.wallet_balance}), 200

@app.route('/customers/<username>/deduct', methods=['POST'])
def deduct_wallet(username):
    """
    Deduct funds from a customer's wallet.

    This route allows a customer to withdraw funds from their wallet. The amount is provided
    in the request body. If the customer does not have sufficient funds, an error message is returned.

    **Request Body**:
    - `amount`: The amount to be deducted from the wallet (float).

    **Response**:
    - If successful: `{"message": "Wallet deducted", "balance": updated_balance}` with a 200 status code.
    - If the customer is not found: `{"error": "Customer not found"}` with a 404 status code.
    - If there are insufficient funds: `{"error": "Insufficient funds"}` with a 400 status code.
    """
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
