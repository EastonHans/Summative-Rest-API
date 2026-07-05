from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from database import (
    init_database, get_all_items, get_item_by_id, create_item,
    update_item, delete_item, search_items_by_name, search_items_by_barcode,
    bulk_delete_items
)
from external_api import fetch_product_details

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

init_database()


@app.route('/inventory', methods=['GET'])
def get_inventory():
    try:
        items = get_all_items()

        page = request.args.get('page', type=int)
        per_page = request.args.get('per_page', default=10, type=int)

        if page is not None:
            start = (page - 1) * per_page
            end = start + per_page
            paginated = items[start:end]
            return jsonify({
                "status": "success",
                "data": paginated,
                "count": len(paginated),
                "total": len(items),
                "page": page,
                "per_page": per_page,
                "total_pages": (len(items) + per_page - 1) // per_page
            }), 200

        return jsonify({
            "status": "success",
            "data": items,
            "count": len(items)
        }), 200
    except Exception as e:
        logger.error(f"Error fetching inventory: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/inventory/stats', methods=['GET'])
def inventory_stats():
    try:
        items = get_all_items()

        if not items:
            return jsonify({
                "status": "success",
                "data": {"total_items": 0, "total_quantity": 0, "average_price": 0, "categories": {}}
            }), 200

        total_quantity = sum(i.get('quantity', 0) for i in items)
        average_price = round(sum(i.get('price', 0) for i in items) / len(items), 2)

        categories = {}
        for item in items:
            cat = item.get('category', 'Uncategorized')
            categories[cat] = categories.get(cat, 0) + 1

        return jsonify({
            "status": "success",
            "data": {
                "total_items": len(items),
                "total_quantity": total_quantity,
                "average_price": average_price,
                "categories": categories
            }
        }), 200

    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/inventory/<int:item_id>', methods=['GET'])
def get_single_item(item_id):
    try:
        item = get_item_by_id(item_id)
        if item:
            return jsonify({"status": "success", "data": item}), 200
        return jsonify({"status": "error", "message": f"Item with ID {item_id} not found"}), 404
    except Exception as e:
        logger.error(f"Error fetching item {item_id}: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/inventory', methods=['POST'])
def add_item():
    try:
        data = request.get_json()

        required_fields = ['name', 'barcode', 'quantity', 'price', 'brand']
        for field in required_fields:
            if field not in data:
                return jsonify({"status": "error", "message": f"Missing required field: {field}"}), 400

        new_item = create_item(data)
        return jsonify({
            "status": "success",
            "data": new_item,
            "message": "Item created successfully"
        }), 201

    except Exception as e:
        logger.error(f"Error creating item: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/inventory/<int:item_id>', methods=['PATCH'])
def update_single_item(item_id):
    try:
        data = request.get_json()
        updated_item = update_item(item_id, data)

        if updated_item:
            return jsonify({
                "status": "success",
                "data": updated_item,
                "message": "Item updated successfully"
            }), 200

        return jsonify({"status": "error", "message": f"Item with ID {item_id} not found"}), 404

    except Exception as e:
        logger.error(f"Error updating item {item_id}: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/inventory/<int:item_id>', methods=['DELETE'])
def remove_item(item_id):
    try:
        if delete_item(item_id):
            return jsonify({
                "status": "success",
                "message": f"Item with ID {item_id} deleted successfully"
            }), 200
        return jsonify({"status": "error", "message": f"Item with ID {item_id} not found"}), 404

    except Exception as e:
        logger.error(f"Error deleting item {item_id}: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/inventory/bulk-delete', methods=['DELETE'])
def bulk_delete():
    try:
        data = request.get_json()
        if not data or 'ids' not in data or not isinstance(data['ids'], list):
            return jsonify({"status": "error", "message": "'ids' must be a list of item IDs"}), 400

        result = bulk_delete_items(data['ids'])
        return jsonify({
            "status": "success",
            "data": result,
            "message": f"{result['deleted_count']} item(s) deleted"
        }), 200

    except Exception as e:
        logger.error(f"Error in bulk delete: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/inventory/search/name', methods=['GET'])
def search_by_name():
    try:
        search_term = request.args.get('q', '')
        if not search_term:
            return jsonify({"status": "error", "message": "Search term 'q' is required"}), 400

        items = search_items_by_name(search_term)
        return jsonify({"status": "success", "data": items, "count": len(items)}), 200

    except Exception as e:
        logger.error(f"Error searching by name: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/inventory/search/barcode', methods=['GET'])
def search_by_barcode():
    try:
        barcode = request.args.get('barcode', '')
        if not barcode:
            return jsonify({"status": "error", "message": "Barcode parameter is required"}), 400

        item = search_items_by_barcode(barcode)
        if item:
            return jsonify({"status": "success", "data": item}), 200
        return jsonify({"status": "error", "message": f"Item with barcode {barcode} not found"}), 404

    except Exception as e:
        logger.error(f"Error searching by barcode: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/fetch-product', methods=['POST'])
def fetch_product():
    try:
        data = request.get_json()
        search_term = data.get('search_term')
        search_type = data.get('search_type', 'barcode')

        if not search_term:
            return jsonify({"status": "error", "message": "search_term is required"}), 400

        if search_type not in ['barcode', 'name']:
            return jsonify({"status": "error", "message": "search_type must be 'barcode' or 'name'"}), 400

        product_data = fetch_product_details(search_term, search_type)

        if product_data:
            return jsonify({"status": "success", "data": product_data}), 200
        return jsonify({"status": "error", "message": f"Product not found for {search_type}: {search_term}"}), 404

    except Exception as e:
        logger.error(f"Error fetching product: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/enrich-item/<int:item_id>', methods=['POST'])
def enrich_item_with_api(item_id):
    try:
        item = get_item_by_id(item_id)
        if not item:
            return jsonify({"status": "error", "message": f"Item with ID {item_id} not found"}), 404

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

        return jsonify({"status": "error", "message": f"Product not found for {search_type}: {search_term}"}), 404

    except Exception as e:
        logger.error(f"Error enriching item: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "Inventory Management System"}), 200


@app.errorhandler(404)
def not_found(error):
    return jsonify({"status": "error", "message": "Endpoint not found"}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"status": "error", "message": "Method not allowed"}), 405


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"status": "error", "message": "Internal server error"}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
