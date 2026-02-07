# 🚀 QUICK START GUIDE

## Prerequisites
- Docker Desktop installed
- Terminal/Command Prompt
- Web browser

## Setup (5 Minutes)

### Step 1: Extract Files
Extract the `smart-checkout-system` folder to your desired location.

### Step 2: Start Services

**Option A: Using Setup Script (Recommended)**
```bash
cd smart-checkout-system
./setup.sh
```

**Option B: Manual Start**
```bash
cd smart-checkout-system
docker-compose up -d
```

Wait 30 seconds for services to start.

### Step 3: Seed Database
```bash
docker-compose exec backend python -m app.seed
```

### Step 4: Open Application
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/api/docs

## 🎮 Test the Flow

### Customer Experience (2 minutes)

1. **Login**
   - Go to http://localhost:3000/login
   - Enter any 10-digit phone number
   - Click "Get Started"

2. **Scan Product**
   - Click on any product card OR
   - Manually navigate to: http://localhost:3000/product/PRODUCT:MILK001
   - Add to cart

3. **Checkout**
   - View cart
   - Click "Proceed to Checkout"
   - Click "Pay Now"
   - Wait for payment processing (auto-success after 2 seconds)

4. **Get Exit QR**
   - You'll see your exit QR code
   - Note the countdown timer (10 minutes)

### Staff Verification (1 minute)

1. **Staff Login**
   - Go to http://localhost:3000/staff-login
   - Email: `staff@store.com`
   - Password: `staff123`

2. **Verify Exit QR**
   - You'll see the scanner
   - Scan the customer's exit QR
   - See green (authorized) or red (denied) screen

## 📦 What's Running?

Check status:
```bash
docker-compose ps
```

You should see:
- ✅ postgres (Database)
- ✅ backend (FastAPI)
- ✅ frontend (React)
- ✅ n8n (Automation)

## 🔍 View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 🛑 Stop Services

```bash
docker-compose down
```

## 🧪 Test API Directly

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Get products
curl http://localhost:8000/api/v1/products

# Guest login
curl -X POST http://localhost:8000/api/v1/auth/guest-login \
  -H "Content-Type: application/json" \
  -d '{"phone_number":"9876543210"}'
```

## 📱 Mobile Testing

The app is mobile-responsive. Test on your phone:
1. Find your computer's IP address
2. Visit http://YOUR_IP:3000
3. Allow camera access for QR scanning

## 🐛 Troubleshooting

### Services won't start
```bash
docker-compose down -v
docker-compose up -d
```

### Database connection error
```bash
docker-compose restart postgres
sleep 10
docker-compose restart backend
```

### QR Scanner not working
- Ensure you're using HTTPS or localhost
- Grant camera permissions
- Use Chrome/Edge/Safari (Firefox may have issues)

### Port already in use
Edit `docker-compose.yml` and change port numbers.

## 🎯 Key URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | - |
| Backend API | http://localhost:8000 | - |
| API Docs | http://localhost:8000/api/docs | - |
| n8n | http://localhost:5678 | admin / admin123 |
| Database | localhost:5432 | postgres / postgres |

## 📝 Test Credentials

**Customer Login:**
- Phone: Any 10-digit number (e.g., 9876543210)

**Staff Login:**
- Email: staff@store.com
- Password: staff123

**Admin Login:**
- Email: admin@store.com
- Password: admin123

## 🎨 Sample Products

The database is seeded with 10 products:
- Milk Tetra Pack - ₹60
- Organic Oats - ₹250
- Whole Wheat Bread - ₹45
- Organic Bananas - ₹80
- Free Range Eggs - ₹120
- Olive Oil - ₹450
- Greek Yogurt - ₹150
- Granola Mix - ₹280
- Almond Milk - ₹180
- Organic Honey - ₹350

## 📚 Next Steps

1. **Explore API**: Visit http://localhost:8000/api/docs
2. **Check n8n**: Visit http://localhost:5678
3. **Customize**: Edit code in backend/ and frontend/
4. **Deploy**: Follow deployment guide in main README.md

## 🚀 Development Mode

For active development without Docker:

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 🎉 Success!

You now have a fully functional self-checkout system running locally!

For detailed documentation, see:
- Main README.md
- backend/README.md
- frontend/README.md

## 💡 Tips

1. Use Chrome/Edge for best QR scanner performance
2. Test on mobile device for full experience
3. Check API docs for all available endpoints
4. n8n can be used to create custom workflows
5. All UUIDs are used instead of integer IDs for security

## 📞 Need Help?

1. Check logs: `docker-compose logs -f`
2. Review API docs: http://localhost:8000/api/docs
3. Check main README.md troubleshooting section

Happy coding! 🚀
