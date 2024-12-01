import requests

BASE_URL = "http://localhost:5001"

def test_authenticate_customer():
    """Test customer authentication."""
    # Test successful authentication
    auth_data = {"username": "test_user", "password": "test_password"}
    response = requests.post(f"{BASE_URL}/auth", json=auth_data)
    assert response.status_code == 200
    assert "id" in response.json()

    # Test failed authentication
    auth_data = {"username": "wrong_user", "password": "wrong_password"}
    response = requests.post(f"{BASE_URL}/auth", json=auth_data)
    assert response.status_code == 400
    assert response.json()["error"] == "Customer not authenticated or does not exist."

def test_register_customer():
    """Test customer registration."""
    # Test successful registration
    register_data = {"username": "new_user", "password": "new_password"}
    response = requests.post(f"{BASE_URL}/customers", json=register_data)
    assert response.status_code == 201
    assert response.json()["message"] == "Customer registered successfully"

    # Test registration with existing username
    response = requests.post(f"{BASE_URL}/customers", json=register_data)
    assert response.status_code == 400
    assert response.json()["error"] == "Username already exists"

def test_get_all_customers():
    """Test fetching all customers."""
    response = requests.get(f"{BASE_URL}/customers")
    assert response.status_code == 200
    customers = response.json()
    assert isinstance(customers, list)
    assert len(customers) > 0

def test_get_customer_details():
    """Test fetching details of a specific customer."""
    # Register a customer first
    register_data = {"username": "test_customer", "password": "test_password"}
    requests.post(f"{BASE_URL}/customers", json=register_data)

    # Fetch the customer's details
    response = requests.get(f"{BASE_URL}/customers/test_customer")
    assert response.status_code == 200
    customer = response.json()
    assert customer["username"] == "test_customer"

    # Test customer not found
    response = requests.get(f"{BASE_URL}/customers/non_existing_user")
    assert response.status_code == 404
    assert response.json()["error"] == "Customer not found"

def test_update_customer():
    """Test updating customer details."""
    # Register a customer first
    register_data = {"username": "update_customer", "password": "update_password"}
    requests.post(f"{BASE_URL}/customers", json=register_data)

    # Update the customer's details
    update_data = {"password": "new_password"}
    response = requests.put(f"{BASE_URL}/customers/update_customer", json=update_data)
    assert response.status_code == 200
    assert response.json()["message"] == "Customer updated"

    # Verify the update by fetching the customer details
    response = requests.get(f"{BASE_URL}/customers/update_customer")
    assert response.status_code == 200
    customer = response.json()
    assert customer["password"] == "new_password"

def test_delete_customer():
    """Test deleting a customer."""
    # Register a customer first
    register_data = {"username": "delete_customer", "password": "delete_password"}
    requests.post(f"{BASE_URL}/customers", json=register_data)

    # Delete the customer
    response = requests.delete(f"{BASE_URL}/customers/delete_customer")
    assert response.status_code == 200
    assert response.json()["message"] == "Customer deleted"

    # Verify deletion by attempting to fetch the customer
    response = requests.get(f"{BASE_URL}/customers/delete_customer")
    assert response.status_code == 404
    assert response.json()["error"] == "Customer not found"

def test_charge_wallet():
    """Test charging a customer's wallet."""
    # Register a customer first
    register_data = {"username": "charge_customer", "password": "charge_password"}
    requests.post(f"{BASE_URL}/customers", json=register_data)

    # Charge the wallet
    charge_data = {"amount": 50.0}
    response = requests.post(f"{BASE_URL}/customers/charge_customer/charge", json=charge_data)
    assert response.status_code == 200
    assert response.json()["message"] == "Wallet charged"
    assert response.json()["balance"] == 50.0

    # Test customer not found
    response = requests.post(f"{BASE_URL}/customers/non_existing_user/charge", json=charge_data)
    assert response.status_code == 404
    assert response.json()["error"] == "Customer not found"

def test_deduct_wallet():
    """Test deducting funds from a customer's wallet."""
    # Register a customer first
    register_data = {"username": "deduct_customer", "password": "deduct_password"}
    requests.post(f"{BASE_URL}/customers", json=register_data)

    # Charge the wallet first
    charge_data = {"amount": 100.0}
    requests.post(f"{BASE_URL}/customers/deduct_customer/charge", json=charge_data)

    # Deduct funds
    deduct_data = {"amount": 50.0}
    response = requests.post(f"{BASE_URL}/customers/deduct_customer/deduct", json=deduct_data)
    assert response.status_code == 200
    assert response.json()["message"] == "Wallet deducted"
    assert response.json()["balance"] == 50.0

    # Test insufficient funds
    deduct_data = {"amount": 100.0}
    response = requests.post(f"{BASE_URL}/customers/deduct_customer/deduct", json=deduct_data)
    assert response.status_code == 400
    assert response.json()["error"] == "Insufficient funds"

    # Test customer not found
    response = requests.post(f"{BASE_URL}/customers/non_existing_user/deduct", json=deduct_data)
    assert response.status_code == 404
    assert response.json()["error"] == "Customer not found"
