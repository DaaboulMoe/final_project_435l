from flask import Flask, request, jsonify
from sqlalchemy.exc import IntegrityError
from models import Product
from db import db, init_db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db/inventory_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
init_db(app)

@app.route('/inventory', methods=['POST'])
def add_product():
    """
    Add a new product to the inventory.

    **Endpoint:** ``/inventory``

    **Method:** ``POST``

    **Request Body:**
        - `name` (str): The name of the product. (max 100 characters)
        - `category` (str): The category of the product. (max 50 characters)
        - `price_per_item` (float): The price per item of the product.
        - `description` (str, optional): The description of the product. (max 200 characters)
        - `count_in_stock` (int): The quantity of the product in stock.

    **Responses:**
        - 201: Product added successfully.
        - 400: Product could not be added due to an integrity error.

    :return: JSON response with a message and status code.
    :rtype: tuple
    """
    try:
        data = request.json
        product = Product(**data)
        db.session.add(product)
        db.session.commit()
        return jsonify({"message": "Product added successfully"}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Product could not be added"}), 400

@app.route('/inventory', methods=['GET'])
def get_all_products():
    """
    Get a list of all products in the inventory.

    **Endpoint:** ``/inventory``

    **Method:** ``GET``

    **Responses:**
        - 200: A list of all products.

    :return: JSON response with a list of products and status code.
    :rtype: tuple
    """
    products = Product.query.all() 
    products_list = [product.to_dict() for product in products] 
    return jsonify(products_list), 200

@app.route('/inventory/<int:product_id>', methods=['GET'])
def get_product_details(product_id):
    """
    Get details of a specific product by its ID.

    **Endpoint:** ``/inventory/<product_id>``

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
    product = Product.query.get(product_id)
    if product:
        return jsonify(product.to_dict()), 200
    else:
        return jsonify({"error": "Product not found"}), 404

@app.route('/inventory/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """
    Delete a specific product by its ID.

    **Endpoint:** ``/inventory/<product_id>``

    **Method:** ``DELETE``

    **URL Parameters:**
        - `product_id` (int): The ID of the product.

    **Responses:**
        - 200: Product deleted successfully.
        - 404: Product not found.

    :param product_id: The ID of the product.
    :type product_id: int
    :return: JSON response with a message or error message and status code.
    :rtype: tuple
    """
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Product deleted successfully"}), 200
    else:
        return jsonify({"error": "Product not found"}), 404

@app.route('/inventory/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """
    Update a specific product by its ID.

    **Endpoint:** ``/inventory/<product_id>``

    **Method:** ``PUT``

    **URL Parameters:**
        - `product_id` (int): The ID of the product.

    **Request Body:**
        - `name` (str, optional): The name of the product. (max 100 characters)
        - `category` (str, optional): The category of the product. (max 50 characters)
        - `price_per_item` (float, optional): The price per item of the product.
        - `description` (str, optional): The description of the product. (max 200 characters)
        - `count_in_stock` (int, optional): The quantity of the product in stock.

    **Responses:**
        - 200: Product updated successfully.
        - 404: Product not found.

    :param product_id: The ID of the product.
    :type product_id: int
    :return: JSON response with a message or error message and status code.
    :rtype: tuple
    """
    product = Product.query.get(product_id)
    if product:
        data = request.json
        for key, value in data.items():
            setattr(product, key, value)
        db.session.commit()
        return jsonify({"message": "Product updated successfully"}), 200
    else:
        return jsonify({"error": "Product not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)