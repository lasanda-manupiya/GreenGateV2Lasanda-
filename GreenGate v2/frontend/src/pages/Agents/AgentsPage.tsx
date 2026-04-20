import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../../auth/useAuth';
import { getAgents } from '../../api/agents';
import { AgentStatusCard } from '../../components/agents/AgentStatusCard';
import { ActivityFeed } from '../../components/agents/ActivityFeed';
import { Card } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { ChevronDown, ChevronRight } from 'lucide-react';
import { useState } from 'react';
import type { Agent, AuditEntry } from '../../types';

const mockAgents: Agent[] = [
  { id: 'a1', name: 'Carbon Auditor', gate: 1, description: 'Scans financial data and builds carbon inventory', status: 'idle', last_active: new Date(Date.now() - 3600000).toISOString(), policy_profile: { auto_scan: true, confidence_threshold: 'medium', scan_frequency: 'weekly' }, actions: ['scan_invoices', 'build_inventory', 'calculate_baseline'] },
  { id: 'a2', name: 'Strategy Builder', gate: 2, description: 'Generates CRPs and aligns with frameworks', status: 'running', last_active: new Date(Date.now() - 600000).toISOString(), policy_profile: { framework_priority: 'PPN 06/21', auto_align: true, review_cycle: 'quarterly' }, actions: ['generate_crp', 'recommend_frameworks', 'calculate_sbti'] },
  { id: 'a3', name: 'Delivery Tracker', gate: 3, description: 'Tracks implementation of reduction measures', status: 'idle', last_active: new Date(Date.now() - 86400000).toISOString(), policy_profile: { tracking_interval: 'monthly', alert_threshold: 10 }, actions: ['track_measures', 'forecast_impact', 'alert_delays'] },
  { id: 'a4', name: 'Compliance Checker', gate: 4, description: 'Verifies data quality and compliance', status: 'paused', last_active: new Date(Date.now() - 172800000).toISOString(), policy_profile: { verification_level: 'limited', data_quality_min: 0.8 }, actions: ['verify_data', 'check_compliance', 'flag_anomalies'] },
  { id: 'a5', name: 'Report Writer', gate: 5, description: 'Generates framework-specific reports', status: 'idle', last_active: new Date(Date.now() - 604800000).toISOString(), policy_profile: { output_formats: ['pdf', 'docx'], auto_submit: false }, actions: ['generate_report', 'compile_evidence', 'format_submission'] },
  { id: 'a6', name: 'Security Auditor', gate: 6, description: 'Continuous security and data protection compliance', status: 'error', last_active: new Date(Date.now() - 28800000).toISOString(), policy_profile: { frameworks: ['iso27001', 'gdpr', 'nhs_dspt', 'cyber_essentials'], scan_schedule: 'weekly' }, actions: ['run_iso27001', 'run_gdpr', 'run_nhs_dspt', 'run_cyber_essentials'] },
];

const mockActivity: AuditEntry[] = [
  { id: '1', org_id: '1', gate: 1, actor_type: 'agent', actor_id: 'a1', actor_name: 'Carbon Auditor', action: 'Completed invoice scan batch #47', result: 'pass', details: 'Processed 47 invoices, extracted 12 emission-relevant line items', created_at: new Date(Date.now() - 3600000).toISOString() },
  { id: '2', org_id: '1', gate: 2, actor_type: 'agent', actor_id: 'a2', actor_name: 'Strategy Builder', action: 'CRP generation in progress', result: 'info', details: 'Generating Carbon Reduction Plan v4 with updated targets', created_at: new Date(Date.now() - 1800000).toISOString() },
  { id: '3', org_id: '1', gate: 6, actor_type: 'agent', actor_id: 'a6', actor_name: 'Security Auditor', action: 'Failed to complete ISO 27001 scan', result: 'fail', details: 'Connection timeout to evidence repository. Retry scheduled.', created_at: new Date(Date.now() - 28800000).toISOString() },
  { id: '4', org_id: '1', gate: 4, actor_type: 'agent', actor_id: 'a4', actor_name: 'Compliance Checker', action: 'Paused awaiting data refresh', result: 'warn', details: 'Scope 3 data requires update before verification can continue', created_at: new Date(Date.now() - 172800000).toISOString() },
  { id: '5', org_id: '1', gate: 1, actor_type: 'agent', actor_id: 'a1', actor_name: 'Carbon Auditor', action: 'Baseline recalculation complete', result: 'pass', details: 'Updated baseline with new Scope 2 data from utility provider', created_at: new Date(Date.now() - 86400000).toISOString() },
];

export function AgentsPage() {
  const { user } = useAuth();
  const [expandedAgent, setExpandedAgent] = useState<string | null>(null);

  const { data: agents } = useQuery({
    queryKey: ['agents', user?.org_id],
    queryFn: () => getAgents(user!.org_id),
    enabled: !!user?.org_id,
    placeholderData: mockAgents,
  });

  const allAgents = agents || mockAgents;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-[var(--color-text)]" style={{ fontFamily: 'var(--font-display)' }}>
          AI Agents
        </h1>
        <p className="text-sm text-[var(--color-text-muted)]">
          Overview of all governance agents and their current status
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {allAgents.map((agent) => (
          <AgentStatusCard key={agent.id} agent={agent} />
        ))}
      </div>

      <Card
        header={
          <h2 className="text-base font-semibold text-[var(--color-text)]">Agent Activity Timeline</h2>
        }
      >
        <ActivityFeed entries={mockActivity} maxItems={20} />
      </Card>

      <Card
        header={
          <h2 className="text-base font-semibold text-[var(--color-text)]">Policy Profiles</h2>
        }
      >
        <div className="space-y-2">
          {allAgents.map((agent) => (
            <div key={agent.id} className="border border-[var(--color-border)] rounded-lg">
              <button
                onClick={() => setExpandedAgent(expandedAgent === agent.id ? null : agent.id)}
                className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className="text-sm font-medium text-[var(--color-text)]">{agent.name}</span>
                  <Badge variant="neutral">Gate {agent.gate}</Badge>
                </div>
                {expandedAgent === agent.id ? (
                  <ChevronDown className="w-4 h-4 text-[var(--color-text-muted)]" />
                ) : (
                  <ChevronRight className="w-4 h-4 text-[var(--color-text-muted)]" />
                )}
              </button>
              {expandedAgent === agent.id && (
                <div className="px-4 pb-4 border-t border-[var(--color-border)]">
                  <div className="mt-3 space-y-2">
                    {Object.entries(agent.policy_profile).map(([key, value]) => (
                      <div key={key} className="flex items-center justify-between text-sm">
                        <span className="text-[var(--color-text-muted)] capitalize">
                          {key.replace(/_/g, ' ')}
                        </span>
                        <span className="text-[var(--color-text)] font-medium">
                          {Array.isArray(value) ? value.join(', ') : String(value)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
