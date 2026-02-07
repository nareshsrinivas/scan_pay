# 📋 COPY-PASTE COMMAND REFERENCE

Quick reference for all commands you'll need. Just copy and paste!

## 🚀 QUICK START (Choose One Method)

### Method 1: Automatic Setup (Easiest) ⭐

```bash
cd smart-checkout-system
chmod +x quickstart.sh
./quickstart.sh
```

Then choose option 1 (Docker Compose).

### Method 2: Docker Compose (Recommended)

```bash
cd smart-checkout-system
docker-compose up -d
```

Wait 30 seconds, then open:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000/api/docs

### Method 3: Manual Setup

**Terminal 1 - Backend:**
```bash
cd smart-checkout-system/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings
createdb smartcheckout_db  # or use your PostgreSQL client
python app/seed.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd smart-checkout-system/frontend
npm install
echo "VITE_API_URL=http://localhost:8000/api/v1" > .env
npm run dev
```

## 🔍 VERIFY INSTALLATION

### Check Backend
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Expected output:
# {"status":"healthy","version":"1.0.0"}
```

### Check Frontend
```bash
# Open in browser
open http://localhost:3000
# Or visit manually
```

### Check Database (Docker)
```bash
docker exec -it smart-checkout-db psql -U postgres -d smart_checkout -c "SELECT COUNT(*) FROM products;"

# Should return: count > 0
```

## 📊 DOCKER COMMANDS

### Start Services
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### View Logs (All Services)
```bash
docker-compose logs -f
```

### View Logs (Specific Service)
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Restart Service
```bash
docker-compose restart backend
```

### Rebuild (After Code Changes)
```bash
docker-compose build backend
docker-compose up -d backend
```

### Complete Reset (Delete Everything)
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Access Container Shell
```bash
# Backend
docker exec -it smart-checkout-backend bash

# Database
docker exec -it smart-checkout-db psql -U postgres -d smart_checkout

# Frontend
docker exec -it smart-checkout-frontend sh
```

## 🧪 API TESTING COMMANDS

### Set Token Variable (After Login)
```bash
export TOKEN="YOUR_ACCESS_TOKEN_HERE"
```

Or get it automatically:
```bash
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/guest-login \
  -H "Content-Type: application/json" \
  -d '{"phone_number":"9876543210"}' | jq -r '.data.access_token')

echo $TOKEN
```

### Test All Endpoints

**1. Guest Login**
```bash
curl -X POST http://localhost:8000/api/v1/auth/guest-login \
  -H "Content-Type: application/json" \
  -d '{"phone_number":"9876543210"}'
```

**2. Get Products**
```bash
curl http://localhost:8000/api/v1/products \
  -H "Authorization: Bearer $TOKEN"
```

**3. Get Specific Product**
```bash
# Replace UUID with actual product UUID from step 2
curl http://localhost:8000/api/v1/products/PRODUCT_UUID_HERE \
  -H "Authorization: Bearer $TOKEN"
```

**4. Add to Cart**
```bash
curl -X POST http://localhost:8000/api/v1/cart/add \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "product_uuid": "PRODUCT_UUID_HERE",
    "quantity": 2
  }'
```

**5. View Cart**
```bash
curl http://localhost:8000/api/v1/cart \
  -H "Authorization: Bearer $TOKEN"
```

**6. Create Order**
```bash
curl -X POST http://localhost:8000/api/v1/orders/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{}'
```

**7. Initiate Payment**
```bash
# Replace ORDER_UUID with UUID from step 6
curl -X POST http://localhost:8000/api/v1/payments/initiate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "order_uuid": "ORDER_UUID_HERE",
    "payment_method": "upi"
  }'
```

**8. Generate Exit QR**
```bash
curl -X POST http://localhost:8000/api/v1/exit-qr/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "order_uuid": "ORDER_UUID_HERE"
  }'
```

**9. Verify Exit QR (Staff)**
```bash
# First login as staff
STAFF_TOKEN=$(curl -X POST http://localhost:8000/api/v1/staff/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@store.com","password":"admin123"}' | jq -r '.data.access_token')

# Then verify
curl -X POST http://localhost:8000/api/v1/exit-qr/verify \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $STAFF_TOKEN" \
  -d '{
    "token": "EXIT_QR_TOKEN_HERE"
  }'
```

## 🗄️ DATABASE COMMANDS

### PostgreSQL Commands (Docker)
```bash
# Connect to database
docker exec -it smart-checkout-db psql -U postgres -d smart_checkout

# List tables
\dt

# View products
SELECT * FROM products LIMIT 5;

# View users
SELECT * FROM users LIMIT 5;

# Count orders
SELECT COUNT(*) FROM orders;

# Exit
\q
```

### Manual Database Setup (Non-Docker)
```bash
# Create database
createdb smartcheckout_db

# Or using psql
psql postgres
CREATE DATABASE smartcheckout_db;
\c smartcheckout_db
\q
```

### Seed Sample Data
```bash
cd backend
source venv/bin/activate  # if using virtual env
python app/seed.py
```

## 🎨 FRONTEND COMMANDS

### Development
```bash
cd frontend
npm run dev
```

### Build for Production
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

### Lint Code
```bash
npm run lint
```

### Format Code
```bash
npm run format
```

## 🔧 BACKEND COMMANDS

### Start Development Server
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Run Tests
```bash
pytest
```

### Code Formatting
```bash
black app/
isort app/
```

### Type Checking
```bash
mypy app/
```

## 📦 DEPENDENCY MANAGEMENT

### Backend (Python)
```bash
# Install dependencies
pip install -r requirements.txt

