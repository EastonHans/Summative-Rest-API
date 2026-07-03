import requests
import json
from typing import Optional
from tabulate import tabulate

# API base URL (adjust if running on different host/port)
API_BASE_URL = "http://localhost:5000"

class InventoryCLI:
    """CLI tool for interacting with the Inventory Management API."""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
    
    # ==================== DISPLAY HELPERS ====================
    
    @staticmethod
    def print_header(title: str):
        """Print a formatted header."""
        print(f"\n{'=' * 60}")
        print(f"  {title}")
        print(f"{'=' * 60}\n")
    
    @staticmethod
    def print_success(message: str):
        """Print a success message."""
        print(f"✓ {message}")
    
    @staticmethod
    def print_error(message: str):
        """Print an error message."""
        print(f"✗ Error: {message}")
    
    @staticmethod
    def print_info(message: str):
        """Print an info message."""
        print(f"ℹ {message}")
    
    def display_items(self, items: list):
        """Display inventory items in a table format."""
        if not items:
            self.print_info("No items found.")
            return
        
        # Prepare table data
        table_data = []
        for item in items:
            table_data.append([
                item['id'],
                item['name'],
                item['barcode'],
                item['quantity'],
                f"${item['price']:.2f}",
                item['brand']
            ])
        
        headers = ['ID', 'Name', 'Barcode', 'Qty', 'Price', 'Brand']
        print(tabulate(table_data, headers=headers, tablefmt='grid'))
    
    def display_item_details(self, item: dict):
        """Display detailed information about a single item."""
        print("\n" + "=" * 60)
        print("INVENTORY ITEM DETAILS")
        print("=" * 60)
        
        details = [
            ['ID', item['id']],
            ['Name', item['name']],
            ['Barcode', item['barcode']],
            ['Brand', item['brand']],
            ['Category', item['category']],
            ['Quantity', item['quantity']],
            ['Price', f"${item['price']:.2f}"],
            ['Description', item['description']],
            ['Created At', item['created_at']],
            ['Updated At', item['updated_at']]
        ]
        
        if item.get('external_api_data'):
            print("\nEXTERNAL API DATA (OpenFoodFacts):")
            print("-" * 60)
            api_data = item['external_api_data']
            api_details = [
                ['Product Name', api_data.get('product_name', 'N/A')],
                ['Brands', api_data.get('brands', 'N/A')],
                ['Categories', api_data.get('categories', 'N/A')],
                ['Ingredients', api_data.get('ingredients_text', 'N/A')[:50] + '...'],
                ['Nutrition Grade', api_data.get('nutrition_grade', 'N/A')],
                ['Energy (kcal)', api_data.get('energy_kcal', 'N/A')]
            ]
            print(tabulate(api_details, tablefmt='plain'))
        
        print(tabulate(details, tablefmt='plain'))
        print("=" * 60 + "\n")
    
    # ==================== API OPERATIONS ====================
    
    def view_all_items(self):
        """View all inventory items."""
        try:
            self.print_header("ALL INVENTORY ITEMS")
            response = requests.get(f"{self.base_url}/inventory")
            
            if response.status_code == 200:
                data = response.json()
                items = data['data']
                self.print_info(f"Found {data['count']} items")
                self.display_items(items)
                return items
            else:
                self.print_error(response.json().get('message', 'Failed to fetch items'))
                return None
        
        except requests.exceptions.ConnectionError:
            self.print_error("Cannot connect to API. Is the server running?")
            return None
        except Exception as e:
            self.print_error(str(e))
            return None
    
    def view_item(self, item_id: int):
        """View details of a single item."""
        try:
            self.print_header(f"ITEM DETAILS (ID: {item_id})")
            response = requests.get(f"{self.base_url}/inventory/{item_id}")
            
            if response.status_code == 200:
                item = response.json()['data']
                self.display_item_details(item)
                return item
            else:
                self.print_error(response.json().get('message', 'Item not found'))
                return None
        
        except Exception as e:
            self.print_error(str(e))
            return None
    
    def search_by_name(self, name: str):
        """Search items by name."""
        try:
            self.print_header(f"SEARCH RESULTS FOR: {name}")
            response = requests.get(
                f"{self.base_url}/inventory/search/name",
                params={'q': name}
            )
            
            if response.status_code == 200:
                data = response.json()
                items = data['data']
                self.print_info(f"Found {data['count']} item(s)")
                self.display_items(items)
                return items
            else:
                self.print_error(response.json().get('message', 'Search failed'))
                return None
        
        except Exception as e:
            self.print_error(str(e))
            return None
    
    def search_by_barcode(self, barcode: str):
        """Search item by barcode."""
        try:
            self.print_header(f"SEARCH BY BARCODE: {barcode}")
            response = requests.get(
                f"{self.base_url}/inventory/search/barcode",
                params={'barcode': barcode}
            )
            
            if response.status_code == 200:
                item = response.json()['data']
                self.display_item_details(item)
                return item
            else:
                self.print_error(response.json().get('message', 'Item not found'))
                return None
        
        except Exception as e:
            self.print_error(str(e))
            return None
    
    def add_item(self, name: str, barcode: str, quantity: int, price: float, brand: str, category: str = "", description: str = ""):
        """Add a new inventory item."""
        try:
            self.print_header("ADD NEW ITEM")
            
            payload = {
                "name": name,
                "barcode": barcode,
                "quantity": int(quantity),
                "price": float(price),
                "brand": brand,
                "category": category or "Uncategorized",
                "description": description or ""
            }
            
            response = requests.post(
                f"{self.base_url}/inventory",
                json=payload
            )
            
            if response.status_code == 201:
                item = response.json()['data']
                self.print_success(f"Item created successfully (ID: {item['id']})")
                self.display_item_details(item)
                return item
            else:
                self.print_error(response.json().get('message', 'Failed to create item'))
                return None
        
        except Exception as e:
            self.print_error(str(e))
            return None
    
    def update_item(self, item_id: int, **kwargs):
        """Update an inventory item."""
        try:
            self.print_header(f"UPDATE ITEM (ID: {item_id})")
            
            # Remove None values from kwargs
            payload = {k: v for k, v in kwargs.items() if v is not None}
            
            if not payload:
                self.print_error("No fields to update")
                return None
            
            response = requests.patch(
                f"{self.base_url}/inventory/{item_id}",
                json=payload
            )
            
            if response.status_code == 200:
                item = response.json()['data']
                self.print_success("Item updated successfully")
                self.display_item_details(item)
                return item
            else:
                self.print_error(response.json().get('message', 'Failed to update item'))
                return None
        
        except Exception as e:
            self.print_error(str(e))
            return None
    
    def delete_item(self, item_id: int):
        """Delete an inventory item."""
        try:
            self.print_header(f"DELETE ITEM (ID: {item_id})")
            
            # Confirm deletion
            confirm = input(f"Are you sure you want to delete item {item_id}? (yes/no): ").lower()
            if confirm != 'yes':
                self.print_info("Deletion cancelled")
                return False
            
            response = requests.delete(f"{self.base_url}/inventory/{item_id}")
            
            if response.status_code == 200:
                self.print_success(response.json().get('message', 'Item deleted successfully'))
                return True
            else:
                self.print_error(response.json().get('message', 'Failed to delete item'))
                return False
        
        except Exception as e:
            self.print_error(str(e))
            return False
    
    def fetch_from_api(self, search_term: str, search_type: str = "barcode"):
        """Fetch product from OpenFoodFacts API."""
        try:
            self.print_header(f"FETCH FROM OPENFOODFACTS ({search_type.upper()})")
            
            payload = {
                "search_term": search_term,
                "search_type": search_type
            }
            
            response = requests.post(
                f"{self.base_url}/api/fetch-product",
                json=payload
            )
            
            if response.status_code == 200:
                product = response.json()['data']
                self.print_success(f"Product found: {product['product_name']}")
                self._display_api_product(product)
                return product
            else:
                self.print_error(response.json().get('message', 'Product not found'))
                return None
        
        except Exception as e:
            self.print_error(str(e))
            return None
    
    def enrich_item(self, item_id: int, search_type: str = "barcode"):
        """Enrich an inventory item with OpenFoodFacts data."""
        try:
            self.print_header(f"ENRICH ITEM {item_id} WITH OPENFOODFACTS DATA")
            
            payload = {"search_type": search_type}
            
            response = requests.post(
                f"{self.base_url}/api/enrich-item/{item_id}",
                json=payload
            )
            
            if response.status_code == 200:
                item = response.json()['data']
                self.print_success("Item enriched with external API data")
                self.display_item_details(item)
                return item
            else:
                self.print_error(response.json().get('message', 'Failed to enrich item'))
                return None
        
        except Exception as e:
            self.print_error(str(e))
            return None
    
    @staticmethod
    def _display_api_product(product: dict):
        """Display OpenFoodFacts product details."""
        details = [
            ['Product Name', product.get('product_name', 'N/A')],
            ['Brands', product.get('brands', 'N/A')],
            ['Barcode', product.get('barcode', 'N/A')],
            ['Categories', product.get('categories', 'N/A')],
            ['Ingredients', product.get('ingredients_text', 'N/A')[:50] + '...'],
            ['Nutrition Grade', product.get('nutrition_grade', 'N/A')],
            ['Energy (kcal/100g)', product.get('energy_kcal', 'N/A')],
            ['Fat (g/100g)', product.get('fat', 'N/A')],
            ['Carbs (g/100g)', product.get('carbohydrates', 'N/A')],
            ['Protein (g/100g)', product.get('proteins', 'N/A')],
        ]
        print(tabulate(details, tablefmt='plain'))
        print()


