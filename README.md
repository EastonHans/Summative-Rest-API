# Inventory Management System

A Flask REST API for running e-commerce inventory, hooked up to OpenFoodFacts so your product data doesn't sit there stale. You give it a barcode, it goes and finds the real details. No copy-pasting nutrition facts by hand.

## What it actually does

- Full CRUD on inventory items. Create one, read it back, update the quantity, delete it when you're done.
- Pulls live product info from OpenFoodFacts by barcode or by name.
- Search by name or barcode, whichever you've got on hand.
- Auto-enriches whatever's already in your inventory with fresh external data.
- A CLI that walks you through everything, no need to fight with curl.
- Solid test coverage across the endpoints and the API integration.
- Follows REST conventions properly.
- Stores everything in a plain JSON file. Setup takes about thirty seconds.

## What you'll need

Python 3.7 or newer, pip, and Git. That's it.

## Getting it running

### 1. Grab the repo

```bash
git clone git@github.com:EastonHans/Summative-Rest-API.git
cd Summative-Rest-API
```

### 2. Set up a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install the dependencies

```bash
pip install -r requirements.txt
```

### 4. Sort out your environment variables

There's already a `.env` file in the project root, but here's what's in it:

```
FLASK_ENV=development
FLASK_DEBUG=True
API_BASE_URL=http://localhost:5000
```

### 5. Fire up the database

It initializes itself on first run, mock data included. Want to do it manually instead?

```bash
python -c "from database import init_database; init_database()"
```

## The API

### Inventory

#### Grab everything
```
GET /inventory
```
Returns something like:
```json
{
  "status": "success",
  "data": [...],
  "count": 3
}
```

#### Grab one item
```
GET /inventory/<id>
```
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

#### Add something new
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

#### Update it
```
PATCH /inventory/<id>
Content-Type: application/json

{
  "quantity": 50,
  "price": 8.99
}
```

#### Get rid of it
```
DELETE /inventory/<id>
```

### Searching

#### By name
```
GET /inventory/search/name?q=<search_term>
```

#### By barcode
```
GET /inventory/search/barcode?barcode=<barcode>
```

### Talking to OpenFoodFacts

#### Fetch a product straight from their database
```
POST /api/fetch-product
Content-Type: application/json

{
  "search_term": "1234567890",
  "search_type": "barcode"  // or "name"
}
```

#### Enrich something you already stored
```
POST /api/enrich-item/<id>
Content-Type: application/json

{
  "search_type": "barcode"  // or "name"
}
```

#### Health check
```
GET /health
```

## Running the thing

### Start the server

```bash
python app.py
```

It'll come up on `http://localhost:5000`.

### Start the CLI

Open a second terminal, activate your venv again, then:

```bash
python cli.py
```

## Using the CLI

It's menu-driven. Here's the gist of it.

**See everything:**
```
Option: 1
```

**Search by name:**
```
Option: 3
Enter product name: Almond
```

**Add a new item:**
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

**Pull from OpenFoodFacts:**
```
Option: 8
Search by (barcode/name): barcode
Enter barcode: 3017620425035
```

**Enrich an existing item:**
```
Option: 9
Enter item ID: 1
Search by (barcode/name): barcode
```

**Update stock:**
```
Option: 6
Enter item ID: 1
Quantity: 45
```

**Delete something:**
```
Option: 7
Enter item ID: 1
Confirm deletion: yes
```

## Testing

```bash
# the whole suite
pytest test_app.py -v

# with a coverage report
pytest test_app.py --cov=. --cov-report=html

# just one class
pytest test_app.py::TestAPIEndpoints -v

# just one test
pytest test_app.py::TestAPIEndpoints::test_get_all_inventory -v
```

What's actually covered:

- Database operations. 10 tests. Create, read, update, delete, all of it.
- API endpoints. 17 tests, spanning CRUD, search, and how things fail when they should fail.
- The OpenFoodFacts integration. 8 tests, all mocked so you're not hammering their servers every run.
- Error handling. 2 tests, checking the HTTP error responses behave.

Want the detailed numbers?

```bash
pytest test_app.py --cov=. --cov-report=html
# then open htmlcov/index.html
```

## When something breaks

### Debug mode

