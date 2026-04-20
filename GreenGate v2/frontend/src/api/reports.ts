import client from './client';
import type { DashboardData } from '../types';

export const getDashboard = async (orgId: string): Promise<DashboardData> => {
  const res = await client.get<DashboardData>(`/organisations/${orgId}/dashboard`);
  return res.data;
};

export const getFrameworkReport = async (
  orgId: string,
  frameworkId: string
): Promise<Record<string, unknown>> => {
  const res = await client.get(`/organisations/${orgId}/reports/framework/${frameworkId}`);
  return res.data;
};

export const generateEvidencePack = async (
  orgId: string,
  gate?: number
): Promise<{ download_url: string; generated_at: string }> => {
  const params = gate ? { gate } : {};
  const res = await client.post(`/organisations/${orgId}/reports/evidence-pack`, null, { params });
  return res.data;
};
