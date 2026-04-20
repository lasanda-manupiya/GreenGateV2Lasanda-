import client from './client';
import type { Agent } from '../types';

// Agents are global (shared across orgs on the backend) — the backend routes them
// under /api/v1/agents/... and pulls the org from the authenticated user's JWT.
// We keep the `orgId` param in the signatures for call-site convenience, but it's
// only used when an action needs to target a specific org explicitly.

// Backend returns `AgentResponse` which uses snake_case with different field names
// (`gate_number`, `last_active_at`, no `actions`). The frontend `Agent` type uses
// `gate`, `last_active`, `actions[]`. We transform at the API boundary so every
// page that already consumes `Agent` keeps working.
interface BackendAgent {
  id: string;
  name: string;
  agent_type: string;
  gate_number: number;
  description: string | null;
  status: string;
  policy_profile: Record<string, unknown> | null;
  tool_permissions: unknown[] | null;
  last_active_at: string | null;
  created_at: string;
}

const ACTIONS_BY_TYPE: Record<string, string[]> = {
  carbon_auditor: ['scan_invoices', 'build_inventory', 'calculate_baseline'],
  strategy_builder: ['generate_crp', 'calculate_sbti_target', 'recommend_frameworks'],
  progress_tracker: ['track_progress', 'forecast_trajectory', 'flag_deviations'],
  audit_prep: ['generate_evidence_pack', 'run_readiness_check', 'pre_audit_review'],
  report_writer: ['list_available_reports', 'compile_disclosure', 'generate_report'],
  security_auditor: ['run_iso27001', 'run_gdpr', 'run_nhs_dspt', 'run_cyber_essentials'],
};

function toFrontendAgent(b: BackendAgent): Agent {
  return {
    id: b.id,
    name: b.name,
    gate: b.gate_number,
    description: b.description ?? '',
    status: (['idle', 'running', 'paused', 'error'].includes(b.status)
      ? b.status
      : 'idle') as Agent['status'],
    last_active: b.last_active_at,
    policy_profile: b.policy_profile ?? {},
    actions: ACTIONS_BY_TYPE[b.agent_type] ?? [],
  };
}

export const getAgents = async (_orgId?: string): Promise<Agent[]> => {
  const res = await client.get<BackendAgent[]>(`/agents/`);
  return res.data.map(toFrontendAgent);
};

export const getAgentStatus = async (_orgId: string, agentId: string): Promise<Agent> => {
  const res = await client.get<BackendAgent>(`/agents/${agentId}/status`);
  return toFrontendAgent(res.data);
};

export const runAgent = async (
  orgId: string,
  agentId: string,
  action: string,
  extraPayload: Record<string, unknown> = {}
): Promise<{ status: string; result: Record<string, unknown>; audit_entries: string[] }> => {
  const res = await client.post(`/agents/${agentId}/run`, {
    action,
    payload: { organisation_id: orgId, ...extraPayload },
  });
  return res.data;
};
