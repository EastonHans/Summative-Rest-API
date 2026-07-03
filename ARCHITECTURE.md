# API Architecture & Design Document

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Design](#architecture-design)
3. [Module Breakdown](#module-breakdown)
4. [Design Patterns](#design-patterns)
5. [Data Flow](#data-flow)
6. [External API Integration](#external-api-integration)
7. [Error Handling Strategy](#error-handling-strategy)
8. [Security Considerations](#security-considerations)
9. [Scalability & Performance](#scalability--performance)

---

## System Overview

The Inventory Management System is a three-tier REST API designed to manage e-commerce inventory with real-time enrichment from external product databases.

### Key Components
- **Flask REST API Server** - Handles HTTP requests and business logic
- **JSON-based Database** - Simple file storage for inventory data
- **External API Client** - Integrates with OpenFoodFacts API
- **CLI Interface** - User-friendly command-line tool
- **Test Suite** - Comprehensive unit tests with 36 test cases

### Technology Stack
- **Framework**: Flask 2.3.2 with Flask-CORS
- **Runtime**: Python 3.7+
- **External APIs**: OpenFoodFacts REST API
- **Testing**: pytest with mocking
- **Data Format**: JSON
- **HTTP Methods**: GET, POST, PATCH, DELETE (RESTful)

---

## Architecture Design

### Layered Architecture

```
┌─────────────────────────────────────────┐
│         CLI Interface Layer             │
│  (cli.py - User Interaction)            │
├─────────────────────────────────────────┤
│      Flask API Layer (app.py)           │
│  - Route Handlers                       │
│  - Request Validation                   │
│  - Response Formatting                  │
├─────────────────────────────────────────┤
│    Business Logic & Data Layer          │
│  - database.py (CRUD operations)        │
│  - external_api.py (External services) │
├─────────────────────────────────────────┤
│       Storage & External Services       │
│  - inventory.json (Local storage)       │
│  - OpenFoodFacts API (Remote service)   │
└─────────────────────────────────────────┘
```

### Component Interaction

```
User
  ↓
CLI Interface (cli.py)
  ↓
[API Requests - HTTP/JSON]
  ↓
Flask Application (app.py)
  ├─→ Route Handlers
  ├─→ Request Validation
  └─→ Response Formatting
  ↓
Business Logic (database.py)
  ├─→ CRUD Operations
  ├─→ Search Functions
  └─→ Data Validation
  ↓
Storage & External Services
  ├─→ inventory.json (File I/O)
  └─→ external_api.py
      └─→ OpenFoodFacts API
```

---

## Module Breakdown

### 1. app.py - Flask Application Layer

**Responsibilities:**
- Route definition and HTTP request handling
- Request validation and error handling
- Response formatting and HTTP status codes
- CORS configuration for cross-origin requests

**Key Functions:**
- Route decorators (@app.route)
- Error handlers for HTTP errors
- JSON request/response handling

**Example Flow:**
```python
@app.route('/inventory', methods=['POST'])
def add_item():
    # 1. Extract JSON data
    data = request.get_json()
    
    # 2. Validate required fields
    validate_required_fields(data)
    
    # 3. Call business logic
    new_item = create_item(data)
    
    # 4. Format response
    return jsonify({
        "status": "success",
        "data": new_item,
        "message": "Item created successfully"
    }), 201
```

### 2. database.py - Data Layer

**Responsibilities:**
- CRUD operations (Create, Read, Update, Delete)
- JSON file I/O operations
- Search functionality
- Data persistence

**Key Functions:**
```
- init_database()          # Initialize with mock data
- load_inventory()         # Read from JSON
- save_inventory()         # Write to JSON
- create_item()            # Add new item
- get_item_by_id()         # Retrieve single item
- get_all_items()          # Retrieve all items
- update_item()            # Modify item
- delete_item()            # Remove item
- search_items_by_name()   # Search by name
- search_items_by_barcode()# Search by barcode
```

**Data Structure:**
```json
{
  "id": 1,
  "name": "Product",
  "barcode": "123456",
  "quantity": 50,
  "price": 9.99,
  "brand": "Brand",
  "category": "Category",
  "description": "Description",
  "created_at": "ISO-8601 timestamp",
  "updated_at": "ISO-8601 timestamp",
  "external_api_data": {}
}
```

### 3. external_api.py - External Service Integration

**Responsibilities:**
- OpenFoodFacts API communication
- Product data fetching and formatting
- Error handling for external services
- Response standardization

**Key Functions:**
```
- ExternalAPIIntegration.__init__()
- fetch_product_by_barcode()
- fetch_product_by_name()
- _format_product_data()
- fetch_product_details()  # Wrapper function
```

**API Response Handling:**
```python
# OpenFoodFacts returns:
{
  "status": 1,
  "product": {
    "product_name": "...",
    "brands": "...",
    "code": "...",
    ...
  }
}

# We format to:
{
  "product_name": "...",
  "brands": "...",
  "barcode": "...",
  "categories": "...",
  ...
}
```

### 4. cli.py - User Interface Layer

**Responsibilities:**
- Interactive user menu
- Input collection and validation
- API endpoint calls
- Output formatting and display
- Error message presentation

**Key Classes:**
- `InventoryCLI` - Main CLI handler
- Display methods for formatted output
- Menu-driven interaction

**Menu Options:**
```
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
```

### 5. test_app.py - Testing Suite

**Responsibilities:**
- Unit test coverage for all modules
- Integration tests for API endpoints
- Mock external API calls
- Fixture management

**Test Classes:**
- `TestDatabase` (12 tests) - Database operations
- `TestAPIEndpoints` (14 tests) - API route testing
- `TestExternalAPI` (8 tests) - External API integration
- `TestErrorHandlers` (2 tests) - Error handling

---

## Design Patterns

### 1. MVC Pattern (Modified)

```
Model: database.py
├─ Handles data structure
└─ Manages persistence

View: cli.py
├─ Displays data to user
└─ Collects user input

Controller: app.py
├─ Routes requests
├─ Calls appropriate models
└─ Returns responses
```

### 2. Singleton Pattern

```python
# external_api.py
api_client = ExternalAPIIntegration()

# Used globally throughout application
def fetch_product_details(search_term, search_type):
    # Uses singleton instance
    return api_client.fetch_product_by_barcode(search_term)
```

### 3. Repository Pattern

```python
# database.py acts as repository
class InventoryRepository:
    - Abstracts data storage details
    - Provides clean interface for data access
    - Handles JSON serialization/deserialization
```

### 4. Adapter Pattern

```python
# external_api.py adapts OpenFoodFacts API to our format
def _format_product_data(product):
    """
    Converts OpenFoodFacts response format
    to our standardized format
    """
    return {
        "product_name": product.get("product_name"),
        "brands": product.get("brands"),
        ...
    }
```

### 5. Error Handling Pattern

```python
# Consistent error handling across all layers
try:
    # Perform operation
except SpecificException:
    # Log error
    logger.error(f"Error: {e}")
    # Return error response
    return jsonify({"status": "error", "message": str(e)}), 400
```

---

## Data Flow

### Adding an Item

```sequence
User → CLI.add_item()
  ↓
User inputs: name, barcode, quantity, price, brand, category, description
  ↓
CLI.add_item() → POST /inventory
  ↓
app.py add_item() handler
  ├─ Extract JSON data
  ├─ Validate required fields
  └─ Call database.create_item()
  ↓
database.py create_item()
  ├─ Load existing inventory
  ├─ Generate new ID
  ├─ Create new item object
  ├─ Append to inventory array
  ├─ Save to inventory.json
  └─ Return new item
  ↓
app.py returns JSON response (201 Created)
  ↓
CLI displays success message and item details
```

### Enriching Item with External Data

```sequence
User → CLI.enrich_item(item_id)
  ↓
CLI calls POST /api/enrich-item/<id>
  ↓
app.py enrich_item_with_api() handler
  ├─ Get item by ID from database
  ├─ Extract barcode or name
  └─ Call external_api.fetch_product_details()
  ↓
external_api.py fetch_product_details()
  ├─ Prepare API request
  ├─ Call requests.get() to OpenFoodFacts
  ├─ Parse response JSON
  └─ Format data with _format_product_data()
  ↓
OpenFoodFacts API returns product data
  ↓
external_api.py returns formatted data
  ↓
app.py calls database.update_item()
  ├─ Load existing item
  ├─ Update external_api_data field
  ├─ Update updated_at timestamp
  ├─ Save to inventory.json
  └─ Return updated item
  ↓
app.py returns JSON response (200 OK)
  ↓
CLI displays enriched item details with API data
```

### Searching Items

```sequence
User → CLI.search_by_name("Almond")
  ↓
CLI calls GET /inventory/search/name?q=Almond
  ↓
app.py search_by_name() handler
  ├─ Extract query parameter
  ├─ Call database.search_items_by_name()
  └─ Return matching items
  ↓
database.py search_items_by_name()
  ├─ Load inventory from JSON
  ├─ Filter items (case-insensitive partial match)
  └─ Return matching items array
  ↓
app.py returns JSON response (200 OK)
  ↓
CLI displays results in table format
```

---

## External API Integration

### OpenFoodFacts API

**Endpoints Used:**
```
GET /api/v0/product/{barcode}.json
GET /api/v0/cgi/search.pl?search_terms={name}&json=1
```

**Request Example:**
```bash
curl "https://world.openfoodfacts.org/api/v0/product/5901234123457.json"
```

**Response Mapping:**
```
OpenFoodFacts Field    →    Our Field
product_name           →    product_name
brands                 →    brands
code                   →    barcode
categories             →    categories
ingredients_text       →    ingredients_text
nutrition_grade_fr     →    nutrition_grade
energy_kcal_100g       →    energy_kcal
fat_100g               →    fat
carbohydrates_100g     →    carbohydrates
proteins_100g          →    proteins
image_front_url        →    image_url
url                    →    url
```

**Error Handling:**
```python
try:
    response = requests.get(url, timeout=5)
    if response.status_code == 200:
        data = response.json()
        if data.get("status") == 1 and "product" in data:
            return format_product_data(data["product"])
    return None
except requests.exceptions.RequestException as e:
    logger.error(f"API request failed: {e}")
    return None
```

---

## Error Handling Strategy

### HTTP Status Codes

```
200 OK              - Successful GET, PATCH, DELETE
201 Created         - POST successful
400 Bad Request     - Invalid input, missing fields
404 Not Found       - Resource doesn't exist
405 Not Allowed     - Wrong HTTP method
500 Server Error    - Unexpected error
```

### Response Format

**Success:**
```json
{
  "status": "success",
  "data": { ... },
  "count": N,
  "message": "Operation successful"
}
```

**Error:**
```json
{
  "status": "error",
  "message": "Descriptive error message"
}
```

### Error Handling Layers

**1. Input Validation (app.py)**
```python
if not data.get('name'):
    return jsonify({
        "status": "error",
        "message": "Missing required field: name"
    }), 400
```

**2. Business Logic (database.py)**
```python
if not item:
    return None  # Handled by app.py
```

**3. External API (external_api.py)**
```python
try:
    response = requests.get(url)
except RequestException as e:
    logger.error(f"API error: {e}")
    return None
```

**4. HTTP Error Handlers (app.py)**
```python
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "status": "error",
        "message": "Endpoint not found"
    }), 404
```

---

## Security Considerations

### Current Implementation
- No authentication/authorization
- CORS enabled for all origins
- No input sanitization (development mode)
- JSON file accessible locally

### Production Recommendations

1. **Authentication**
   - Implement JWT tokens
   - API key management
   - OAuth2 for third-party access

2. **Authorization**
   - Role-based access control (RBAC)
   - Resource-level permissions
   - Admin vs. employee roles

3. **Data Protection**
   - Use HTTPS/TLS for all communications
   - Encrypt sensitive data
   - Hash passwords if using user system
   - Implement CORS properly

4. **Input Validation**
   - Sanitize all inputs
   - Validate data types and ranges
   - Implement rate limiting
   - Use parameterized queries

5. **API Security**
   - Rate limiting and throttling
   - Request signature verification
   - API versioning (v1, v2, etc.)
   - Request logging and monitoring

---

## Scalability & Performance

### Current Architecture Limitations
- Single-threaded Flask development server
- JSON file I/O (not suitable for high-load)
- In-memory data loading for searches
- No caching mechanism

### Scalability Improvements

1. **Database**
   ```
   Current:  JSON file
   Upgrade:  PostgreSQL / MongoDB
   Benefits: Better concurrency, query optimization
   ```

2. **Caching**
   ```
   Add: Redis cache layer
   Cache: Frequently accessed items, API responses
   Benefits: Faster response times, reduced API calls
   ```

3. **API Gateway**
   ```
   Add: nginx / Kong
   Features: Load balancing, rate limiting, authentication
   ```

4. **Asynchronous Processing**
   ```
   Add: Celery + Redis
   Use: Long-running operations, background jobs
   ```

5. **Horizontal Scaling**
   ```
   Deploy: Multiple API instances
   Use: Load balancer for distribution
   ```

### Performance Metrics

**Current Performance:**
- Single item retrieval: ~1-5ms
- Search operation: ~5-20ms (depends on dataset size)
- External API call: ~200-500ms (network dependent)
- Full inventory load: ~1-10ms (JSON file I/O)

**Optimization Strategies:**
- Implement pagination for large datasets
- Add database indexing
- Use caching for frequent queries
- Optimize JSON serialization
- Connection pooling for external APIs

---

## Deployment Architecture

### Development
```
Developer Machine
├─ Flask dev server (port 5000)
├─ JSON file storage
└─ Direct API calls
```

### Staging
```
Staging Environment
├─ Docker container
├─ SQLite database
├─ External API integration
└─ Testing endpoints
```

### Production
```
Production Environment
├─ Kubernetes cluster
├─ Load balancer
├─ PostgreSQL database
├─ Redis cache
├─ nginx reverse proxy
├─ CDN for static assets
└─ Monitoring & logging
```

---

## API Versioning Strategy

### Current Version: v1

For future versions:
```
GET /api/v1/inventory    # Current
GET /api/v2/inventory    # Future changes
```

**Version Management:**
- Maintain backward compatibility
- Deprecation notice before removal
- Support multiple versions simultaneously
- Document breaking changes

---

## Monitoring & Logging

### Recommended Additions

```python
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

# Log important events
logger.info("Item created", extra={"item_id": item_id})
logger.warning("External API slow", extra={"duration": response_time})
logger.error("Database error", extra={"error": str(e)})
```

### Metrics to Track
- API response times
- Error rates
- External API success rates
- Database operation times
- User activity logs

---

## Conclusion

This architecture provides a solid foundation for an inventory management system with clear separation of concerns, consistent error handling, and external API integration. The modular design allows for easy testing, maintenance, and future scalability improvements.

---

**Document Version:** 1.0
**Last Updated:** January 2024
**Framework Version:** Flask 2.3.2
**Python Version:** 3.7+