# Update requirements
pip freeze > requirements.txt

# Install new package
pip install package-name
pip freeze > requirements.txt
```

### Frontend (Node)
```bash
# Install dependencies
npm install

# Install new package
npm install package-name

# Update all packages
npm update

# Check for outdated packages
npm outdated
```

## 🔄 n8n AUTOMATION COMMANDS

### Start n8n (Docker)
```bash
docker run -d \
  --name smart-checkout-n8n \
  -p 5678:5678 \
  -e N8N_BASIC_AUTH_ACTIVE=true \
  -e N8N_BASIC_AUTH_USER=admin \
  -e N8N_BASIC_AUTH_PASSWORD=admin123 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

### Access n8n
```bash
open http://localhost:5678
```

Login: admin / admin123

## 🐞 TROUBLESHOOTING COMMANDS

### Check Running Services
```bash
docker-compose ps
```

### Check Port Usage
```bash
# Check if port 8000 is in use (macOS/Linux)
lsof -i :8000

# Check if port 3000 is in use
lsof -i :3000

# Windows
netstat -ano | findstr :8000
```

### Kill Process on Port
```bash
# macOS/Linux
kill -9 $(lsof -t -i:8000)

# Windows
# Find PID from netstat command, then:
taskkill /PID <PID> /F
```

### Clear Docker Volumes
```bash
docker-compose down -v
docker volume prune -f
```

### Clear Docker Images
```bash
docker-compose down --rmi all
docker image prune -a -f
```

### Complete Docker Cleanup
```bash
docker-compose down -v --rmi all
docker system prune -a -f
docker volume prune -f
```

### Check Backend Logs
```bash
# Docker
docker-compose logs backend

# Manual
tail -f backend/logs/app.log  # if logging to file
```

### Check Frontend Logs
```bash
# Docker
docker-compose logs frontend

# Manual - check browser console
```

## 🔍 MONITORING COMMANDS

### System Resource Usage
```bash
docker stats
```

### Disk Usage
```bash
docker system df
```

### Network Status
```bash
docker network ls
docker network inspect smart-checkout-network
```

## 📝 COMMON WORKFLOWS

### Complete Fresh Start
```bash
# 1. Stop everything
docker-compose down -v

# 2. Remove old images
docker-compose down --rmi all

# 3. Rebuild
docker-compose build --no-cache

# 4. Start fresh
docker-compose up -d

# 5. Check logs
docker-compose logs -f
```

### Update Code and Restart
```bash
# Pull changes (if using git)
git pull

# Rebuild and restart
docker-compose build backend frontend
docker-compose up -d

# Or restart specific service
docker-compose restart backend
```

### Database Reset
```bash
# 1. Stop services
docker-compose down

# 2. Remove database volume
docker volume rm smart-checkout-system_postgres_data

# 3. Start again (will create fresh DB)
docker-compose up -d

# 4. Seed data
docker exec -it smart-checkout-backend python app/seed.py
```

## 🚀 DEPLOYMENT COMMANDS

### Build Production Images
```bash
# Backend
docker build -t smart-checkout-backend:latest ./backend

# Frontend
docker build -t smart-checkout-frontend:latest ./frontend
```

### Push to Registry (DockerHub Example)
```bash
# Tag images
docker tag smart-checkout-backend:latest username/smart-checkout-backend:latest
docker tag smart-checkout-frontend:latest username/smart-checkout-frontend:latest

# Push
docker push username/smart-checkout-backend:latest
docker push username/smart-checkout-frontend:latest
```

## 🌐 OPEN IN BROWSER COMMANDS

### macOS
```bash
open http://localhost:3000
open http://localhost:8000/api/docs
```

### Linux
```bash
xdg-open http://localhost:3000
xdg-open http://localhost:8000/api/docs
```

### Windows (PowerShell)
```powershell
Start-Process http://localhost:3000
Start-Process http://localhost:8000/api/docs
```

## 📊 QUICK STATUS CHECK

Run this to check if everything is working:

```bash
#!/bin/bash
echo "🔍 Checking Smart Checkout System Status..."
echo ""

# Check backend
echo "Backend Health:"
curl -s http://localhost:8000/api/v1/health | jq
echo ""

# Check frontend (simple GET)
echo "Frontend Status:"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:3000
echo ""

# Check Docker containers
echo "Docker Containers:"
docker-compose ps
echo ""

echo "✅ Status Check Complete!"
```

Save as `check_status.sh`, make executable, and run:
```bash
chmod +x check_status.sh
./check_status.sh
```

---

## 💡 PRO TIPS

1. **Save your token**: After login, export TOKEN variable for easy testing
2. **Use jq**: Install jq for pretty JSON output: `brew install jq` (macOS)
3. **Alias commands**: Add to .bashrc:
   ```bash
   alias dc='docker-compose'
   alias dcu='docker-compose up -d'
   alias dcd='docker-compose down'
   alias dcl='docker-compose logs -f'
   ```
4. **Watch logs**: Keep `docker-compose logs -f` running in separate terminal
5. **Use Swagger**: API docs at /api/docs provide interactive testing

---

**That's it! These are all the commands you'll need. Copy, paste, and run! 🚀**
