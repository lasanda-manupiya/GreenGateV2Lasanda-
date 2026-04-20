import client from './client';
import type { User } from '../types';

export interface OrgSummary {
  id: string;
  name: string;
  sector: string | null;
  country: string;
  current_gate: number;
  onboarding_complete: boolean;
  user_count: number;
  admin_email: string | null;
  created_at: string;
}

export interface PlatformStats {
  total_organisations: number;
  total_users: number;
  active_users: number;
  organisations: OrgSummary[];
}

export const getPlatformStats = async (): Promise<PlatformStats> => {
  const res = await client.get<PlatformStats>('/platform/stats');
  return res.data;
};

export const getOrgUsers = async (orgId: string): Promise<User[]> => {
  const res = await client.get<User[]>(`/platform/organisations/${orgId}/users`);
  return res.data;
};
