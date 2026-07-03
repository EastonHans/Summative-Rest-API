# Inventory Management System

A comprehensive Flask-based REST API for managing an e-commerce inventory with integration to the OpenFoodFacts API for real-time product data enrichment.

## 🎯 Features

- **CRUD Operations**: Full Create, Read, Update, Delete functionality for inventory items
- **Real-time API Integration**: Fetch product details from OpenFoodFacts API by barcode or product name
- **Search Capabilities**: Search inventory by product name or barcode
- **Data Enrichment**: Automatically enhance stored inventory with external API data
- **CLI Interface**: User-friendly command-line tool to interact with the API
- **Comprehensive Testing**: Unit tests for all endpoints and integrations
- **RESTful Design**: Following REST conventions for all endpoints
- **JSON Storage**: Simple JSON file-based database for easy setup

## 📋 Requirements

- Python 3.7+
- pip (Python package manager)
- Git

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone git@github.com:EastonHans/Summative-Rest-API.git
cd Summative-Rest-API
```

### 2. Create a Virtual Environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root (already provided):

```
FLASK_ENV=development
FLASK_DEBUG=True
API_BASE_URL=http://localhost:5000
```

### 5. Initialize the Database

The database initializes automatically on first run with mock data. To manually initialize:

```bash
python -c "from database import init_database; init_database()"
```

## 📡 API Endpoints

### Inventory Management

#### Get All Items
```
GET /inventory
```
**Response:**
```json
{
  "status": "success",
  "data": [...],
  "count": 3
}
```

#### Get Single Item
```
GET /inventory/<id>
```
**Response:**
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

#### Create New Item
```
POST /inventory
Content-Type: application/json

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

#### Update Item
```
PATCH /inventory/<id>
Content-Type: application/json

{
  "quantity": 50,
  "price": 8.99
}
```

#### Delete Item
```
DELETE /inventory/<id>
```

### Search Endpoints

#### Search by Name
```
GET /inventory/search/name?q=<search_term>
```

#### Search by Barcode
```
GET /inventory/search/barcode?barcode=<barcode>
```

### External API Integration

#### Fetch Product from OpenFoodFacts
```
POST /api/fetch-product
Content-Type: application/json

{
  "search_term": "1234567890",
  "search_type": "barcode"  // or "name"
}
```

#### Enrich Inventory Item with API Data
```
POST /api/enrich-item/<id>
Content-Type: application/json

{
  "search_type": "barcode"  // or "name"
}
```

#### Health Check
```
GET /health
```

## 💻 Running the Application

### 1. Start the Flask API Server

```bash
python app.py
```

The server will start on `http://localhost:5000`

### 2. Run the CLI Application (in another terminal)

```bash
# Activate the virtual environment first
python cli.py
```

## 🎮 CLI Usage Examples

The CLI application provides an interactive menu with the following options:

### View All Items
```
Option: 1
```

### Search by Name
```
Option: 3
Enter product name: Almond
```

### Add New Item
```
Option: 5
Product name: Almond Butter
Barcode: 1234567890
Quantity: 25
Price: 8.99
Brand: Nature's
Category: Spreads
Description: Creamy almond butter
```

### Fetch from OpenFoodFacts
```
Option: 8
Search by (barcode/name): barcode
Enter barcode: 3017620425035
```

### Enrich Item with API Data
```
Option: 9
Enter item ID: 1
Search by (barcode/name): barcode
```

### Update Item Stock
```
Option: 6
Enter item ID: 1
Quantity: 45
```

### Delete Item
```
Option: 7
Enter item ID: 1
Confirm deletion: yes
```

## 🧪 Testing

Run the test suite to verify all functionality:

```bash
# Run all tests
pytest test_app.py -v

# Run with coverage report
pytest test_app.py --cov=. --cov-report=html

# Run specific test class
pytest test_app.py::TestAPIEndpoints -v

# Run specific test
pytest test_app.py::TestAPIEndpoints::test_get_all_inventory -v
```

### Test Coverage

The test suite includes:

- **Database Tests** (10 tests): Create, read, update, delete operations
- **API Endpoint Tests** (17 tests): All CRUD endpoints, search, error handling
- **External API Tests** (8 tests): OpenFoodFacts integration with mocked responses
- **Error Handler Tests** (2 tests): HTTP error handling

Run with coverage to see detailed metrics:

```bash
pytest test_app.py --cov=. --cov-report=html
# Open htmlcov/index.html in browser
```

## 🔍 Debugging

### Using Flask Debug Mode

The application runs in debug mode by default. Debug mode enables:
- Auto-reloading on file changes
- Interactive debugger
- Detailed error pages

### Using Postman for API Testing

