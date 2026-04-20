import client from './client';
import type { AuthResponse, LoginRequest, RegisterRequest, User } from '../types';

export const login = async (data: LoginRequest): Promise<AuthResponse> => {
  const res = await client.post<AuthResponse>('/auth/login', data);
  return res.data;
};

export const register = async (data: RegisterRequest): Promise<User> => {
  const res = await client.post<User>('/auth/register', data);
  return res.data;
};

export const refreshToken = async (token: string): Promise<AuthResponse> => {
  const res = await client.post<AuthResponse>('/auth/refresh', { token });
  return res.data;
};

export const getMe = async (): Promise<User> => {
  const res = await client.get<User>('/auth/me');
  return res.data;
};
