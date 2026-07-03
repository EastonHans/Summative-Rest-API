import pytest
import json
import os
from unittest.mock import patch, MagicMock
from app import app, init_database
from database import (
    create_item, update_item, delete_item, get_item_by_id,
    get_all_items, search_items_by_name, search_items_by_barcode
)
from external_api import fetch_product_details, ExternalAPIIntegration


# ==================== FIXTURES ====================

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    init_database()  # Initialize database with test data
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def cleanup():
    """Clean up test database file."""
    yield
    # Clean up after each test
    if os.path.exists('inventory.json'):
        try:
            os.remove('inventory.json')
        except:
            pass


# ==================== DATABASE TESTS ====================

class TestDatabase:
    """Test database operations."""
    
    def test_create_item(self):
        """Test creating a new inventory item."""
        init_database()
        item_data = {
            "name": "Test Product",
            "barcode": "1234567890",
            "quantity": 10,
            "price": 5.99,
            "brand": "Test Brand",
            "category": "Test",
            "description": "Test item"
        }
        
        item = create_item(item_data)
        
        assert item['name'] == "Test Product"
        assert item['barcode'] == "1234567890"
        assert item['quantity'] == 10
        assert item['price'] == 5.99
        assert 'id' in item
        assert 'created_at' in item
    
    def test_get_all_items(self):
        """Test retrieving all items."""
        init_database()
        items = get_all_items()
        
        assert isinstance(items, list)
        assert len(items) > 0
    
    def test_get_item_by_id(self):
        """Test retrieving a single item by ID."""
        init_database()
        items = get_all_items()
        first_item_id = items[0]['id']
        
        item = get_item_by_id(first_item_id)
        
        assert item is not None
        assert item['id'] == first_item_id
    
    def test_get_nonexistent_item(self):
        """Test retrieving an item that doesn't exist."""
        init_database()
        item = get_item_by_id(99999)
        
        assert item is None
    
    def test_update_item(self):
        """Test updating an item."""
        init_database()
        items = get_all_items()
        item_id = items[0]['id']
        
        updated = update_item(item_id, {"quantity": 99, "price": 9.99})
        
        assert updated is not None
        assert updated['quantity'] == 99
        assert updated['price'] == 9.99
    
    def test_update_nonexistent_item(self):
        """Test updating a non-existent item."""
        init_database()
        updated = update_item(99999, {"quantity": 50})
        
        assert updated is None
    
    def test_delete_item(self):
        """Test deleting an item."""
        init_database()
        items = get_all_items()
        initial_count = len(items)
        item_id = items[0]['id']
        
        deleted = delete_item(item_id)
        
        assert deleted is True
        assert len(get_all_items()) == initial_count - 1
    
    def test_delete_nonexistent_item(self):
        """Test deleting a non-existent item."""
        init_database()
        deleted = delete_item(99999)
        
        assert deleted is False
    
    def test_search_items_by_name(self):
        """Test searching items by name."""
        init_database()
        results = search_items_by_name("Almond")
        
        assert len(results) > 0
        assert "Almond" in results[0]['name']
    
    def test_search_items_by_name_no_match(self):
        """Test searching with no matches."""
        init_database()
        results = search_items_by_name("XYZ_NONEXISTENT")
        
        assert len(results) == 0
    
    def test_search_items_by_barcode(self):
        """Test searching items by barcode."""
        init_database()
        items = get_all_items()
        barcode = items[0]['barcode']
        
        result = search_items_by_barcode(barcode)
        
        assert result is not None
        assert result['barcode'] == barcode
    
    def test_search_items_by_barcode_no_match(self):
        """Test searching barcode with no match."""
        init_database()
        result = search_items_by_barcode("0000000000")
        
        assert result is None


# ==================== API ENDPOINT TESTS ====================

