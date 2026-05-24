import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Auto-login on load - no manual login needed
    const doAutoLogin = async () => {
      const demoEmail = 'demo@local.ai';
      const demoPassword = 'demo123';
      try {
        // Try to register (will fail if exists)
        await axios.post('/api/auth/register', {
          email: demoEmail,
          password: demoPassword,
          full_name: 'Demo User'
        });
      } catch (e) {
        // User exists, continue to login
      }
      
      // Login
      const formData = new FormData();
      formData.append('username', demoEmail);
      formData.append('password', demoPassword);
      
      const response = await axios.post('/api/auth/login', formData);
      const { access_token } = response.data;
      
      localStorage.setItem('token', access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      await fetchUser();
    };
    
    doAutoLogin();
  }, []);

  const fetchUser = async () => {
    try {
      const response = await axios.get('/api/users/me');
      setUser(response.data);
    } catch (error) {
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await axios.post('/api/auth/login', formData);
    const { access_token } = response.data;
    
    localStorage.setItem('token', access_token);
    axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
    
    await fetchUser();
    return true;
  };

  const register = async (email, password, fullName) => {
    await axios.post('/api/auth/register', {
      email,
      password,
      full_name: fullName
    });
    return true;
  };

  const autoLogin = async () => {
    const demoEmail = 'demo@local.ai';
    const demoPassword = 'demo123';
    try {
      await register(demoEmail, demoPassword, 'Demo User');
    } catch (e) {
      // User might already exist
    }
    const formData = new FormData();
    formData.append('username', demoEmail);
    formData.append('password', demoPassword);
    const response = await axios.post('/api/auth/login', formData);
    const { access_token } = response.data;
    localStorage.setItem('token', access_token);
    axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
    await fetchUser();
    return true;
  };

  const logout = () => {
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, autoLogin, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