def display_menu():
    """Display the main menu."""
    print("\n" + "=" * 60)
    print("  INVENTORY MANAGEMENT SYSTEM - CLI")
    print("=" * 60)
    print("""
1.  View all inventory items
2.  View item details
3.  Search by name
4.  Search by barcode
5.  Add new item
6.  Update item
7.  Delete item
8.  Fetch product from OpenFoodFacts
9.  Enrich item with OpenFoodFacts data
10. Exit
    """)
    print("=" * 60)


def get_input(prompt: str, input_type=str, required=True):
    """Get user input with validation."""
    while True:
        try:
            user_input = input(prompt).strip()
            if required and not user_input:
                print("This field is required. Please try again.")
                continue
            if input_type == int:
                return int(user_input)
            elif input_type == float:
                return float(user_input)
            return user_input
        except ValueError:
            print(f"Invalid input. Please enter a valid {input_type.__name__}")


def main():
    """Main CLI application loop."""
    cli = InventoryCLI()
    
    print("\nWelcome to the Inventory Management System!")
    print("Make sure the Flask API server is running (python app.py)")
    
    while True:
        display_menu()
        choice = get_input("Enter your choice (1-10): ")
        
        try:
            if choice == '1':
                cli.view_all_items()
            
            elif choice == '2':
                item_id = get_input("Enter item ID: ", int)
                cli.view_item(item_id)
            
            elif choice == '3':
                name = get_input("Enter product name to search: ")
                cli.search_by_name(name)
            
            elif choice == '4':
                barcode = get_input("Enter barcode to search: ")
                cli.search_by_barcode(barcode)
            
            elif choice == '5':
                print("\n--- Add New Item ---")
                name = get_input("Product name: ")
                barcode = get_input("Barcode: ")
                quantity = get_input("Quantity: ", int)
                price = get_input("Price: ", float)
                brand = get_input("Brand: ")
                category = get_input("Category (optional): ", required=False)
                description = get_input("Description (optional): ", required=False)
                cli.add_item(name, barcode, quantity, price, brand, category, description)
            
            elif choice == '6':
                item_id = get_input("Enter item ID to update: ", int)
                print("\n--- Update Item (leave blank to skip) ---")
                name = get_input("Product name: ", required=False)
                quantity = get_input("Quantity: ", required=False)
                price = get_input("Price: ", required=False)
                
                update_data = {
                    'name': name if name else None,
                    'quantity': int(quantity) if quantity else None,
                    'price': float(price) if price else None
                }
                cli.update_item(item_id, **update_data)
            
            elif choice == '7':
                item_id = get_input("Enter item ID to delete: ", int)
                cli.delete_item(item_id)
            
            elif choice == '8':
                search_type = get_input("Search by (barcode/name): ").lower()
                if search_type not in ['barcode', 'name']:
                    print("Invalid search type. Please use 'barcode' or 'name'")
                    continue
                search_term = get_input(f"Enter {search_type}: ")
                cli.fetch_from_api(search_term, search_type)
            
            elif choice == '9':
                item_id = get_input("Enter item ID to enrich: ", int)
                search_type = get_input("Search by (barcode/name) [default: barcode]: ", required=False) or "barcode"
                cli.enrich_item(item_id, search_type)
            
            elif choice == '10':
                print("\nThank you for using Inventory Management System!")
                break
            
            else:
                print("Invalid choice. Please try again.")
        
        except KeyboardInterrupt:
            print("\n\nApplication interrupted by user.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            continue


if __name__ == '__main__':
    main()
