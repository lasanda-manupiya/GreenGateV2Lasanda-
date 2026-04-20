import client from './client';
import type { Organisation, GateStatus } from '../types';

export const getOrganisation = async (orgId: string): Promise<Organisation> => {
  const res = await client.get<Organisation>(`/organisations/${orgId}`);
  return res.data;
};

export const updateOrganisation = async (
  orgId: string,
  data: Partial<Organisation>
): Promise<Organisation> => {
  const res = await client.patch<Organisation>(`/organisations/${orgId}`, data);
  return res.data;
};

export const getGateStatus = async (orgId: string): Promise<GateStatus[]> => {
  const res = await client.get<GateStatus[]>(`/organisations/${orgId}/gates`);
  return res.data;
};
