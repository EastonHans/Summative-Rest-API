# API Routes Documentation

## Route Planning & Design

This document outlines all the planned routes, their inputs, outputs, and data modifications for the Inventory Management System.

---

## 1. INVENTORY CRUD OPERATIONS

### 1.1 GET /inventory
**Purpose:** Fetch all inventory items

**Route Inputs:**
- None (Query parameters optional in future)

**Route Outputs:**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "name": "Organic Almond Milk",
      "barcode": "5901234123457",
      "quantity": 50,
      "price": 4.99,
      "brand": "Silk",
      "category": "Beverages",
      "description": "Filtered water, almonds, cane sugar...",
      "created_at": "2024-01-01T12:00:00",
      "updated_at": "2024-01-01T12:00:00",
      "external_api_data": {}
    }
  ],
  "count": 1
}
```

**Data Modifications:** None (Read-only)

**Triggered By CLI:**
- Option 1: View all inventory items
- Option 3: Search by name (filtered)
- Option 4: Search by barcode (single result)

---

### 1.2 GET /inventory/<id>
**Purpose:** Fetch a single inventory item by ID

**Route Inputs:**
- `id` (URL parameter): Integer - Item ID

**Route Outputs:**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "name": "Organic Almond Milk",
    "barcode": "5901234123457",
    "quantity": 50,
    "price": 4.99,
    "brand": "Silk",
    "category": "Beverages",
    "description": "Filtered water, almonds, cane sugar...",
    "created_at": "2024-01-01T12:00:00",
    "updated_at": "2024-01-01T12:00:00",
    "external_api_data": {}
  }
}
```

**Data Modifications:** None (Read-only)

**Triggered By CLI:**
- Option 2: View item details

---

### 1.3 POST /inventory
**Purpose:** Add a new inventory item

**Route Inputs (JSON Body):**
```json
{
  "name": "Product Name",
  "barcode": "1234567890",
  "quantity": 100,
  "price": 9.99,
  "brand": "Brand Name",
  "category": "Category",
  "description": "Product description"
}
```

**Route Outputs:**
```json
{
  "status": "success",
  "data": {
    "id": 4,
    "name": "Product Name",
    "barcode": "1234567890",
    "quantity": 100,
    "price": 9.99,
    "brand": "Brand Name",
    "category": "Category",
    "description": "Product description",
    "created_at": "2024-01-01T12:00:00",
    "updated_at": "2024-01-01T12:00:00",
    "external_api_data": {}
  },
  "message": "Item created successfully"
}
```

**Data Modifications:**
- Adds new item to inventory array
- Generates new ID (max ID + 1)
- Sets created_at and updated_at timestamps
- Returns 201 Created status

**Triggered By CLI:**
- Option 5: Add new item

---

### 1.4 PATCH /inventory/<id>
**Purpose:** Update an existing inventory item

**Route Inputs (URL & JSON Body):**
- `id` (URL parameter): Integer - Item ID
- JSON Body (partial):
```json
{
  "quantity": 50,
  "price": 8.99,
  "name": "Updated Name",
  "description": "Updated description"
}
```

**Route Outputs:**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "name": "Updated Name",
    "quantity": 50,
    "price": 8.99,
    "updated_at": "2024-01-01T13:00:00",
    ...
  },
  "message": "Item updated successfully"
}
```

**Data Modifications:**
- Updates specified fields only
- Preserves untouched fields
- Updates the updated_at timestamp
- Returns 200 OK status

**Triggered By CLI:**
- Option 6: Update item (quantity, price, name)
- Option 9: Enrich item with external API data

---

### 1.5 DELETE /inventory/<id>
**Purpose:** Delete an inventory item

**Route Inputs:**
- `id` (URL parameter): Integer - Item ID

**Route Outputs:**
```json
{
  "status": "success",
  "message": "Item with ID 1 deleted successfully"
}
```

**Data Modifications:**
- Removes item from inventory array
- Returns 200 OK status
- Returns 404 if item not found

**Triggered By CLI:**
- Option 7: Delete item

---

## 2. SEARCH OPERATIONS

### 2.1 GET /inventory/search/name
**Purpose:** Search inventory items by product name

**Route Inputs (Query Parameters):**
- `q` (required): String - Search term (case-insensitive, partial match)

**Route Outputs:**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "name": "Organic Almond Milk",
      "barcode": "5901234123457",
      "quantity": 50,
      "price": 4.99,
      ...
    }
  ],
  "count": 1
}
```