It's on by default, which gets you auto-reload on file changes, the interactive debugger, and error pages that actually tell you something.

### Postman

1. Grab [Postman](https://www.postman.com/downloads/) if you don't have it.
2. Build your requests, or import a collection.
3. Hit the endpoints and see what comes back.

Here's a starter collection:

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

### Logs

Check your console for the Flask request logs. If you want them saved somewhere:

```bash
python app.py > app.log 2>&1
```

## How it's laid out

```
Summative-Rest-API/
├── app.py                 # Flask app and all the routes
├── database.py            # DB logic and mock data
├── external_api.py        # OpenFoodFacts integration
├── cli.py                 # the command-line interface
├── test_app.py            # tests
├── requirements.txt       # dependencies
├── .env                   # environment variables
├── .gitignore
├── inventory.json         # auto-generated mock database
└── README.md
```

## Response shape

Every response follows the same pattern, success or not.

**When it works:**
```json
{
  "status": "success",
  "data": {...},
  "message": "Operation successful"
}
```

**When it doesn't:**
```json
{
  "status": "error",
  "message": "Error description"
}
```

## What an inventory item looks like

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

## The OpenFoodFacts piece

This project leans on the [OpenFoodFacts API](https://openfoodfacts.github.io/openfoodfacts-server/api/) for product names, brands, ingredient lists, nutritional breakdowns (energy, fat, carbs, protein), nutrition grades, categories, and images. It's a genuinely useful free database, and it saves you from typing out ingredient lists by hand.

Here's what a response from them looks like:

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

## Common headaches

**Server won't start:**
```bash
# see what's hogging port 5000
netstat -tulpn | grep 5000

# or just use a different one
python app.py --port 5001
```

**CLI can't reach the API?** Make sure the Flask server's actually running, double check `API_BASE_URL` in your `.env` matches where the server's listening, and take a peek at your firewall settings while you're at it.

**Tests failing:**
```bash
pip install -r requirements.txt

rm -rf .pytest_cache
rm -rf htmlcov

pytest test_app.py -vv
```

**Getting errors from the external API?** Check your internet connection first, then confirm the barcode or product name actually exists in OpenFoodFacts. They also rate-limit you, roughly one request per second, so don't hammer it.

## Environment variables, all of them

```
FLASK_ENV                  # development or production
FLASK_DEBUG                # on or off
SECRET_KEY                 # Flask's secret key
API_HOST                   # server host
API_PORT                   # server port
API_BASE_URL                # base URL the CLI hits
OPENFOODFACTS_API_TIMEOUT  # how long to wait, in seconds
DATABASE_FILE               # where the JSON file lives
```

## Before you put this anywhere real

1. Change `SECRET_KEY`. Don't ship the default.
2. Set `FLASK_ENV=production`.
3. Turn `FLASK_DEBUG` off.
4. Keep separate `.env` files per environment.
5. Add real authentication. This doesn't have any right now.
6. Use HTTPS for the external API calls.
7. Validate and sanitize every input that comes in.
8. Put rate limiting in front of it.
9. Swap the JSON file for a proper database. PostgreSQL or MongoDB, take your pick.
10. Run it behind nginx or Apache, not bare.

## Shipping it somewhere

### Docker

Drop this in a `Dockerfile`:

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV FLASK_APP=app.py
CMD ["python", "app.py"]
```

Then:

```bash
docker build -t inventory-api .
docker run -p 5000:5000 inventory-api
```

### Heroku

Add a `Procfile`:
```
web: python app.py
```

Then push:
```bash
git push heroku main
```

## Worth reading

- [Flask docs](https://flask.palletsprojects.com/)
- [OpenFoodFacts API](https://openfoodfacts.github.io/openfoodfacts-server/api/)
- [pytest docs](https://docs.pytest.org/)
- [REST API best practices](https://restfulapi.net/)

## Contributing

Fork it, branch off (`git checkout -b feature/AmazingFeature`), commit your work, push the branch, and open a pull request. Standard stuff.

## License

MIT. Do what you want with it.

## Got a problem?

Open an issue on GitHub and I'll take a look.

---

**Last updated:** June 2026
**Version:** 1.0.0
**Author:** Easton Hans