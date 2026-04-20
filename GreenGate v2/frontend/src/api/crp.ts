import client from './client';
import type { CrpDocument } from '../types';

export const generateCrp = async (orgId: string): Promise<CrpDocument> => {
  const res = await client.post<CrpDocument>(`/organisations/${orgId}/crp/generate`);
  return res.data;
};

export const getLatestCrp = async (orgId: string): Promise<CrpDocument> => {
  const res = await client.get<CrpDocument>(`/organisations/${orgId}/crp/latest`);
  return res.data;
};