**Data Modifications:** None (Read-only)

**Triggered By CLI:**
- Option 3: Search by name

---

### 2.2 GET /inventory/search/barcode
**Purpose:** Search inventory item by barcode

**Route Inputs (Query Parameters):**
- `barcode` (required): String - Product barcode

**Route Outputs:**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "name": "Organic Almond Milk",
    "barcode": "5901234123457",
    "quantity": 50,
    "price": 4.99,
    ...
  }
}
```

**Data Modifications:** None (Read-only)

**Triggered By CLI:**
- Option 4: Search by barcode

---

## 3. EXTERNAL API INTEGRATION

### 3.1 POST /api/fetch-product
**Purpose:** Fetch product details from OpenFoodFacts API

**Route Inputs (JSON Body):**
```json
{
  "search_term": "1234567890",
  "search_type": "barcode"
}
```
OR
```json
{
  "search_term": "Almond Milk",
  "search_type": "name"
}
```

**Route Outputs (Success):**
```json
{
  "status": "success",
  "data": {
    "product_name": "Organic Almond Milk",
    "brands": "Silk",
    "barcode": "5901234123457",
    "categories": "Plant-based Beverages",
    "ingredients_text": "Filtered water, almonds, cane sugar...",
    "nutrition_grade": "A",
    "energy_kcal": 32,
    "fat": 2.5,
    "carbohydrates": 1.0,
    "proteins": 1.0,
    "image_url": "https://...",
    "url": "https://..."
  }
}
```

**Route Outputs (Not Found):**
```json
{
  "status": "error",
  "message": "Product not found for barcode: 0000000000"
}
```

**Data Modifications:** None (Read-only from external source)

**Triggered By CLI:**
- Option 8: Fetch product from OpenFoodFacts

**Error Handling:**
- Catches network errors and connection timeouts
- Returns 404 if product not found in API
- Logs all errors for debugging

---

### 3.2 POST /api/enrich-item/<id>
**Purpose:** Enrich an inventory item with external API data

**Route Inputs (URL & JSON Body):**
- `id` (URL parameter): Integer - Item ID
- JSON Body (optional):
```json
{
  "search_type": "barcode"
}
```

**Route Outputs (Success):**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "name": "Organic Almond Milk",
    "barcode": "5901234123457",
    "quantity": 50,
    "price": 4.99,
    "external_api_data": {
      "product_name": "Organic Almond Milk",
      "brands": "Silk",
      "categories": "Plant-based Beverages",
      "ingredients_text": "Filtered water, almonds, cane sugar...",
      "nutrition_grade": "A",
      "energy_kcal": 32,
      ...
    },
    "updated_at": "2024-01-01T13:00:00"
  },
  "message": "Item enriched with external API data"
}
```

**Data Modifications:**
- Fetches data from OpenFoodFacts API (using barcode or name)
- Updates the `external_api_data` field in the inventory item
- Updates the `updated_at` timestamp
- Persists changes to JSON database

**Triggered By CLI:**
- Option 9: Enrich item with OpenFoodFacts data

**Error Handling:**
- Returns 404 if inventory item not found
- Returns 404 if product not found in external API
- Catches network errors and timeouts

---

## 4. UTILITY ENDPOINTS

### 4.1 GET /health
**Purpose:** Health check endpoint

**Route Inputs:** None

