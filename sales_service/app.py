from flask import Flask, request, jsonify
import requests
from models import Sale
from db import db, init_db
import cProfile
import pstats
import io
import os
from functools import wraps


def profile_route(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create an in-memory buffer to capture the profiling stats
        pr = cProfile.Profile()
        pr.enable()

        # Call the actual route handler
        response = func(*args, **kwargs)

        pr.disable()

        # Prepare the profiling data
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
        ps.print_stats()

        # Log the profiling data to a file or print it for debugging
        log_dir = "profiling_logs"
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"{func.__name__}_profile.log")

        with open(log_file, "w") as f:
            f.write(s.getvalue())

        # Alternatively, print to console for development purposes
        # print(s.getvalue())

        # Return the original response
        return response

    return wrapper


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://user:password@db/sales_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
init_db(app)

CUSTOMERS_SERVICE_URL = "http://customers_service:5000"
INVENTORY_SERVICE_URL = "http://inventory_service:5000"


@app.route("/goods", methods=["GET"])
@profile_route
def display_goods():
    """
    Display all goods available in the inventory.

    **Endpoint:** ``/goods``

    **Method:** ``GET``

    **Responses:**
        - 200: A list of all goods with their names and prices.
        - 500: Unable to fetch goods.

    :return: JSON response with a list of goods or error message and status code.
    :rtype: tuple
    """
    response = requests.get(f"{INVENTORY_SERVICE_URL}/inventory")
    if response.status_code == 200:
        products = response.json()
        goods = [
            {"name": product["name"], "price": product["price_per_item"]}
            for product in products
        ]
        return jsonify(goods), 200
    return jsonify({"error": "Unable to fetch goods"}), 500


@app.route("/goods/<int:product_id>", methods=["GET"])
@profile_route
def get_goods_details(product_id):
    """
    Get details of a specific product by its ID.

    **Endpoint:** ``/goods/<product_id>``

    **Method:** ``GET``

    **URL Parameters:**
        - `product_id` (int): The ID of the product.

    **Responses:**
        - 200: Product details.
        - 404: Product not found.

    :param product_id: The ID of the product.
    :type product_id: int
    :return: JSON response with product details or error message and status code.
    :rtype: tuple
    """
    response = requests.get(f"{INVENTORY_SERVICE_URL}/inventory/{product_id}")
    if response.status_code == 200:
        return jsonify(response.json()), 200
    return jsonify({"error": "Product was not found"}), 404


@app.route("/sale", methods=["POST"])
@profile_route
def make_sale():
    """
    Make a sale for a specific product.

    **Endpoint:** ``/sale``

    **Method:** ``POST``

    **Request Body:**
        - `product_name` (str): The name of the product.
        - `username` (str): The username of the customer.
        @profile_route- `quantity` (int, optional): The quantity of the product to be purchased.
        Defaults to 1.

    **Responses:**
        - 200: Sale successful.
        - 400: Insufficient stock or funds.
        - 404: Customer or product not found.
        - 500: Failed to update customer wallet or product stock.

    **Process:**
        - Fetch product details from the inventory service.
        - Fetch customer details from the customer service.
        - Check if the product is in stock and if the customer has sufficient funds.
        - Deduct the total price from the customer's wallet.
        - Update the product stock in the inventory.
        - Create a sale record in the database.

    :return: JSON response with a message and status code.
    :rtype: tuple
    """
    try:
        data = request.json
        product_name = data.get("product_name")
        username = data.get("username")
        quantity = data.get("quantity", 1)

        product_response = requests.get(f"{INVENTORY_SERVICE_URL}/inventory")
        if product_response.status_code != 200:
            return jsonify({"error": "Failed to fetch products from inventory"}), 500

        products = product_response.json()
        product = next(
            (p for p in products if p["name"].lower() == product_name.lower()), None
        )
        if not product:
            return jsonify({"error": "Product not found"}), 404

        customer_response = requests.get(
            f"{CUSTOMERS_SERVICE_URL}/customers/{username}"
        )
        if customer_response.status_code != 200:
            return jsonify({"error": "Customer not found"}), 404
        customer = customer_response.json()

        if product["count_in_stock"] < quantity:
            return jsonify({"error": "Insufficient stock"}), 400
        total_price = product["price_per_item"] * quantity
        if customer["wallet_balance"] < total_price:
            return jsonify({"error": "Insufficient funds"}), 400

        wallet_deduction_response = requests.post(
            f"{CUSTOMERS_SERVICE_URL}/customers/{username}/deduct",
            json={"amount": total_price},
        )
        if wallet_deduction_response.status_code != 200:
            return jsonify({"error": "Failed to update customer wallet"}), 500

        stock_update_response = requests.put(
            f'{INVENTORY_SERVICE_URL}/inventory/{product["id"]}',
            json={"count_in_stock": product["count_in_stock"] - quantity},
        )
        if stock_update_response.status_code != 200:
            requests.post(
                f"{CUSTOMERS_SERVICE_URL}/customers/{username}/add",
                json={"amount": total_price},
            )
            return jsonify({"error": "Failed to update product stock"}), 500

        sale = Sale(
            customer_id=customer["id"],
            product_id=product["id"],
            quantity=quantity,
            total_price=total_price,
        )
        db.session.add(sale)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Sale successful",
                    "balance": customer["wallet_balance"] - total_price,
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