class TestAPIEndpoints:
    """Test Flask API endpoints."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
    
    def test_get_all_inventory(self, client):
        """Test GET /inventory endpoint."""
        response = client.get('/inventory')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'count' in data
    
    def test_get_single_item(self, client):
        """Test GET /inventory/<id> endpoint."""
        # First get all items to get an ID
        response = client.get('/inventory')
        items = json.loads(response.data)['data']
        item_id = items[0]['id']
        
        response = client.get(f'/inventory/{item_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data']['id'] == item_id
    
    def test_get_nonexistent_item(self, client):
        """Test GET /inventory/<id> for non-existent item."""
        response = client.get('/inventory/99999')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_create_item(self, client):
        """Test POST /inventory endpoint."""
        new_item = {
            "name": "Test Product",
            "barcode": "9999999999",
            "quantity": 50,
            "price": 9.99,
            "brand": "Test Brand",
            "category": "Test",
            "description": "Test description"
        }
        
        response = client.post(
            '/inventory',
            data=json.dumps(new_item),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data']['name'] == "Test Product"
    
    def test_create_item_missing_required_field(self, client):
        """Test POST /inventory with missing required field."""
        invalid_item = {
            "name": "Test Product",
            "quantity": 50
            # Missing required fields
        }
        
        response = client.post(
            '/inventory',
            data=json.dumps(invalid_item),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_update_item(self, client):
        """Test PATCH /inventory/<id> endpoint."""
        # Get an existing item
        response = client.get('/inventory')
        items = json.loads(response.data)['data']
        item_id = items[0]['id']
        
        update_data = {
            "quantity": 999,
            "price": 19.99
        }
        
        response = client.patch(
            f'/inventory/{item_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data']['quantity'] == 999
        assert data['data']['price'] == 19.99
    
    def test_update_nonexistent_item(self, client):
        """Test PATCH /inventory/<id> for non-existent item."""
        response = client.patch(
            '/inventory/99999',
            data=json.dumps({"quantity": 50}),
            content_type='application/json'
        )
        
        assert response.status_code == 404
    
    def test_delete_item(self, client):
        """Test DELETE /inventory/<id> endpoint."""
        # Get an existing item
        response = client.get('/inventory')
        items = json.loads(response.data)['data']
        initial_count = len(items)
        item_id = items[0]['id']
        
        response = client.delete(f'/inventory/{item_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        
        # Verify item was deleted
        response = client.get('/inventory')
        items = json.loads(response.data)['data']
        assert len(items) == initial_count - 1
    
    def test_delete_nonexistent_item(self, client):
        """Test DELETE /inventory/<id> for non-existent item."""
        response = client.delete('/inventory/99999')
        
        assert response.status_code == 404
    
    def test_search_by_name(self, client):
        """Test GET /inventory/search/name endpoint."""
        response = client.get('/inventory/search/name?q=Almond')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_search_by_name_missing_query(self, client):
        """Test search by name without query parameter."""
        response = client.get('/inventory/search/name')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_search_by_barcode(self, client):
        """Test GET /inventory/search/barcode endpoint."""
        # Get a known barcode
        response = client.get('/inventory')
        items = json.loads(response.data)['data']
        barcode = items[0]['barcode']
        
        response = client.get(f'/inventory/search/barcode?barcode={barcode}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data']['barcode'] == barcode
    
    def test_search_by_barcode_missing_param(self, client):
        """Test search by barcode without barcode parameter."""
        response = client.get('/inventory/search/barcode')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'


# ==================== EXTERNAL API TESTS ====================

class TestExternalAPI:
    """Test external API integration."""
    
    def test_api_integration_initialization(self):
        """Test ExternalAPIIntegration initialization."""
        api = ExternalAPIIntegration()
        
        assert api.base_url == "https://world.openfoodfacts.org/api/v0"
        assert api.timeout == 5
    
    @patch('external_api.requests.get')
    def test_fetch_product_by_barcode_success(self, mock_get):
        """Test successful product fetch by barcode."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": 1,
            "product": {
                "product_name": "Test Product",
                "brands": "Test Brand",
                "code": "1234567890",
                "categories": "Food",
                "ingredients_text": "Ingredient 1, Ingredient 2",
                "nutrition_grade_fr": "A",
                "energy_kcal_100g": 100,
                "fat_100g": 5.0,
                "carbohydrates_100g": 10.0,
                "proteins_100g": 8.0,
                "image_front_url": "https://example.com/image.jpg"
            }
        }
        mock_get.return_value = mock_response
        
        api = ExternalAPIIntegration()
        result = api.fetch_product_by_barcode("1234567890")
        
        assert result is not None
        assert result['product_name'] == "Test Product"
        assert result['brands'] == "Test Brand"
    
    @patch('external_api.requests.get')
    def test_fetch_product_by_barcode_not_found(self, mock_get):
        """Test product fetch by barcode when not found."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": 0}
        mock_get.return_value = mock_response
        
        api = ExternalAPIIntegration()
        result = api.fetch_product_by_barcode("0000000000")
        
        assert result is None
    
    @patch('external_api.requests.get')
    def test_fetch_product_by_barcode_connection_error(self, mock_get):
        """Test product fetch by barcode with connection error."""
        from requests.exceptions import RequestException
        mock_get.side_effect = RequestException("Connection error")
        
        api = ExternalAPIIntegration()
        result = api.fetch_product_by_barcode("1234567890")
        
        assert result is None
    
    @patch('external_api.requests.get')
    def test_fetch_product_by_name_success(self, mock_get):
        """Test successful product fetch by name."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "products": [
                {
                    "product_name": "Test Product",
                    "brands": "Test Brand",
                    "code": "1234567890",
                    "categories": "Food",
                    "ingredients_text": "Ingredients",
                    "nutrition_grade_fr": "A"
                }
            ]
        }
        mock_get.return_value = mock_response
        
        api = ExternalAPIIntegration()
        results = api.fetch_product_by_name("Test Product")
        
        assert results is not None
        assert len(results) > 0
        assert results[0]['product_name'] == "Test Product"
    
    @patch('external_api.requests.get')
    def test_fetch_product_endpoint(self, mock_get, client):
        """Test POST /api/fetch-product endpoint."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": 1,
            "product": {
                "product_name": "Test Product",
                "brands": "Test Brand",
                "code": "1234567890",
                "categories": "Food",
                "ingredients_text": "Ingredients",
                "nutrition_grade_fr": "A"
            }
        }
        mock_get.return_value = mock_response
        
        response = client.post(
            '/api/fetch-product',
            data=json.dumps({"search_term": "1234567890", "search_type": "barcode"}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_fetch_product_missing_search_term(self, client):
        """Test POST /api/fetch-product without search term."""
        response = client.post(
            '/api/fetch-product',
            data=json.dumps({"search_type": "barcode"}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_fetch_product_invalid_search_type(self, client):
        """Test POST /api/fetch-product with invalid search type."""
        response = client.post(
            '/api/fetch-product',
            data=json.dumps({"search_term": "test", "search_type": "invalid"}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'


# ==================== ERROR HANDLER TESTS ====================

class TestErrorHandlers:
    """Test error handling."""
    
    def test_404_not_found(self, client):
        """Test 404 error handler."""
        response = client.get('/nonexistent/endpoint')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_405_method_not_allowed(self, client):
        """Test 405 error handler."""
        response = client.post('/health')
        
        assert response.status_code == 405
        data = json.loads(response.data)
        assert data['status'] == 'error'


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
