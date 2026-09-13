import { createContext, useContext, useState, useCallback } from "react";
import { loginUser, registerUser } from "./services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem("resqai_user");
    return raw ? JSON.parse(raw) : null;
  });

  const persist = (token, userData) => {
    localStorage.setItem("resqai_token", token);
    localStorage.setItem("resqai_user", JSON.stringify(userData));
    setUser(userData);
  };

  const login = useCallback(async (email, password) => {
    const res = await loginUser({ email, password });
    persist(res.data.access_token, res.data.user);
    return res.data.user;
  }, []);

  const register = useCallback(async (payload) => {
    const res = await registerUser(payload);
    persist(res.data.access_token, res.data.user);
    return res.data.user;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("resqai_token");
    localStorage.removeItem("resqai_user");
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
