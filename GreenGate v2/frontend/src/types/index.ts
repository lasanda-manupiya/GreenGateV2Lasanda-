export interface Organisation {
  id: string;
  name: string;
  sector: string;
  size: string;
  country: string;
  frameworks: string[];
  onboarded: boolean;
  created_at: string;
  updated_at: string;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  name?: string;
  role: 'superadmin' | 'admin' | 'editor' | 'viewer';
  organisation_id: string;
  /** Alias for organisation_id used across pages */
  org_id: string;
  is_director: boolean;
  is_active: boolean;
  organisation?: Organisation;
  created_at: string;
}

export interface Framework {
  id: string;
  code: string;
  name: string;
  description: string;
  version: string;
  category: string;
}

export interface Rule {
  id: string;
  framework_id: string;
  gate: number;
  code: string;
  description: string;
  severity: 'blocker' | 'warning' | 'info';
  auto_check: boolean;
}

export interface Agent {
  id: string;
  name: string;
  gate: number;
  description: string;
  status: 'idle' | 'running' | 'paused' | 'error';
  last_active: string | null;
  policy_profile: Record<string, unknown>;
  actions: string[];
}

export interface EmissionsEntry {
  id: string;
  org_id: string;
  scope: 1 | 2 | 3;
  category: string;
  source: string;
  activity_data: number;
  unit: string;
  emission_factor: number;
  co2e_tonnes: number;
  confidence: 'high' | 'medium' | 'low' | 'estimated';
  data_source: string;
  period_start: string;
  period_end: string;
  created_at: string;
}

export interface EmissionsBaseline {
  id: string;
  org_id: string;
  base_year: number;
  scope1_total: number;
  scope2_total: number;
  scope3_total: number;
  total: number;
  methodology: string;
  verified: boolean;
  created_at: string;
}

export interface TrajectoryPoint {
  year: number;
  target_emissions: number;
  actual_emissions: number | null;
  reduction_pct: number;
}

export interface Submission {
  id: string;
  org_id: string;
  framework_id: string;
  gate: number;
  status: 'draft' | 'pending_review' | 'approved' | 'rejected';
  data: Record<string, unknown>;
  submitted_by: string;
  reviewed_by: string | null;
  created_at: string;
  updated_at: string;
}

export interface AuditEntry {
  id: string;
  org_id: string;
  gate: number;
  actor_type: 'user' | 'agent';
  actor_id: string;
  actor_name: string;
  action: string;
  result: 'pass' | 'fail' | 'warn' | 'info';
  details: string;
  created_at: string;
}

export interface CrpDocument {
  id: string;
  org_id: string;
  version: number;
  status: 'draft' | 'final';
  sections: CrpSection[];
  ppn006_alignment: Record<string, boolean>;
  created_at: string;
}

export interface CrpSection {
  title: string;
  content: string;
  aligned: boolean;
}

export interface SecurityCheck {
  id: string;
  org_id: string;
  framework: string;
  check_code: string;
  description: string;
  status: 'pass' | 'fail' | 'not_started';
  evidence_ref: string;
  notes: string;
  checked_at: string | null;
}

export interface GateStatus {
  gate: number;
  name: string;
  agent: string;
  status: 'locked' | 'active' | 'complete';
  progress: number;
  description: string;
}

export interface DashboardData {
  total_emissions: number;
  compliance_score: number;
  data_coverage: number;
  active_agents: number;
  emissions_by_scope: { scope: number; total: number }[];
  recent_activity: AuditEntry[];
  regulatory_alerts: RegulatoryAlert[];
  gates: GateStatus[];
}

export interface RegulatoryAlert {
  id: string;
  framework: string;
  title: string;
  deadline: string;
  severity: 'high' | 'medium' | 'low';
  description: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  full_name: string;
  email: string;
  password: string;
  organisation_name: string;
  sector?: string;
  role?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}
