import json
import os
from datetime import datetime
from typing import Dict, List, Optional

# Path to our mock database
INVENTORY_FILE = "inventory.json"

def init_database():
    """Initialize the inventory database with mock data."""
    if not os.path.exists(INVENTORY_FILE):
        mock_data = [
            {
                "id": 1,
                "name": "Organic Almond Milk",
                "barcode": "5901234123457",
                "quantity": 50,
                "price": 4.99,
                "brand": "Silk",
                "category": "Beverages",
                "description": "Filtered water, almonds, cane sugar",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "external_api_data": {}
            },
            {
                "id": 2,
                "name": "Whole Wheat Bread",
                "barcode": "5901234123458",
                "quantity": 30,
                "price": 2.99,
                "brand": "Nature's Path",
                "category": "Bakery",
                "description": "Whole wheat flour, water, yeast, salt",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "external_api_data": {}
            },
            {
                "id": 3,
                "name": "Organic Tomato Sauce",
                "barcode": "5901234123459",
                "quantity": 75,
                "price": 2.49,
                "brand": "San Remo",
                "category": "Condiments",
                "description": "Tomatoes, garlic, olive oil, salt",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "external_api_data": {}
            }
        ]
        save_inventory(mock_data)
        return mock_data
    return load_inventory()

def load_inventory() -> List[Dict]:
    """Load inventory from JSON file."""
    try:
        with open(INVENTORY_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_inventory(inventory: List[Dict]):
    """Save inventory to JSON file."""
    with open(INVENTORY_FILE, 'w') as f:
        json.dump(inventory, f, indent=2)

def get_all_items() -> List[Dict]:
    """Get all inventory items."""
    return load_inventory()

def get_item_by_id(item_id: int) -> Optional[Dict]:
    """Get a single inventory item by ID."""
    items = load_inventory()
    for item in items:
        if item['id'] == item_id:
            return item
    return None

def create_item(item_data: Dict) -> Dict:
    """Create a new inventory item with basic field validation."""
    items = load_inventory()

    # Validate types
    if not isinstance(item_data.get('quantity', 0), (int, float)) or item_data.get('quantity', 0) < 0:
        raise ValueError("quantity must be a non-negative number")
    if not isinstance(item_data.get('price', 0.0), (int, float)) or item_data.get('price', 0.0) < 0:
        raise ValueError("price must be a non-negative number")

    # Generate new ID
    new_id = max([item['id'] for item in items], default=0) + 1
    
    new_item = {
        "id": new_id,
        "name": item_data.get("name"),
        "barcode": item_data.get("barcode"),
        "quantity": item_data.get("quantity", 0),
        "price": round(float(item_data.get("price", 0.0)), 2),
        "brand": item_data.get("brand"),
        "category": item_data.get("category", "Uncategorized"),
        "description": item_data.get("description", ""),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "external_api_data": item_data.get("external_api_data", {})
    }
    
    items.append(new_item)
    save_inventory(items)
    return new_item

def update_item(item_id: int, update_data: Dict) -> Optional[Dict]:
    """Update an existing inventory item."""
    items = load_inventory()
    
    for item in items:
        if item['id'] == item_id:
            # Update allowed fields
            for key in ['name', 'barcode', 'quantity', 'price', 'brand', 'category', 'description', 'external_api_data']:
                if key in update_data:
                    item[key] = update_data[key]
            item['updated_at'] = datetime.now().isoformat()
            save_inventory(items)
            return item
    
    return None

def delete_item(item_id: int) -> bool:
    """Delete an inventory item."""
    items = load_inventory()
    items = [item for item in items if item['id'] != item_id]
    
    if len(items) < len(load_inventory()):
        save_inventory(items)
        return True
    return False

def search_items_by_name(name: str) -> List[Dict]:
    """Search items by name (case-insensitive)."""
    items = load_inventory()
    return [item for item in items if name.lower() in item['name'].lower()]

def search_items_by_barcode(barcode: str) -> Optional[Dict]:
    """Search item by barcode."""
    items = load_inventory()
    for item in items:
        if item['barcode'] == barcode:
            return item
    return None


def bulk_delete_items(item_ids: List[int]) -> Dict:
    """
    Delete multiple inventory items at once.

    Args:
        item_ids: List of item IDs to delete

    Returns:
        Dict with counts of deleted and not-found IDs
    """
    items = load_inventory()
    existing_ids = {item['id'] for item in items}
    to_delete = set(item_ids)

    found = to_delete & existing_ids
    not_found = to_delete - existing_ids

    items = [item for item in items if item['id'] not in found]
    save_inventory(items)

    return {
        "deleted": sorted(found),
        "not_found": sorted(not_found),
        "deleted_count": len(found)
    }
