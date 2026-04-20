import client from './client';
import type { EmissionsEntry } from '../types';

interface BackendEmission {
  id: string;
  organisation_id: string;
  reporting_year: number;
  scope: number;
  category: string;
  source: string | null;
  activity_data: number | null;
  activity_unit: string | null;
  emission_factor: number | null;
  emission_factor_source: string | null;
  co2e_tonnes: number | null;
  confidence_tier: string | null;
  data_source: string | null;
  evidence_ref: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

function toNum(v: unknown): number {
  if (v == null) return 0;
  const n = Number(v);
  return isNaN(n) ? 0 : n;
}

function mapEmission(e: BackendEmission): EmissionsEntry {
  return {
    id: e.id,
    org_id: e.organisation_id,
    scope: e.scope as 1 | 2 | 3,
    category: e.category,
    source: e.source || '',
    activity_data: toNum(e.activity_data),
    unit: e.activity_unit || '',
    emission_factor: toNum(e.emission_factor),
    co2e_tonnes: toNum(e.co2e_tonnes),
    confidence: (e.confidence_tier || 'medium') as 'high' | 'medium' | 'low' | 'estimated',
    data_source: e.data_source || '',
    period_start: '',
    period_end: '',
    created_at: e.created_at,
  };
}

export const getEmissions = async (
  orgId?: string,
  scope?: number,
): Promise<EmissionsEntry[]> => {
  const params: Record<string, string | number> = {};
  if (orgId) params.org_id = orgId;
  if (scope) params.scope = scope;
  const res = await client.get<BackendEmission[]>('/emissions/inventory', { params });
  return res.data.map(mapEmission);
};

export const getBaseline = async (orgId: string) => {
  const res = await client.get(`/emissions/${orgId}/baseline`);
  return res.data;
};

export const getTrajectory = async (orgId: string) => {
  const res = await client.get(`/emissions/${orgId}/trajectory`);
  return res.data;
};
