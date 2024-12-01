import pytest
from unittest.mock import patch, MagicMock
import requests

SALES_URL = "http://localhost:5003"
INVENTORY_URL = "http://localhost:5002"
CUSTOMERS_URL = "http://localhost:5001"


@pytest.fixture
def mock_requests():
    """Fixture to mock all external requests."""
    with patch("requests.get") as mock_get, patch("requests.post") as mock_post, patch("requests.put") as mock_put:
        yield mock_get, mock_post, mock_put


def test_get_goods(mock_requests):
    """Test fetching goods from the sales service."""
    mock_get, mock_post, mock_put = mock_requests

    # Mock inventory service response
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [
        {"id": 1, "name": "Test Product", "category": "Electronics", "price_per_item": 100.0, "description": "A test product", "count_in_stock": 20}
    ]

    # Test API call
    response = requests.get(f"{SALES_URL}/goods")
    assert response.status_code == 200
    goods = response.json()
    assert len(goods) == 1
    assert goods[0]["name"] == "Test Product"


def test_get_goods_details(mock_requests):
    """Test fetching details of a specific product."""
    mock_get, mock_post, mock_put = mock_requests

    # Mock inventory service response for a specific product
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "id": 1, "name": "Test Product", "category": "Electronics", "price_per_item": 100.0, "description": "A test product", "count_in_stock": 20
    }

    # Test API call
    response = requests.get(f"{SALES_URL}/goods/1")
    assert response.status_code == 200
    product = response.json()
    assert product["id"] == 1
    assert product["name"] == "Test Product"


def test_make_sale_success(mock_requests):
    """Test successfully making a sale."""
    mock_get, mock_post, mock_put = mock_requests

    # Mock inventory and customer service responses
    mock_get.side_effect = [
        MagicMock(
            status_code=200,
            json=lambda: [
                {"id": 1, "name": "Test Product", "category": "Electronics", "price_per_item": 100.0, "description": "A test product", "count_in_stock": 20}
            ],
        ),
        MagicMock(
            status_code=200,
            json=lambda: {"id": 1, "username": "test_user", "wallet_balance": 1000.0},
        ),
    ]

    # Mock customers and inventory service updates
    mock_post.return_value = MagicMock(status_code=200, json=lambda: {"message": "Sale successful", "balance": 800.0})
    mock_put.return_value = MagicMock(status_code=200)

    # Test sale API
    sale_data = {"product_name": "Test Product", "username": "test_user", "quantity": 2}
    response = requests.post(f"{SALES_URL}/sale", json=sale_data)

    assert response.status_code == 200
    result = response.json()
    assert result["message"] == "Sale successful"
    assert result["balance"] == 800.0


def test_make_sale_insufficient_stock(mock_requests):
    """Test making a sale with insufficient stock."""
    mock_get, mock_post, mock_put = mock_requests

    # Mock inventory service response with insufficient stock
    mock_get.side_effect = [
        MagicMock(
            status_code=200,
            json=lambda: [
                {"id": 1, "name": "Test Product", "category": "Electronics", "price_per_item": 100.0, "description": "A test product", "count_in_stock": 1}
            ],
        ),
    ]

    # Mock sale response
    mock_post.return_value = MagicMock(status_code=400, json=lambda: {"error": "Insufficient stock"})

    # Test sale API
    sale_data = {"product_name": "Test Product", "username": "test_user", "quantity": 2}
    response = requests.post(f"{SALES_URL}/sale", json=sale_data)

    assert response.status_code == 400
    result = response.json()
    assert result["error"] == "Insufficient stock"


def test_make_sale_insufficient_funds(mock_requests):
    """Test making a sale with insufficient funds."""
    mock_get, mock_post, mock_put = mock_requests

    # Mock inventory and customers service responses
    mock_get.side_effect = [
        MagicMock(
            status_code=200,
            json=lambda: [
                {"id": 1, "name": "Test Product", "category": "Electronics", "price_per_item": 100.0, "description": "A test product", "count_in_stock": 20}
            ],
        ),
        MagicMock(
            status_code=200,
            json=lambda: {"id": 1, "username": "test_user", "wallet_balance": 50.0},
        ),
    ]

    # Mock sale response
    mock_post.return_value = MagicMock(status_code=400, json=lambda: {"error": "Insufficient funds"})

    # Test sale API
    sale_data = {"product_name": "Test Product", "username": "test_user", "quantity": 2}
    response = requests.post(f"{SALES_URL}/sale", json=sale_data)

    assert response.status_code == 400
    result = response.json()
    assert result["error"] == "Insufficient funds"
