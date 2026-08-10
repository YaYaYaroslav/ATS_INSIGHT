import React, { createContext, useContext, useState, useCallback } from "react";
import { authApi } from "../api/endpoints.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("ats_token"));

  const login = useCallback(async (email, password) => {
    const data = await authApi.login(email, password);
    localStorage.setItem("ats_token", data.access_token);
    setToken(data.access_token);
  }, []);

  const register = useCallback(async (email, password, fullName) => {
    await authApi.register(email, password, fullName);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("ats_token");
    setToken(null);
  }, []);

  return (
    <AuthContext.Provider value={{ token, isAuthenticated: !!token, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
