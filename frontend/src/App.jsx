import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { useAuthStore } from './store';

// Pages
import Login from './pages/Login';
import Scan from './pages/Scan';
import Product from './pages/Product';
import Cart from './pages/Cart';
import Checkout from './pages/Checkout';
import PaymentSuccess from './pages/PaymentSuccess';
import ExitPass from './pages/ExitPass';
import Verify from './pages/Verify';
import StaffLogin from './pages/StaffLogin';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useAuthStore();
  return isAuthenticated ? children : <Navigate to="/login" />;
};

function App() {
  return (
    <BrowserRouter>
      <Toaster position="top-center" />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/staff-login" element={<StaffLogin />} />
        
        <Route path="/" element={
          <ProtectedRoute>
            <Scan />
          </ProtectedRoute>
        } />
        
        <Route path="/product/:uuid" element={
          <ProtectedRoute>
            <Product />
          </ProtectedRoute>
        } />
        
        <Route path="/cart" element={
          <ProtectedRoute>
            <Cart />
          </ProtectedRoute>
        } />
        
        <Route path="/checkout" element={
          <ProtectedRoute>
            <Checkout />
          </ProtectedRoute>
        } />
        
        <Route path="/payment-success/:orderUuid" element={
          <ProtectedRoute>
            <PaymentSuccess />
          </ProtectedRoute>
        } />
        
        <Route path="/exit-pass/:orderUuid" element={
          <ProtectedRoute>
            <ExitPass />
          </ProtectedRoute>
        } />
        
        <Route path="/verify" element={<Verify />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
