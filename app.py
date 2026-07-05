from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from database import (
    init_database, get_all_items, get_item_by_id, create_item,
    update_item, delete_item, search_items_by_name, search_items_by_barcode,
    bulk_delete_items
)
from external_api import fetch_product_details

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)

# Initialize database with mock data on startup
init_database()


# ==================== INVENTORY ENDPOINTS ====================

@app.route('/inventory', methods=['GET'])
def get_inventory():
    """
    GET /inventory → Fetch all items
    
    Returns:
        JSON array of all inventory items
    """
    try:
        items = get_all_items()
        return jsonify({
            "status": "success",
            "data": items,
            "count": len(items)
        }), 200
    except Exception as e:
        logger.error(f"Error fetching inventory: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/inventory/<int:item_id>', methods=['GET'])
def get_single_item(item_id):
    """
    GET /inventory/<id> → Fetch a single item
    
    Args:
        item_id: ID of the inventory item
        
    Returns:
        JSON object of the item or 404 if not found
    """
    try:
        item = get_item_by_id(item_id)
        if item:
            return jsonify({
                "status": "success",
                "data": item
            }), 200
        return jsonify({
            "status": "error",
            "message": f"Item with ID {item_id} not found"
        }), 404
    except Exception as e:
        logger.error(f"Error fetching item {item_id}: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/inventory', methods=['POST'])
def add_item():
    """
    POST /inventory → Add a new item
    
    Request body (JSON):
        {
            "name": "Product Name",
            "barcode": "1234567890",
            "quantity": 100,
            "price": 9.99,
            "brand": "Brand Name",
            "category": "Category",
            "description": "Product description"
        }
        
    Returns:
        JSON object of created item with 201 status
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'barcode', 'quantity', 'price', 'brand']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "status": "error",
                    "message": f"Missing required field: {field}"
                }), 400
        
        new_item = create_item(data)
        
        return jsonify({
            "status": "success",
            "data": new_item,
            "message": "Item created successfully"
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating item: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/inventory/<int:item_id>', methods=['PATCH'])
def update_single_item(item_id):
    """
    PATCH /inventory/<id> → Update an item
    
    Args:
        item_id: ID of the inventory item
        
    Request body (JSON):
        {
            "quantity": 50,
            "price": 8.99,
            // Any other updatable fields
        }
        
    Returns:
        JSON object of updated item or 404 if not found
    """
    try:
        data = request.get_json()
        updated_item = update_item(item_id, data)
        
        if updated_item:
            return jsonify({
                "status": "success",
                "data": updated_item,
                "message": "Item updated successfully"
            }), 200
        
        return jsonify({
            "status": "error",
            "message": f"Item with ID {item_id} not found"
        }), 404
        
    except Exception as e:
        logger.error(f"Error updating item {item_id}: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/inventory/<int:item_id>', methods=['DELETE'])
def remove_item(item_id):
    """
    DELETE /inventory/<id> → Remove an item
    
    Args:
        item_id: ID of the inventory item
        
    Returns:
        Success/error message
    """
    try:
        if delete_item(item_id):
            return jsonify({
                "status": "success",
                "message": f"Item with ID {item_id} deleted successfully"
            }), 200
        
        return jsonify({
            "status": "error",
            "message": f"Item with ID {item_id} not found"
        }), 404
        
    except Exception as e:
        logger.error(f"Error deleting item {item_id}: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/inventory/bulk-delete', methods=['DELETE'])
def bulk_delete():
    """
    DELETE /inventory/bulk-delete → Remove multiple items at once.

    Request body (JSON):
        {
            "ids": [1, 2, 3]
        }

    Returns:
        JSON with deleted and not_found ID lists
    """
    try:
        data = request.get_json()
        if not data or 'ids' not in data or not isinstance(data['ids'], list):
            return jsonify({
                "status": "error",
                "message": "'ids' must be a list of item IDs"
            }), 400

        result = bulk_delete_items(data['ids'])
        return jsonify({
            "status": "success",
            "data": result,
            "message": f"{result['deleted_count']} item(s) deleted"
        }), 200

    except Exception as e:
        logger.error(f"Error in bulk delete: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ==================== SEARCH ENDPOINTS ====================

@app.route('/inventory/search/name', methods=['GET'])
def search_by_name():
    """
    GET /inventory/search/name?q=<search_term>
    Search inventory items by name
    
    Query params:
        q: Search term
        
    Returns:
        JSON array of matching items
    """
    try:
        search_term = request.args.get('q', '')
        
        if not search_term:
            return jsonify({
                "status": "error",
                "message": "Search term 'q' is required"
            }), 400
        
        items = search_items_by_name(search_term)
        return jsonify({
            "status": "success",
            "data": items,
            "count": len(items)
        }), 200
        
    except Exception as e:
        logger.error(f"Error searching by name: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/inventory/search/barcode', methods=['GET'])
def search_by_barcode():
    """
    GET /inventory/search/barcode?barcode=<barcode>
    Search inventory item by barcode
    
    Query params:
        barcode: Product barcode
        
    Returns:
        JSON object of matching item or 404
    """
    try:
        barcode = request.args.get('barcode', '')
        
        if not barcode:
            return jsonify({
                "status": "error",
                "message": "Barcode parameter is required"
            }), 400
        
        item = search_items_by_barcode(barcode)
        if item:
            return jsonify({
                "status": "success",
                "data": item
            }), 200
        
        return jsonify({
            "status": "error",
            "message": f"Item with barcode {barcode} not found"
        }), 404
        
    except Exception as e:
        logger.error(f"Error searching by barcode: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ==================== EXTERNAL API ENDPOINTS ====================

@app.route('/api/fetch-product', methods=['POST'])
def fetch_product():
    """
    POST /api/fetch-product
    Fetch product details from OpenFoodFacts API
    
    Request body (JSON):
        {
            "search_term": "barcode_or_name",
            "search_type": "barcode" | "name"
        }
        
    Returns:
        Product details from OpenFoodFacts or error
    """
    try:
        data = request.get_json()
        search_term = data.get('search_term')
        search_type = data.get('search_type', 'barcode')
        
        if not search_term:
            return jsonify({
                "status": "error",
                "message": "search_term is required"
            }), 400
        
        if search_type not in ['barcode', 'name']:
            return jsonify({
                "status": "error",
                "message": "search_type must be 'barcode' or 'name'"
            }), 400
        
        product_data = fetch_product_details(search_term, search_type)
        
        if product_data:
            return jsonify({
                "status": "success",
                "data": product_data
            }), 200
        
        return jsonify({
            "status": "error",
            "message": f"Product not found for {search_type}: {search_term}"
        }), 404
        
    except Exception as e:
        logger.error(f"Error fetching product: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/enrich-item/<int:item_id>', methods=['POST'])
def enrich_item_with_api(item_id):
    """
    POST /api/enrich-item/<id>
    Enrich an inventory item with data from OpenFoodFacts API
    
    Args:
        item_id: ID of the inventory item
        
    Request body (JSON):
        {
            "search_type": "barcode" | "name"
        }
        
    Returns:
        Updated item with external API data
    """
    try:
        item = get_item_by_id(item_id)
        if not item:
            return jsonify({
                "status": "error",
                "message": f"Item with ID {item_id} not found"
            }), 404
        
        data = request.get_json() or {}
        search_type = data.get('search_type', 'barcode')
        search_term = item['barcode'] if search_type == 'barcode' else item['name']
        
        product_data = fetch_product_details(search_term, search_type)
        
        if product_data:
            item['external_api_data'] = product_data
            updated_item = update_item(item_id, {'external_api_data': product_data})
            return jsonify({
                "status": "success",
                "data": updated_item,
                "message": "Item enriched with external API data"
            }), 200
        
        return jsonify({
            "status": "error",
            "message": f"Product not found for {search_type}: {search_term}"
        }), 404
        
    except Exception as e:
        logger.error(f"Error enriching item: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ==================== HEALTH CHECK ====================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "Inventory Management System"
    }), 200


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "status": "error",
        "message": "Endpoint not found"
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors."""
    return jsonify({
        "status": "error",
        "message": "Method not allowed"
    }), 405


@app.errorhandler(500)
def internal_server_error(error):
    """Handle 500 errors."""
    return jsonify({
        "status": "error",
        "message": "Internal server error"
    }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
