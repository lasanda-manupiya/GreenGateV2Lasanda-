import client from './client';
import type { CrpDocument } from '../types';

export const generateCrp = async (orgId: string): Promise<CrpDocument> => {
  const res = await client.post<CrpDocument>(`/crp/generate`, null, {
    params: { org_id: orgId },
  });
  return res.data;
};

export const getLatestCrp = async (orgId: string): Promise<CrpDocument> => {
  const res = await client.get<CrpDocument>(`/crp/${orgId}/latest`);
  return res.data;
};
