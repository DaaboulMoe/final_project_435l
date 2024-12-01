import requests

BASE_URL = "http://localhost:5004"

def test_submit_review():
    """Test submitting a new review."""
    review_data = {
        "product_id": 1,
        "rating": 4,
        "username": "testuser",
        "password": "testpassword",
        "comment": "Great product!"
    }
    response = requests.post(f"{BASE_URL}/reviews", json=review_data)
    assert response.status_code == 201
    assert "product_id" in response.json()
    assert response.json()["rating"] == 4
    assert response.json()["comment"] == "Great product!"

def test_submit_review_missing_fields():
    """Test submitting a review with missing required fields."""
    review_data = {
        "product_id": 1,
        "rating": 4,
        "username": "testuser"
    }
    response = requests.post(f"{BASE_URL}/reviews", json=review_data)
    assert response.status_code == 400
    assert response.json()["error"] == "Missing required fields"

def test_submit_review_invalid_rating():
    """Test submitting a review with an invalid rating."""
    review_data = {
        "product_id": 1,
        "rating": 6,  # Invalid rating
        "username": "testuser",
        "password": "testpassword"
    }
    response = requests.post(f"{BASE_URL}/reviews", json=review_data)
    assert response.status_code == 400
    assert response.json()["error"] == "Rating must be between 0 and 5"

def test_submit_review_unauthorized():
    """Test submitting a review with invalid credentials."""
    review_data = {
        "product_id": 1,
        "rating": 4,
        "username": "wronguser",
        "password": "wrongpassword"
    }
    response = requests.post(f"{BASE_URL}/reviews", json=review_data)
    assert response.status_code == 403
    assert response.json()["message"] == "Unauthorized"

def test_update_review():
    """Test updating an existing review."""
    review_data = {
        "username": "testuser",
        "password": "testpassword",
        "rating": 5,
        "comment": "Updated comment"
    }
    # Assuming review_id is 1
    response = requests.put(f"{BASE_URL}/reviews/1", json=review_data)
    assert response.status_code == 200
    updated_review = response.json()
    assert updated_review["rating"] == 5
    assert updated_review["comment"] == "Updated comment"

def test_update_review_invalid_rating():
    """Test updating a review with an invalid rating."""
    review_data = {
        "username": "testuser",
        "password": "testpassword",
        "rating": 6,  # Invalid rating
        "comment": "Updated comment"
    }
    response = requests.put(f"{BASE_URL}/reviews/1", json=review_data)
    assert response.status_code == 400
    assert response.json()["error"] == "Rating must be between 0 and 5"

def test_update_review_unauthorized():
    """Test updating a review by a customer who did not create it."""
    review_data = {
        "username": "wronguser",
        "password": "wrongpassword",
        "rating": 5,
        "comment": "Unauthorized update"
    }
    response = requests.put(f"{BASE_URL}/reviews/1", json=review_data)
    assert response.status_code == 403
    assert response.json()["error"] == "Unauthorized to modify this review"

def test_delete_review():
    """Test deleting a review."""
    review_data = {
        "username": "testuser",
        "password": "testpassword"
    }
    # Assuming review_id is 1
    response = requests.delete(f"{BASE_URL}/reviews/1", json=review_data)
    assert response.status_code == 200

def test_delete_review_unauthorized():
    """Test deleting a review by a customer who did not create it."""
    review_data = {
        "username": "wronguser",
        "password": "wrongpassword"
    }
    response = requests.delete(f"{BASE_URL}/reviews/1", json=review_data)
    assert response.status_code == 403
    assert response.json()["error"] == "Unauthorized"

def test_get_product_reviews():
    """Test fetching all reviews for a specific product."""
    response = requests.get(f"{BASE_URL}/products/1/reviews")
    assert response.status_code == 200
    reviews = response.json()
    assert isinstance(reviews, list)
    assert len(reviews) > 0

def test_get_product_reviews_not_found():
    """Test fetching reviews for a non-existent product."""
    response = requests.get(f"{BASE_URL}/products/9999/reviews")
    assert response.status_code == 404
    assert response.json()["message"] == "Product not found or does not exist."

def test_get_customer_reviews():
    """Test fetching all reviews submitted by a specific customer."""
    response = requests.get(f"{BASE_URL}/customers/1/reviews")
    assert response.status_code == 200
    reviews = response.json()
    assert isinstance(reviews, list)
    assert len(reviews) > 0

def test_get_review_details():
    """Test fetching details of a specific review."""
    response = requests.get(f"{BASE_URL}/reviews/1")
    assert response.status_code == 200
    review = response.json()
    assert review["id"] == 1

def test_moderate_review():
    """Test moderating a review."""
    admin_data = {
        "username": "admin",
        "password": "adminpassword",
        "moderated": True
    }
    # Assuming review_id is 1
    response = requests.post(f"{BASE_URL}/reviews/1/moderate", json=admin_data)
    assert response.status_code == 200
    assert response.json()["moderated"] == True

def test_moderate_review_unauthorized():
    """Test moderating a review by an unauthorized user."""
    admin_data = {
        "username": "wronguser",
        "password": "wrongpassword",
        "moderated": True
    }
    response = requests.post(f"{BASE_URL}/reviews/1/moderate", json=admin_data)
    assert response.status_code == 403
    assert response.json()["message"] == "Unauthorized"