**Route Outputs:**
```json
{
  "status": "healthy",
  "service": "Inventory Management System"
}
```

**Data Modifications:** None

**Triggered By CLI:** Not directly triggered

---

## 5. ERROR HANDLING

### 5.1 HTTP Status Codes

| Status | Meaning | Occurs When |
|--------|---------|------------|
| 200 | OK | Successful GET, PATCH, DELETE |
| 201 | Created | POST successful |
| 400 | Bad Request | Missing required fields, invalid input |
| 404 | Not Found | Item/endpoint doesn't exist |
| 405 | Method Not Allowed | Wrong HTTP method for endpoint |
| 500 | Server Error | Unexpected server errors |

### 5.2 Error Response Format

```json
{
  "status": "error",
  "message": "Descriptive error message"
}
```

---

## 6. DATA FLOW DIAGRAMS

### Adding an Item (CLI Option 5)
```
CLI User Input
    ↓
POST /inventory
    ↓
database.create_item()
    ↓
Update inventory.json
    ↓
Return created item (201)
    ↓
Display success to CLI
```

### Enriching an Item (CLI Option 9)
```
CLI User Input (Item ID)
    ↓
POST /api/enrich-item/<id>
    ↓
GET item from inventory
    ↓
Call external_api.fetch_product_details()
    ↓
Query OpenFoodFacts API
    ↓
PATCH /inventory/<id> with API data
    ↓
Update inventory.json
    ↓
Return enriched item (200)
    ↓
Display success to CLI
```

### Searching by Barcode (CLI Option 4)
```
CLI User Input (Barcode)
    ↓
GET /inventory/search/barcode?barcode=<barcode>
    ↓
database.search_items_by_barcode()
    ↓
Return matching item
    ↓
Display item details to CLI
```

---

## 7. INPUT VALIDATION

### Required Fields for POST /inventory
- `name` - String, non-empty
- `barcode` - String, non-empty
- `quantity` - Integer, non-negative
- `price` - Float, non-negative
- `brand` - String, non-empty

### Optional Fields for POST /inventory
- `category` - String (defaults to "Uncategorized")
- `description` - String (defaults to empty)
- `external_api_data` - Object (defaults to empty object)

### Search Validation
- `/inventory/search/name?q=` - Query parameter required, must be non-empty
- `/inventory/search/barcode?barcode=` - Barcode parameter required, must be non-empty

---

## 8. DATABASE OPERATIONS SUMMARY

| Operation | Input | Output | File Modified |
|-----------|-------|--------|---------------|
| GET all | None | Array of items | No |
| GET one | ID | Single item | No |
| POST | Item object | Created item | Yes |
| PATCH | ID + Updates | Updated item | Yes |
| DELETE | ID | Success message | Yes |
| Search name | Name string | Matching items | No |
| Search barcode | Barcode | Single item | No |

---

## 9. TYPICAL WORKFLOW

### Complete Inventory Management Session

1. **View Inventory** (Option 1)
   - GET /inventory → Display all items

2. **Search for Item** (Option 4)
   - GET /inventory/search/barcode?barcode=5901234123457
   - View item details

3. **Fetch Product Details** (Option 8)
   - POST /api/fetch-product
   - Get fresh data from OpenFoodFacts

4. **Add New Item** (Option 5)
   - POST /inventory
   - Add to inventory array

5. **Enrich with External Data** (Option 9)
   - POST /api/enrich-item/4
   - Fetch and store API data

6. **Update Stock** (Option 6)
   - PATCH /inventory/4
   - Update quantity

7. **View Updated Item** (Option 2)
   - GET /inventory/4
   - Confirm changes

---

## 10. AUTHENTICATION & AUTHORIZATION

**Current Implementation:** None (Development mode)

**For Production:**
- Implement JWT token authentication
- Add role-based access control (Admin, Employee)
- Add endpoints for user management
- Implement request signing for API calls

---

**Last Updated:** January 2024
**Version:** 1.0.0
