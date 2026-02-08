import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle response errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  guestLogin: (phoneNumber, deviceId) =>
    api.post('/auth/guest-login', { phone_number: phoneNumber, device_id: deviceId }),

  getProfile: () =>
    api.get('/auth/profile'),

  logout: () =>
    api.post('/auth/logout'),
};

// Products API
export const productsAPI = {
  getAll: (params) =>
    api.get('/products', { params }),

  getById: (uuid) =>
    api.get(`/products/${uuid}`),

  getByQR: (qrCode) =>
    api.get(`/products/qr/${qrCode}`),
};

// Cart API
export const cartAPI = {
  add: (productUuid, quantity) =>
    api.post('/cart/add', { product_uuid: productUuid, quantity }),

  get: () =>
    api.get('/cart'),

  update: (cartUuid, quantity) =>
    api.put(`/cart/${cartUuid}`, { quantity }),

  remove: (cartUuid) =>
    api.delete(`/cart/${cartUuid}`),

  clear: () =>
    api.delete('/cart'),
};

// Orders API
export const ordersAPI = {
  create: () =>
    api.post('/orders/create'),

  getById: (uuid) =>
    api.get(`/orders/${uuid}`),

  getAll: () =>
    api.get('/orders'),
};

// Payments API
export const paymentsAPI = {
  initiate: (orderUuid, paymentMethod = 'upi') =>
    api.post('/payments/initiate', { order_uuid: orderUuid, payment_method: paymentMethod }),

  getStatus: (paymentUuid) =>
    api.get(`/payments/${paymentUuid}`),

  webhook: (data) =>
    api.post('/payments/webhook', data),
};

// Exit QR API
export const exitQRAPI = {
  generate: (orderUuid) =>
    api.post('/exit-qr/generate', { order_uuid: orderUuid }),

  verify: (qrToken) =>
    api.post('/exit-qr/verify', { qr_token: qrToken }),
};

// Staff API
export const staffAPI = {
  login: (email, password) =>
    api.post('/staff/login', { email, password }),
};

// AI Detection API
export const aiAPI = {
  health: () =>
    api.get('/ai/health'),

  detectProducts: (imageBase64, orderUuid, expectedProducts) =>
    api.post('/ai/detect-products', {
      image: imageBase64,
      order_uuid: orderUuid,
      expected_products: expectedProducts
    }),
};

export default api;
