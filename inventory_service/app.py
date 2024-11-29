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
    try:
        data = request.json
        product = Product(**data)
        db.session.add(product)
        db.session.commit()
        return jsonify({"message": "Product added successfully"}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Product could not be added"}), 400

@app.route('/inventory/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Product deleted successfully"}), 200
    else:
        return jsonify({"error": "Product not found"}), 404

@app.route('/inventory/<int:product_id>', methods=['PUT'])
def update_product(product_id):
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