1. Install [Postman](https://www.postman.com/downloads/)
2. Import the API endpoints or create requests manually
3. Test endpoints with various inputs

Example Postman collection:

```json
{
  "info": {
    "name": "Inventory API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Get All Items",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/inventory"
      }
    },
    {
      "name": "Create Item",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/inventory",
        "body": {
          "mode": "raw",
          "raw": "{...}"
        }
      }
    }
  ]
}
```

### Viewing Logs

Check the console output for Flask request logs and application logs. For persistent logging, redirect output:

```bash
python app.py > app.log 2>&1
```

## 📁 Project Structure

```
Summative-Rest-API/
├── app.py                 # Flask application and API endpoints
├── database.py            # Database operations and mock data
├── external_api.py        # OpenFoodFacts API integration
├── cli.py                 # CLI application for user interaction
├── test_app.py            # Unit tests
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── .gitignore            # Git ignore rules
├── inventory.json        # Mock database (auto-generated)
└── README.md             # This file
```

## 🔄 API Response Format

All API responses follow a consistent format:

**Success Response:**
```json
{
  "status": "success",
  "data": {...},
  "message": "Operation successful"
}
```

**Error Response:**
```json
{
  "status": "error",
  "message": "Error description"
}
```

## 📦 Database Schema

Each inventory item contains:

```json
{
  "id": 1,
  "name": "Product Name",
  "barcode": "1234567890",
  "quantity": 100,
  "price": 9.99,
  "brand": "Brand Name",
  "category": "Category",
  "description": "Product description",
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:00:00",
  "external_api_data": {
    "product_name": "From API",
    "brands": "Brand",
    "ingredients_text": "Ingredients",
    "nutrition_grade": "A",
    ...
  }
}
```

## 🌐 OpenFoodFacts API Integration

The system integrates with the [OpenFoodFacts API](https://openfoodfacts.github.io/openfoodfacts-server/api/) to fetch:

- Product names and brands
- Ingredient information
- Nutritional data (energy, fat, carbs, proteins)
- Nutrition grades
- Categories and images

### Example API Response

```json
{
  "status": 1,
  "product": {
    "product_name": "Organic Almond Milk",
    "brands": "Silk",
    "code": "5901234123457",
    "categories": "Plant-based Beverages",
    "ingredients_text": "Filtered water, almonds, cane sugar...",
    "nutrition_grade_fr": "A",
    "energy_kcal_100g": 32,
    "fat_100g": 2.5,
    "carbohydrates_100g": 1.0,
    "proteins_100g": 1.0,
    "image_front_url": "https://..."
  }
}
```

## 🐛 Troubleshooting

### API Server Not Starting
```bash
# Check if port 5000 is already in use
netstat -tulpn | grep 5000

# Use a different port
python app.py --port 5001
```

### CLI Cannot Connect to API
```bash
# Ensure Flask server is running
# Verify API_BASE_URL in .env matches server address
# Check firewall settings
```

### Tests Failing
```bash
# Ensure all dependencies are installed
pip install -r requirements.txt

# Clean test artifacts
rm -rf .pytest_cache
rm -rf htmlcov

# Run tests with verbose output
pytest test_app.py -vv
```

### External API Errors
- Check internet connection
- Verify barcode/product name exists in OpenFoodFacts database
- Check API rate limits (typically 1 request per second)

## 📝 Environment Variables Reference

```
FLASK_ENV              # Flask environment (development/production)
FLASK_DEBUG            # Enable debug mode
SECRET_KEY             # Flask secret key
API_HOST              # API server host
API_PORT              # API server port
API_BASE_URL          # Base URL for API
OPENFOODFACTS_API_TIMEOUT  # Request timeout in seconds
DATABASE_FILE         # Database file path
```

## 🔐 Security Considerations

For production deployment:

1. Change `SECRET_KEY` in `.env`
2. Set `FLASK_ENV=production`
3. Set `FLASK_DEBUG=False`
4. Use environment-specific `.env` files
5. Implement authentication/authorization
6. Use HTTPS for external API calls
7. Validate and sanitize all inputs
8. Implement rate limiting
9. Use a production-grade database (PostgreSQL, MongoDB)
10. Deploy behind a web server (nginx, Apache)

## 🚀 Deployment

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV FLASK_APP=app.py
CMD ["python", "app.py"]
```

Build and run:

```bash
docker build -t inventory-api .
docker run -p 5000:5000 inventory-api
```

### Heroku Deployment

1. Create `Procfile`:
```
web: python app.py
```

2. Deploy:
```bash
git push heroku main
```

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [OpenFoodFacts API](https://openfoodfacts.github.io/openfoodfacts-server/api/)
- [pytest Documentation](https://docs.pytest.org/)
- [REST API Best Practices](https://restfulapi.net/)

## 👥 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the MIT License.

## 💬 Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Last Updated:** January 2024
**Version:** 1.0.0
**Author:** Easton Hans
