# Smart Checkout - Frontend

React-based Progressive Web App for customer self-checkout experience.

## 🎨 Features

- QR Code Scanner (camera-based)
- Real-time cart updates
- Responsive design (mobile-first)
- UPI payment flow
- Exit QR code display with timer
- Staff verification interface

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 📱 Pages

### Customer Flow
- `/login` - Phone number login
- `/` - QR scanner
- `/product/:uuid` - Product details
- `/cart` - Shopping cart
- `/checkout` - Payment page
- `/payment-success/:orderUuid` - Payment confirmation
- `/exit-pass/:orderUuid` - Exit QR code display

### Staff Flow
- `/staff-login` - Staff authentication
- `/verify` - Exit QR verification

## 🔧 Configuration

Create `.env` file:
```env
VITE_API_URL=http://localhost:8000/api/v1
```

## 🎨 Styling

- **Tailwind CSS** for utility-first styling
- **Custom Components** in `src/components/`
- **Responsive Design** mobile-first approach
- **Color Scheme**:
  - Primary: #00E676 (Green)
  - Dark: #1A2332
  - Accent colors for states

## 📦 Dependencies

Key packages:
- `react` - UI library
- `react-router-dom` - Routing
- `axios` - HTTP client
- `zustand` - State management
- `html5-qrcode` - QR scanning
- `qrcode.react` - QR generation
- `react-hot-toast` - Notifications
- `lucide-react` - Icons

## 🏗️ Architecture

```
src/
├── pages/          # Route components
├── components/     # Reusable components
├── services/       # API calls
├── store/          # Zustand stores
├── utils/          # Helper functions
└── App.jsx         # Root component
```

## 🔄 State Management

Using Zustand for:
- Authentication state
- Cart state
- Order state

```javascript
import { useAuthStore } from './store';

const { user, token, setAuth, logout } = useAuthStore();
```

## 📡 API Integration

All API calls in `src/services/api.js`:

```javascript
import { authAPI, cartAPI, productsAPI } from './services/api';

// Login
const response = await authAPI.guestLogin(phone, deviceId);

// Add to cart
await cartAPI.add(productUuid, quantity);
```

## 🎯 Key Features Implementation

### QR Scanner
Using `html5-qrcode` library for camera access:
```javascript
const scanner = new Html5QrcodeScanner('qr-reader', {
  fps: 10,
  qrbox: { width: 250, height: 250 }
});
```

### Exit QR Display
Using `qrcode.react` for QR code generation:
```javascript
<QRCodeSVG
  value={token}
  size={256}
  level="H"
/>
```

## 📱 PWA Support

To enable PWA features:
1. Add manifest.json
2. Register service worker
3. Add offline support

## 🐛 Troubleshooting

**QR Scanner not working:**
- Requires HTTPS or localhost
- Check browser permissions
- Ensure camera access granted

**API calls failing:**
- Check VITE_API_URL in .env
- Verify backend is running
- Check CORS settings

**Build errors:**
```bash
rm -rf node_modules package-lock.json
npm install
```

## 🚀 Deployment

### Netlify/Vercel
```bash
npm run build
# Deploy dist/ folder
```

### Docker
Already configured in main docker-compose.yml

## 📝 Development Guidelines

- Use functional components with hooks
- Follow React best practices
- Keep components small and focused
- Use Tailwind utility classes
- Handle loading and error states
- Add proper TypeScript types (future)

## 🎨 Customization

### Colors
Edit `tailwind.config.js`:
```javascript
colors: {
  primary: {
    DEFAULT: '#00E676',
    dark: '#00C853',
  }
}
```

### Branding
- Update logo in assets
- Modify app name in index.html
- Change theme colors

## 🧪 Testing

```bash
# Add testing library
npm install -D @testing-library/react vitest

# Run tests
npm run test
```

## 📚 Resources

- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Zustand](https://zustand-demo.pmnd.rs/)
