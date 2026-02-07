import { create } from 'zustand';

export const useAuthStore = create((set) => ({
  user: JSON.parse(localStorage.getItem('user') || 'null'),
  token: localStorage.getItem('token') || null,
  isAuthenticated: !!localStorage.getItem('token'),
  
  setAuth: (user, token) => {
    localStorage.setItem('user', JSON.stringify(user));
    localStorage.setItem('token', token);
    set({ user, token, isAuthenticated: true });
  },
  
  logout: () => {
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    set({ user: null, token: null, isAuthenticated: false });
  },
}));

export const useCartStore = create((set) => ({
  cart: null,
  loading: false,
  
  setCart: (cart) => set({ cart }),
  setLoading: (loading) => set({ loading }),
  clearCart: () => set({ cart: null }),
}));

export const useOrderStore = create((set) => ({
  currentOrder: null,
  orders: [],
  
  setCurrentOrder: (order) => set({ currentOrder: order }),
  setOrders: (orders) => set({ orders }),
  clearCurrentOrder: () => set({ currentOrder: null }),
}));
