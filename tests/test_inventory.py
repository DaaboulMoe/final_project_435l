import requests

BASE_URL = "http://localhost:5002"

def test_add_product():
    """Test adding a new product to the inventory."""
    product_data = {
        "name": "Test Product",
        "category": "Electronics",
        "price_per_item": 299.99,
        "description": "A test product for inventory",
        "count_in_stock": 10,
    }
    response = requests.post(f"{BASE_URL}/inventory", json=product_data)
    assert response.status_code == 201
    assert response.json()["message"] == "Product added successfully"

def test_get_all_products():
    """Test fetching all products."""
    response = requests.get(f"{BASE_URL}/inventory")
    assert response.status_code == 200
    products = response.json()
    assert isinstance(products, list)
    assert len(products) > 0 

def test_get_product_details():
    """Test fetching details of a specific product."""
    # Get the list of all products
    products = requests.get(f"{BASE_URL}/inventory").json()
    product_id = products[0]["id"]

    # Fetch product details
    response = requests.get(f"{BASE_URL}/inventory/{product_id}")
    assert response.status_code == 200
    product = response.json()
    assert product["id"] == product_id

def test_update_product():
    """Test updating a product."""
    # Get the list of all products
    products = requests.get(f"{BASE_URL}/inventory").json()
    product_id = products[0]["id"]

    # Update product data
    updated_data = {"count_in_stock": 50}
    response = requests.put(f"{BASE_URL}/inventory/{product_id}", json=updated_data)
    assert response.status_code == 200
    assert response.json()["message"] == "Product updated successfully"

    # Verify the update
    product = requests.get(f"{BASE_URL}/inventory/{product_id}").json()
    assert product["count_in_stock"] == 50

def test_delete_product():
    """Test deleting a product."""
    # Get the list of all products
    products = requests.get(f"{BASE_URL}/inventory").json()
    product_id = products[0]["id"]

    # Delete the product
    response = requests.delete(f"{BASE_URL}/inventory/{product_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Product deleted successfully"

    # Verify deletion
    response = requests.get(f"{BASE_URL}/inventory/{product_id}")
    assert response.status_code == 404
    assert response.json()["error"] == "Product not found"
