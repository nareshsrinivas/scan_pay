# 🚀 Smart Checkout System - Installation Guide

Complete step-by-step guide to set up and run the Smart Checkout System locally.

## 📋 Prerequisites

### Required Software
- **Python 3.10+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **PostgreSQL 14+** - [Download](https://www.postgresql.org/download/)
- **Git** - [Download](https://git-scm.com/downloads/)

### Optional (Recommended)
- **Docker & Docker Compose** - [Download](https://docs.docker.com/get-docker/)
- **VS Code** - [Download](https://code.visualstudio.com/)

## 🎯 Option 1: Quick Start with Docker (Recommended)

This is the fastest way to get started. Everything runs in containers.

### Step 1: Run Quick Start Script

```bash
# Make script executable
chmod +x quickstart.sh

# Run it
./quickstart.sh
```

Choose option 1 for Docker Compose setup.

### Step 2: Access the Application

After containers start:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **n8n Automation**: http://localhost:5678

### Step 3: Test the System

1. Open http://localhost:3000
2. Click "Guest Login" → Enter phone: 9876543210
3. Go to "Scan Product" page
4. Test with sample products (auto-seeded)

### Managing Docker Services

```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Remove everything (including data)
docker-compose down -v
```

---

## 🔧 Option 2: Manual Installation (Local Development)

For developers who want full control.

### Step 1: Clone & Setup Project

```bash
# Clone repository
git clone <your-repo-url>
cd smart-checkout-system
```

### Step 2: Database Setup

#### Install PostgreSQL (if not installed)
- **macOS**: `brew install postgresql`
- **Ubuntu**: `sudo apt-get install postgresql`
- **Windows**: Download from postgresql.org

#### Create Database

```bash
# Start PostgreSQL service
sudo service postgresql start  # Linux
brew services start postgresql  # macOS

# Create database
createdb smartcheckout_db

# Or using psql
psql postgres
CREATE DATABASE smartcheckout_db;
\q
```

### Step 3: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env file with your settings
nano .env  # or use any text editor
```

#### Configure .env

Update these values in `backend/.env`:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/smartcheckout_db
JWT_SECRET=your-super-secret-jwt-key-change-this
QR_SECRET=your-qr-secret-key-change-this
RAZORPAY_KEY_ID=your_razorpay_test_key
RAZORPAY_KEY_SECRET=your_razorpay_test_secret
```

#### Initialize Database & Seed Data

```bash
# Run database migrations (if using Alembic)
alembic upgrade head

# Seed sample data
python app/seed.py
```

#### Start Backend Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will run at: http://localhost:8000

Test it: http://localhost:8000/docs

### Step 4: Frontend Setup

Open a new terminal window:

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Or create manually
echo "VITE_API_URL=http://localhost:8000/api/v1" > .env

# Start development server
npm run dev
```

Frontend will run at: http://localhost:5173

### Step 5: n8n Setup (Optional but Recommended)

#### Using Docker (Easiest)

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

#### Manual Installation

```bash
npm install -g n8n

# Start n8n
n8n start
```

Access n8n at: http://localhost:5678

#### Import Workflows

1. Open http://localhost:5678
2. Login with admin/admin123
3. Go to Workflows
4. Import from `n8n/workflows/payment_success.json`

### Step 6: AI Service Setup (Optional)

```bash
cd ai_service

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run AI service
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

---

## 🧪 Testing the Installation

### 1. Test Backend API

```bash
# Health check
curl http://localhost:8000/health

# Get products
curl http://localhost:8000/api/v1/products
```

### 2. Test Frontend

1. Open http://localhost:5173 (or :3000 if using Docker)
2. You should see the login page
3. Click "Continue as Guest"
4. Enter phone number: 9876543210

### 3. Complete Checkout Flow

1. **Scan Product** → Navigate to Scan page
2. **Product Details** → View product info
3. **Add to Cart** → Click "Add to Cart"
4. **Checkout** → Go to Cart and click "Proceed to Checkout"
5. **Payment** → Click "Pay Now" (test mode)
6. **Exit QR** → View generated exit QR code
7. **Verify** → Staff can scan QR to verify

### 4. Test Staff Portal

1. Go to http://localhost:5173/staff-login
2. Login with:
   - Email: admin@store.com
   - Password: admin123
3. Scan customer exit QR to verify

---

## 🔍 Troubleshooting

### Backend Issues

#### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>
```

#### Database Connection Error
```bash
# Check PostgreSQL is running
sudo service postgresql status

# Check connection
psql -U postgres -d smartcheckout_db
```

#### Module Not Found
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend Issues

#### npm install fails
```bash
# Clear cache
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

#### API Connection Error
- Check `VITE_API_URL` in `.env`
- Ensure backend is running on port 8000
- Check CORS settings in backend

### Docker Issues

#### Containers Not Starting
```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

#### Database Migration Error
```bash
# Access backend container
docker exec -it smart-checkout-backend bash

# Run migrations
alembic upgrade head
```

---

## 📚 Next Steps

After successful installation:

1. **Read the Documentation**
   - API Docs: http://localhost:8000/docs
   - Frontend Components: `frontend/src/components/`

2. **Configure Payment Gateway**
   - Sign up for Razorpay test account
   - Update credentials in `.env`

3. **Customize the System**
   - Add your store logo
   - Update color theme
   - Add more products

4. **Set Up n8n Workflows**
   - Import sample workflows
   - Create custom automation

5. **Enable AI Service** (Optional)
   - Train custom detection models
   - Configure visual validation

---

## 🆘 Getting Help

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Read error messages carefully
3. Check logs: `docker-compose logs` or console output
4. Open an issue on GitHub
5. Contact support: support@smartcheckout.com

---

## 📝 Configuration Checklist

- [ ] PostgreSQL installed and running
- [ ] Database created
- [ ] Backend .env configured
- [ ] Frontend .env configured
- [ ] Dependencies installed
- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] Sample data seeded
- [ ] API accessible at /docs
- [ ] Login working
- [ ] Payment gateway configured (optional)

---

## 🎉 Success!

If everything is working, you should be able to:
- ✅ Access frontend at http://localhost:5173
- ✅ Login as guest
- ✅ Browse products
- ✅ Add items to cart
- ✅ Complete checkout
- ✅ Generate exit QR
- ✅ Verify exit QR as staff

**Happy Shopping! 🛍️**
