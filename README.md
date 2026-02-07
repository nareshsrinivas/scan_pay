# 🛒 Smart Checkout System

# claude link --->  https://claude.ai/chat/f0b75f70-e196-45df-a175-a8b6af88841a

A production-grade self-checkout system enabling customers to scan products, pay via UPI, and exit stores using secure time-bound QR codes.

## 🎯 Core Features

- **QR Code Scanning**: Scan product QR codes to add items to cart
- **Shopping Cart**: Add, update, remove items with real-time total calculation
- **Secure Payments**: UPI payment integration with webhook verification
- **Exit QR Generation**: Time-bound QR codes for secure exit verification
- **Staff Verification**: Gate staff can verify exit QR codes
- **Real-time Automation**: n8n workflows for payment processing
- **Responsive Design**: Mobile-first UI that works on all devices

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌────────────┐
│   React     │────▶│   FastAPI    │────▶│ PostgreSQL │
│  Frontend   │     │   Backend    │     │  Database  │
└─────────────┘     └──────────────┘     └────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │     n8n      │
                    │  Automation  │
                    └──────────────┘
```

## 📦 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Relational database
- **JWT** - Authentication
- **QRCode** - QR code generation

### Frontend
- **React 18** - UI library
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Zustand** - State management
- **React Router** - Navigation
- **html5-qrcode** - QR scanning
- **Axios** - HTTP client

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **n8n** - Workflow automation

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Option 1: Docker (Recommended)

```bash
# Clone the repository
cd smart-checkout-system

# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f backend
```

Services will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs
- n8n: http://localhost:5678 (admin/admin123)

### Option 2: Local Development

**Backend:**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
createdb smart_checkout

# Configure environment
cp .env .env.local
# Edit .env.local with your settings

# Seed database
python -m app.seed

# Run server
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

## 📱 User Flow

### Customer Journey
1. **Login** - Enter phone number (guest login)
2. **Scan** - Scan product QR codes in store
3. **Cart** - Review items, adjust quantities
4. **Checkout** - Create order and proceed to payment
5. **Payment** - Pay via UPI
6. **Exit QR** - Receive time-bound exit QR code
7. **Exit** - Show QR at gate for verification

### Staff Journey
1. **Login** - Staff credentials (staff@store.com / staff123)
2. **Verify** - Scan customer exit QR codes
3. **Authorize** - System shows green (valid) or red (invalid)

## 🔒 Security Features

- JWT-based authentication
- Password hashing with bcrypt
- QR token expiration (10 minutes)
- One-time use QR codes
- Payment webhook signature verification
- SQL injection prevention (ORM)
- CORS protection
- Device fingerprinting

## 🗄️ Database Schema

```
users ──────┐
           │
           ├──▶ orders ──────┐
           │        │        │
           │        ├──▶ order_items
           │        │
           │        ├──▶ payments
           │        │
           │        └──▶ exit_qrs
           │
           └──▶ carts ──────▶ products
                            │
staff                       └──▶ cart_items
```

## 🧪 Testing

### Test Credentials

**Customer Login:**
- Phone: Any 10-digit number

**Staff Login:**
- Email: staff@store.com
- Password: staff123

**Admin Login:**
- Email: admin@store.com
- Password: admin123

### Test Flow

1. Login with phone number
2. Scan products (use seeded products from database)
3. Add to cart
4. Checkout and pay
5. Generate exit QR
6. Use staff login to verify QR at `/verify`

### API Testing

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

## 📊 API Endpoints

See backend/README.md for complete API documentation or visit:
http://localhost:8000/api/docs

## 🔧 Configuration

### Environment Variables

**Backend (.env):**
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/smart_checkout
JWT_SECRET=your-jwt-secret
QR_SECRET=your-qr-secret
PAYMENT_KEY=razorpay_key
PAYMENT_SECRET=razorpay_secret
N8N_WEBHOOK_URL=http://localhost:5678/webhook/payment-success
```

**Frontend (.env):**
```env
VITE_API_URL=http://localhost:8000/api/v1
```

## 📝 Development

### Project Structure

```
smart-checkout-system/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── models/    # Database models
│   │   ├── api/       # API routes
│   │   ├── core/      # Security & deps
│   │   └── utils/     # Helpers
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/          # React frontend
│   ├── src/
│   │   ├── pages/     # React pages
│   │   ├── services/  # API services
│   │   ├── store/     # State management
│   │   └── App.jsx
│   ├── package.json
│   └── Dockerfile
├── n8n/              # Automation workflows
│   └── workflows/
├── infrastructure/    # Docker & configs
└── docker-compose.yml
```

### Adding New Features

1. **Backend**: Create API module in `backend/app/api/`
2. **Frontend**: Add page in `frontend/src/pages/`
3. **Database**: Update models in `backend/app/models/`
4. **Automation**: Create workflow in `n8n/workflows/`

## 🐛 Troubleshooting

**Database connection issues:**
```bash
docker-compose down -v
docker-compose up -d postgres
docker-compose logs postgres
```

**Backend not starting:**
```bash
docker-compose logs backend
# Check DATABASE_URL in .env
```

**Frontend build errors:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**QR Scanner not working:**
- Ensure HTTPS or localhost
- Allow camera permissions
- Check browser compatibility

## 🚀 Deployment

### Production Considerations

1. **Environment Variables**: Use secrets management
2. **Database**: Use managed PostgreSQL (AWS RDS, etc.)
3. **SSL**: Enable HTTPS
4. **Payment Gateway**: Configure real payment provider
5. **Monitoring**: Add logging and monitoring
6. **Backups**: Regular database backups
7. **Scaling**: Use load balancer for backend

### Docker Production Build

```bash
# Build optimized images
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

## 📚 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [n8n Documentation](https://docs.n8n.io/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file

## 🆘 Support

For issues:
1. Check troubleshooting section
2. Review API docs at /api/docs
3. Check Docker logs
4. Open an issue on GitHub

## 🎉 Acknowledgments

Built with modern technologies and best practices for production deployment.
