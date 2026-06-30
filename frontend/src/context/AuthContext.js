import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser]       = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token     = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');
    if (token && savedUser) {
      try { setUser(JSON.parse(savedUser)); } catch {}
    }
    setLoading(false);
  }, []);

  const login = useCallback(async (email, password) => {
    const res = await authAPI.login({ email, password });
    const { access_token } = res.data;
    localStorage.setItem('token', access_token);
    const userData = { email };
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
    return res.data;
  }, []);

  const register = useCallback(async (email, password, full_name) => {
    return await authAPI.register({ email, password, full_name });
  }, []);

  const logout = useCallback(async () => {
    try {
      await authAPI.logout();           // tell the server
    } catch {}                          // always clear client-side even if request fails
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  }, []);

  const resendVerification = useCallback(async (email) => {
    return await authAPI.resendVerification(email);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, resendVerification }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};