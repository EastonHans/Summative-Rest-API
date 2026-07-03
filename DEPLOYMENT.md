# Deployment & Troubleshooting Guide

## Table of Contents
1. [Local Development Setup](#local-development-setup)
2. [Troubleshooting Common Issues](#troubleshooting-common-issues)
3. [Debugging Guide](#debugging-guide)
4. [Docker Deployment](#docker-deployment)
5. [Production Deployment](#production-deployment)
6. [Performance Tuning](#performance-tuning)
7. [Monitoring & Logs](#monitoring--logs)

---

## Local Development Setup

### Complete Setup Walkthrough

#### Step 1: Verify Python Installation
```bash
python --version
# Output should be: Python 3.7 or higher
```

#### Step 2: Clone Repository
```bash
git clone git@github.com:EastonHans/Summative-Rest-API.git
cd Summative-Rest-API
```

#### Step 3: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

#### Step 4: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 5: Verify Installation
```bash
python -c "import flask; import requests; import pytest; print('All packages installed!')"
```

#### Step 6: Run Initial Tests
```bash
pytest test_app.py -v
# Should show: 36 passed in ~1.10s
```

#### Step 7: Start Development Servers
```bash
# Terminal 1: Start API server
python app.py

# Terminal 2: Start CLI (after API is running)
python cli.py
```

---

## Troubleshooting Common Issues

### Issue 1: "ModuleNotFoundError: No module named 'flask'"

**Cause:** Dependencies not installed

**Solution:**
```bash
# Ensure virtual environment is activated
python -m pip install -r requirements.txt

# Verify installation
pip list | findstr Flask
```

---

### Issue 2: "Address already in use" or "Port 5000 in use"

**Cause:** Another process using port 5000

**Solutions:**

**Option A: Kill the process**
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :5000
kill -9 <PID>
```

**Option B: Use different port**
```bash
# Edit app.py
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
```

**Option C: Use Flask CLI**
```bash
set FLASK_PORT=5001  # Windows
export FLASK_PORT=5001  # macOS/Linux
python app.py
```

---

### Issue 3: "Connection refused" when CLI connects to API

**Cause:** API server not running

**Solution:**
```bash
# Make sure you have TWO terminals:
# Terminal 1: python app.py
# Terminal 2: python cli.py

# Check if server is running
curl http://localhost:5000/health
# Should return: {"status": "healthy", "service": "Inventory Management System"}
```

---

### Issue 4: Tests failing with "inventory.json: No such file"

**Cause:** Database file not initialized

**Solution:**
```bash
# Initialize database
python -c "from database import init_database; init_database(); print('Database initialized!')"

# Or run tests with automatic initialization
pytest test_app.py --co  # Collect tests (initializes DB)
```

---

### Issue 5: External API calls failing

**Cause:** Network issues or OpenFoodFacts API down

**Solutions:**
```bash
# Test API connectivity
curl "https://world.openfoodfacts.org/api/v0/product/5901234123457.json"

# Try different barcode (if product not found)
# Search for real product barcodes online

# Check your internet connection
ping google.com

# Check firewall settings
# Some firewalls may block OpenFoodFacts API calls
```

---

### Issue 6: JSON encoding/decoding errors

**Cause:** Corrupted inventory.json or encoding issues

**Solution:**
```bash
# Backup current file
copy inventory.json inventory.json.backup

# Delete and reinitialize
del inventory.json
python -c "from database import init_database; init_database()"
```

---

### Issue 7: Git push fails with permission denied

**Cause:** SSH key not set up or wrong remote URL

**Solution:**
```bash
# Check git configuration
git config --list

# Set up SSH key (one-time)
# Follow GitHub's instructions to generate SSH key

# Verify remote URL
git remote -v
# Should show: origin  git@github.com:EastonHans/Summative-Rest-API.git

# If HTTPS, convert to SSH
git remote set-url origin git@github.com:EastonHans/Summative-Rest-API.git
```

---

## Debugging Guide

### Enable Debug Logging

```python
# Add to app.py
import logging
logging.basicConfig(level=logging.DEBUG)

# Or set environment variable
# export FLASK_ENV=development
# export FLASK_DEBUG=1
```

### Using Python Debugger (pdb)

```python
# Add breakpoint in code
def add_item():
    data = request.get_json()
    import pdb; pdb.set_trace()  # Debugger stops here
    new_item = create_item(data)
    return jsonify(new_item), 201
```

### Using Flask Debugger

```bash
# Enable interactive debugger
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py

# Visit endpoint that causes error
# Flask will show interactive debugger in browser
```

### Testing Individual Functions

```python
# Create test_debug.py
from app import app
from database import init_database, get_all_items

if __name__ == '__main__':
    init_database()
    items = get_all_items()
    print(f"Total items: {len(items)}")
    for item in items:
        print(f"- {item['name']} (ID: {item['id']})")
```

Then run:
```bash
python test_debug.py
```

### Using Postman for API Testing

1. **Import Requests:**
   - Create new request
   - Select method (GET, POST, etc.)
   - Enter URL: http://localhost:5000/inventory
   - Click Send

2. **Test with Data:**
   - Select method: POST
   - URL: http://localhost:5000/inventory
   - Body tab → raw → JSON:
   ```json
   {
     "name": "Test Product",
     "barcode": "1234567890",
     "quantity": 50,
     "price": 9.99,
     "brand": "Test Brand"
   }
   ```

3. **Save Collection:**
   - Create a collection for all endpoints
   - Reuse for future testing

---

### Viewing Database Contents

```python
# Create inspect_db.py
import json
from database import load_inventory

inventory = load_inventory()
print(json.dumps(inventory, indent=2))
```

Run:
```bash
python inspect_db.py
```

---

### Testing External API

```python
# Create test_api.py
from external_api import ExternalAPIIntegration

api = ExternalAPIIntegration()

# Test by barcode
product = api.fetch_product_by_barcode("5901234123457")
print(f"Product: {product}")

# Test by name
products = api.fetch_product_by_name("Almond Milk", limit=3)
print(f"Found {len(products)} products")
```

---

## Docker Deployment

### Create Dockerfile

```dockerfile
# Use official Python runtime as base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV FLASK_DEBUG=0

# Run application
CMD ["python", "app.py"]
```

### Create docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - FLASK_DEBUG=0
    volumes:
      - ./inventory.json:/app/inventory.json
    restart: unless-stopped
```

### Build and Run

```bash
# Build image
docker build -t inventory-api:latest .

# Run container
docker run -p 5000:5000 inventory-api:latest

# Or use docker-compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## Production Deployment

### Using Gunicorn

1. **Install Gunicorn:**
```bash
pip install gunicorn
```

2. **Create wsgi.py:**
```python
from app import app

if __name__ == "__main__":
    app.run()
```

3. **Run with Gunicorn:**
```bash
# Single worker
gunicorn --bind 0.0.0.0:5000 --workers 1 wsgi:app

# Multiple workers
gunicorn --bind 0.0.0.0:5000 --workers 4 wsgi:app
```

### Using Nginx

1. **Create /etc/nginx/sites-available/inventory-api:**
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /path/to/app/static/;
    }
}
```

2. **Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/inventory-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Using Systemd Service

1. **Create /etc/systemd/system/inventory-api.service:**
```ini
[Unit]
Description=Inventory Management System API
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/inventory-api
ExecStart=/var/www/inventory-api/venv/bin/gunicorn \
    --bind 127.0.0.1:5000 \
    --workers 4 \
    wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```

2. **Start service:**
```bash
sudo systemctl daemon-reload
sudo systemctl start inventory-api
sudo systemctl enable inventory-api
sudo systemctl status inventory-api
```

### SSL/HTTPS Configuration

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Generate certificate
sudo certbot certonly --nginx -d yourdomain.com

# Update nginx config
ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# Auto-renewal
sudo systemctl enable certbot.timer
```

---

## Performance Tuning

### Database Optimization

```python
# Add indexing for frequently searched fields
# Note: with JSON file storage, consider migrating to database

# Current search is O(n), can be optimized with:
# 1. Database indexes
# 2. In-memory cache
# 3. Pagination
```

### API Response Optimization

```python
# Add pagination
@app.route('/inventory', methods=['GET'])
def get_inventory():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    items = get_all_items()
    start = (page - 1) * per_page
    end = start + per_page
    
    return jsonify({
        "status": "success",
        "data": items[start:end],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": len(items)
        }
    }), 200
```

### Caching Implementation

```python
# Install Flask-Caching
pip install Flask-Caching

# Configure cache
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/inventory', methods=['GET'])
@cache.cached(timeout=300)  # Cache for 5 minutes
def get_inventory():
    ...
```

### Connection Pooling (for PostgreSQL)

```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'postgresql://user:password@localhost/db',
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

---

## Monitoring & Logs

### Application Logging

```python
# Add to app.py
import logging
from logging.handlers import RotatingFileHandler

log_handler = RotatingFileHandler(
    'app.log',
    maxBytes=10485760,  # 10MB
    backupCount=10
)

log_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s'
))

app.logger.addHandler(log_handler)
app.logger.setLevel(logging.INFO)

# Log important events
@app.before_request
def log_request():
    app.logger.info(f"{request.method} {request.path}")

@app.after_request
def log_response(response):
    app.logger.info(f"Response: {response.status_code}")
    return response
```

### Health Monitoring

```bash
# Create health check script
#!/bin/bash
curl -s http://localhost:5000/health | grep -q "healthy"
if [ $? -eq 0 ]; then
    echo "API is healthy"
else
    echo "API is down!"
    # Restart service
    systemctl restart inventory-api
fi
```

### Performance Metrics

```python
# Monitor response times
import time

@app.before_request
def start_timer():
    request.start_time = time.time()

@app.after_request
def log_performance(response):
    duration = time.time() - request.start_time
    app.logger.info(f"{request.path}: {duration:.2f}s")
    return response
```

---

## Rollback & Recovery

### Database Backup

```bash
# Backup inventory.json
cp inventory.json inventory.json.backup.$(date +%Y%m%d_%H%M%S)

# Automated daily backup (Linux)
# Add to crontab
0 2 * * * cp /var/www/inventory-api/inventory.json /backups/inventory.json.$(date +\%Y\%m\%d)
```

### Rollback Procedure

```bash
# If deployment fails
# 1. Stop current service
systemctl stop inventory-api

# 2. Restore previous version
git revert <commit-hash>

# 3. Restart service
systemctl start inventory-api

# 4. Monitor logs
journalctl -u inventory-api -f
```

---

## Common Commands Reference

```bash
# Development
python app.py
python cli.py
pytest test_app.py -v

# Production with Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 wsgi:app

# Docker
docker build -t inventory-api:latest .
docker run -p 5000:5000 inventory-api:latest
docker-compose up -d

# Git
git add .
git commit -m "message"
git push origin main
git pull origin main

# Database
python -c "from database import init_database; init_database()"
python -c "from database import load_inventory; import json; print(json.dumps(load_inventory(), indent=2))"

# Testing
pytest test_app.py -v --cov
pytest test_app.py::TestDatabase -v

# Monitoring
curl http://localhost:5000/health
tail -f app.log
```

---

**Document Version:** 1.0
**Last Updated:** January 2024
