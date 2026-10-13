import { createContext, useContext, useMemo, useState } from "react";
import {
  api,
  clearAuth,
  getToken,
  getUser,
  saveToken,
  saveUser,
} from "../api/api";

const AuthContext = createContext(null);

function extractUser(data) {
  return data?.user || data?.state?.user || data?.data?.user || null;
}

function extractToken(data) {
  return data?.access_token || data?.token || data?.data?.access_token || null;
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(getUser());
  const [token, setToken] = useState(getToken());

  async function login(credentials) {
    const data = await api.login(credentials);
    const nextToken = extractToken(data);

    if (!nextToken) {
      throw new Error("Login succeeded but no access token was returned.");
    }

    const nextUser = extractUser(data) || { email: credentials.email };
    saveToken(nextToken);
    saveUser(nextUser);
    setToken(nextToken);
    setUser(nextUser);

    return data;
  }

  async function signup(payload) {
    return api.signup(payload);
  }

  function logout() {
    clearAuth();
    setToken(null);
    setUser(null);
  }

  const value = useMemo(
    () => ({
      user,
      token,
      isAuthenticated: Boolean(token),
      login,
      signup,
      logout,
    }),
    [user, token],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider.");
  }
  return context;
}
