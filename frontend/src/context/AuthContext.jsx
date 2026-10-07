import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('dept_access_token');
    if (!token) {
      setLoading(false);
      return;
    }

    api.getCurrentUser()
      .then((userData) => {
        setUser(userData);
      })
      .catch(() => {
        localStorage.removeItem('dept_access_token');
        localStorage.removeItem('dept_refresh_token');
        setUser(null);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const login = async (email, password) => {
    const data = await api.login(email, password);
    localStorage.setItem('dept_access_token', data.accessToken);
    localStorage.setItem('dept_refresh_token', data.refreshToken);
    setUser(data.user);
    return data.user;
  };

  const logout = () => {
    localStorage.removeItem('dept_access_token');
    localStorage.removeItem('dept_refresh_token');
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isHod: user?.role === 'HOD',
        isAdmin: user?.role === 'ADMIN',
        loading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
