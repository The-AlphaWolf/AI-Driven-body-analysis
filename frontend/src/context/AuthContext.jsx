import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check for existing token on mount
  useEffect(() => {
    const token = api.getToken();
    if (token) {
      api.getMe()
        .then((data) => setUser(data.user))
        .catch((err) => {
          // Only an actual 401 means the token is invalid — a network
          // hiccup or a Render cold-start timeout is not proof of that,
          // and wiping a good token on those just logs people out at random.
          if (err.status === 401) {
            api.removeToken();
            setUser(null);
          }
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = useCallback(async (email, password) => {
    const data = await api.login(email, password);
    setUser(data.user);
    return data;
  }, []);

  const register = useCallback(async (email, password) => {
    const data = await api.register(email, password);
    setUser(data.user);
    return data;
  }, []);

  const logout = useCallback(async () => {
    await api.logout();
    setUser(null);
  }, []);

  // The shared demo login is read-only. This only drives the interface —
  // every write is refused by the API regardless of what the client believes.
  const isDemo = Boolean(user?.is_demo);

  return (
    <AuthContext.Provider value={{ user, isDemo, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
