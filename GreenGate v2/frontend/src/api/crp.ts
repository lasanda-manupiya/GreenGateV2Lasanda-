import client from './client';
import type { CrpDocument } from '../types';

export interface GenerateCrpResponse {
  status: string;
  crp: Record<string, unknown>;
  audit_entries: unknown[];
  llm_runtime?: Record<string, unknown>;
}

export const generateCrp = async (orgId: string): Promise<GenerateCrpResponse> => {
  const res = await client.post<GenerateCrpResponse>(`/crp/generate`, null, {
    params: { org_id: orgId },
  });
  return res.data;
};

export const getLatestCrp = async (orgId: string): Promise<CrpDocument> => {
  const res = await client.get<CrpDocument>(`/crp/${orgId}/latest`);
  return res.data;
};
