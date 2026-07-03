# Quick Start Guide

Get the Inventory Management System up and running in 5 minutes!

## Prerequisites

- Python 3.7 or higher
- pip (usually comes with Python)
- Git

## 🚀 Quick Setup

### 1. Clone & Navigate
```bash
git clone git@github.com:EastonHans/Summative-Rest-API.git
cd Summative-Rest-API
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Start API Server
```bash
python app.py
```
✓ Server running on http://localhost:5000

### 5. Open New Terminal & Run CLI
```bash
# Activate virtual environment first (same as step 2)
python cli.py
```

## 📊 Quick API Tests

### Using curl (Command Line)

```bash
# View all items
curl http://localhost:5000/inventory

# View single item
curl http://localhost:5000/inventory/1

# Search by name
curl "http://localhost:5000/inventory/search/name?q=Almond"

# Health check
curl http://localhost:5000/health
```

### Using Postman

1. Open Postman
2. Create new request
3. Set method to GET
4. Enter: `http://localhost:5000/inventory`
5. Send

## 🧪 Run Tests

```bash
pytest test_app.py -v
```

## 📁 File Structure
```
- app.py              → Flask API server
- cli.py             → Command-line interface
- database.py        → Data management
- external_api.py    → OpenFoodFacts integration
- test_app.py        → Unit tests
- inventory.json     → Auto-generated database
```

## 🎯 Common Tasks

### Add a Product via CLI
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

### Search for Product
```
Option: 3 (by name) or 4 (by barcode)
Enter search term
```

### Fetch from OpenFoodFacts
```
Option: 8
Search type: barcode
Barcode: 3017620425035
```

### Update Stock
```
Option: 6
Item ID: 1
New quantity: 45
```

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 5000 in use | Change port in app.py or kill process |
| No module named Flask | Run `pip install -r requirements.txt` |
| API server not responding | Ensure app.py is running in separate terminal |
| Tests fail | Check all dependencies installed |

## 📚 Useful Commands

```bash
# Activate environment
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Install packages
pip install -r requirements.txt

# Run specific test
pytest test_app.py::TestAPIEndpoints::test_get_all_inventory -v

# View test coverage
pytest test_app.py --cov

# Deactivate environment
deactivate

# Check Python version
python --version
```

## 🌐 API Endpoints Reference

```
GET    /inventory                    → All items
GET    /inventory/<id>              → Single item
POST   /inventory                    → Create item
PATCH  /inventory/<id>              → Update item
DELETE /inventory/<id>              → Delete item
GET    /inventory/search/name       → Search by name
GET    /inventory/search/barcode    → Search by barcode
POST   /api/fetch-product           → Fetch from OpenFoodFacts
POST   /api/enrich-item/<id>        → Add API data to item
GET    /health                      → Health check
```

## 💡 Tips

1. **Always activate virtual environment** before running anything
2. **Keep two terminals open**: one for API, one for CLI
3. **Use real barcodes** from products for best OpenFoodFacts results
4. **Check .env** file for configuration
5. **Review README.md** for detailed documentation

## 🆘 Need Help?

- Check README.md for detailed documentation
- Review ROUTES_DOCUMENTATION.md for API details
- Run tests: `pytest test_app.py -v`
- Check console output for error messages

---

**Ready to go!** Start with `python app.py` and `python cli.py` 🎉
