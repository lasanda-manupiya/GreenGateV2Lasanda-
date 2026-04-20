import { createContext, useState, useEffect, useCallback, type ReactNode } from 'react';
import { login as apiLogin, register as apiRegister, getMe } from '../api/auth';
import { setTokens, clearTokens, getRefreshToken } from '../api/client';
import { refreshToken as apiRefreshToken } from '../api/auth';
import type { User, LoginRequest, RegisterRequest } from '../types';

export interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (data: LoginRequest) => Promise<void>;
  logout: () => void;
  register: (data: RegisterRequest) => Promise<void>;
}

export const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!user && !!token;

  const enrichUser = (me: User): User => ({
    ...me,
    org_id: me.organisation_id,
    name: me.full_name,
  });

  useEffect(() => {
    const tryRefresh = async () => {
      const rt = getRefreshToken();
      if (rt) {
        try {
          const res = await apiRefreshToken(rt);
          setTokens(res.access_token, res.refresh_token);
          setToken(res.access_token);
          const me = await getMe();
          setUser(enrichUser(me));
        } catch {
          clearTokens();
        }
      }
      setIsLoading(false);
    };
    tryRefresh();
  }, []);

  const login = useCallback(async (data: LoginRequest) => {
    const res = await apiLogin(data);
    setTokens(res.access_token, res.refresh_token);
    setToken(res.access_token);
    const me = await getMe();
    setUser(enrichUser(me));
  }, []);

  const register = useCallback(async (data: RegisterRequest) => {
    await apiRegister(data);
    const loginRes = await apiLogin({ email: data.email, password: data.password });
    setTokens(loginRes.access_token, loginRes.refresh_token);
    setToken(loginRes.access_token);
    const me = await getMe();
    setUser(enrichUser(me));
  }, []);

  const logout = useCallback(() => {
    clearTokens();
    setToken(null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{ user, token, isAuthenticated, isLoading, login, logout, register }}
    >
      {children}
    </AuthContext.Provider>
  );
}
