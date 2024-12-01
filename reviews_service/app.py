from flask import Flask, request, jsonify
from sqlalchemy.exc import IntegrityError
from models import Review
from db import db, init_db
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db/reviews_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
init_db(app)

CUSTOMERS_SERVICE_URL = 'http://customers_service:5000'
INVENTORY_SERVICE_URL = 'http://inventory_service:5000'

@app.route('/reviews', methods=['POST'])
def submit_review():
    """Submit a new review for a product"""
    data = request.get_json()
    
    required_fields = ['product_id', 'rating', 'username', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({
            'error': 'Missing required fields'
        }), 400

    # Authenticate customer at url
    username = data.get("username")
    password = data.get("password")
    product_id = data.get('product_id')
    rating = data.get('rating')

    # Authenticate and get customer's id
    response = requests.post(f'{CUSTOMERS_SERVICE_URL}/auth', json={"username" : username, "password" : password})
    response_data = response.json()
    print("RESPONSE DATAAAAAAAA")
    print("response data ", response_data)
    customer_id = response_data['id']
    if response.status_code != 200:
        return jsonify({"message" : "Unauthorized"}), 403
    
    # Check if product_id exists
    response = requests.get(f'{INVENTORY_SERVICE_URL}/inventory/validate/{product_id}')
    if response.status_code != 200:
        return jsonify({"message" : "Product not found or does not exist."}), 404

    if not (0 <= data['rating'] <= 5):
        return jsonify({
            'error': 'Rating must be between 0 and 5'
        }), 400

    try:
        review = Review(
            customer_id=customer_id,
            product_id=data['product_id'],
            rating=data['rating'],
            comment=data.get('comment', '')
        )
        db.session.add(review)
        db.session.commit()
        return jsonify(review.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to create review'
        }), 400

@app.route('/reviews/<int:review_id>', methods=['PUT'])
def update_review(review_id):
    """Update an existing review"""
    data = request.get_json()
    review = Review.query.get_or_404(review_id)
    
    required_fields = ['username', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({
            'error': 'Missing required fields'
        }), 400
    username = data.get("username")
    password = data.get("password")

    #Get customer's id after authenticating
    response = requests.post(f'{CUSTOMERS_SERVICE_URL}/auth', json={"username" : username, "password" : password})
    if response.status_code != 200:
        return jsonify({"message" : "Unauthorized"}), 403
    customer_id = response.json()["id"]

    # Verify customer owns this review
    if customer_id != review.customer_id:
        return jsonify({
            'error': 'Unauthorized to modify this review'
        }), 403

    if 'rating' in data:
        if not (0 <= data['rating'] <= 5):
            return jsonify({
                'error': 'Rating must be between 0 and 5'
            }), 400
        review.rating = data['rating']
        
    if 'comment' in data:
        review.comment = data['comment']
        review.moderated = False  # Reset moderation status on update
        
    try:
        db.session.commit()
        return jsonify(review.to_dict()), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to update review'
        }), 400

@app.route('/reviews/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    """Delete a review"""
    data = request.get_json()
    review = Review.query.get_or_404(review_id)
    
    required_fields = ['username', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({
            'error': 'Missing required fields'
        }), 400
    username = data.get("username")
    password = data.get("password")

    #Get customer's id after authenticating
    response = requests.post(f'{CUSTOMERS_SERVICE_URL}/auth', json={"username" : username, "password" : password})
    if response.status_code != 200:
        return jsonify({"message" : "Unauthorized"}), 403
    
    try:
        db.session.delete(review)
        db.session.commit()
        return '', 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to delete review'
        }), 400

@app.route('/products/<int:product_id>/reviews', methods=['GET'])
def get_product_reviews(product_id):
    """Get all reviews for a specific product"""
    reviews = Review.query.filter_by(product_id=product_id).all()
    return jsonify([review.to_dict() for review in reviews]), 200

@app.route('/customers/<int:customer_id>/reviews', methods=['GET'])
def get_customer_reviews(customer_id):
    """Get all reviews by a specific customer"""
    reviews = Review.query.filter_by(customer_id=customer_id).all()
    return jsonify([review.to_dict() for review in reviews]), 200

@app.route('/reviews/<int:review_id>/moderate', methods=['POST'])
def moderate_review(review_id):
    """Moderate a review (admin only)"""
    data = request.get_json()
    review = Review.query.get_or_404(review_id)

    required_fields = ['username', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({
            'error': 'Missing required fields'
        }), 400
    username = data.get("username")
    password = data.get("password")

    if username != "admin":
        return jsonify({"message" : "Unauthorized"}), 403

    #Authenticate admin
    response = requests.post(f'{CUSTOMERS_SERVICE_URL}/auth', json={"username" : username, "password" : password})
    if response.status_code != 200:
        return jsonify({"message" : "Unauthorized"}), 403
    
    if 'moderated' in data:
        review.moderated = data['moderated'] == True
        
    try:
        db.session.commit()
        return jsonify(review.to_dict()), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to moderate review'
        }), 400

@app.route('/reviews/<int:review_id>', methods=['GET'])
def get_review_details(review_id):
    """Get detailed information about a specific review"""
    review = Review.query.get_or_404(review_id)
    return jsonify(review.to_dict()), 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
