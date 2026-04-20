import client from './client';
import type { User } from '../types';

export interface UserListResponse {
  users: User[];
  total: number;
}

export interface InviteUserRequest {
  email: string;
  full_name: string;
  password: string;
  role: string;
}

export const listUsers = async (): Promise<UserListResponse> => {
  const res = await client.get<UserListResponse>('/users/');
  return res.data;
};

export const inviteUser = async (data: InviteUserRequest): Promise<User> => {
  const res = await client.post<User>('/users/invite', data);
  return res.data;
};

export const updateUserRole = async (userId: string, role: string): Promise<User> => {
  const res = await client.put<User>(`/users/${userId}/role`, { role });
  return res.data;
};

export const toggleUserActive = async (userId: string): Promise<User> => {
  const res = await client.put<User>(`/users/${userId}/deactivate`);
  return res.data;
};
