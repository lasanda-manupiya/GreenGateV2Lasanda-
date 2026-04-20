import { useState, useCallback } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../../auth/useAuth';
import { useAgentRun } from '../../hooks/useAgentRun';
import { getEmissions } from '../../api/emissions';
import { getAgents } from '../../api/agents';
import { Card } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { Tabs } from '../../components/ui/Tabs';
import { Table } from '../../components/ui/Table';
import { AgentStatusCard } from '../../components/agents/AgentStatusCard';
import { RuleBadge } from '../../components/governance/RuleBadge';
import { Progress } from '../../components/ui/Progress';
import { Play, ChevronDown, CheckCircle, XCircle, Link2 } from 'lucide-react';
import { CsvUploadPanel } from '../../components/emissions/CsvUploadPanel';
import type { EmissionsEntry, Agent } from '../../types';

const mockAgent: Agent = {
  id: 'a1',
  name: 'Carbon Auditor',
  gate: 1,
  description: 'Scans financial data and builds carbon inventory',
  status: 'idle',
  last_active: new Date(Date.now() - 3600000).toISOString(),
  policy_profile: { auto_scan: true, confidence_threshold: 'medium' },
  actions: ['scan_invoices', 'build_inventory', 'calculate_baseline'],
};

const mockEmissions: (EmissionsEntry & Record<string, unknown>)[] = [
  { id: '1', org_id: '1', scope: 1 as const, category: 'Stationary Combustion', source: 'Natural Gas - Office Heating', activity_data: 45000, unit: 'kWh', emission_factor: 0.000184, co2e_tonnes: 8.28, confidence: 'high' as const, data_source: 'Xero', period_start: '2025-01-01', period_end: '2025-12-31', created_at: '2025-12-15' },
  { id: '2', org_id: '1', scope: 1 as const, category: 'Mobile Combustion', source: 'Company Fleet - Diesel', activity_data: 12000, unit: 'litres', emission_factor: 0.002692, co2e_tonnes: 32.3, confidence: 'high' as const, data_source: 'Xero', period_start: '2025-01-01', period_end: '2025-12-31', created_at: '2025-12-15' },
  { id: '3', org_id: '1', scope: 2 as const, category: 'Purchased Electricity', source: 'Grid Electricity - All Sites', activity_data: 320000, unit: 'kWh', emission_factor: 0.000207, co2e_tonnes: 66.24, confidence: 'high' as const, data_source: 'Utility Bills', period_start: '2025-01-01', period_end: '2025-12-31', created_at: '2025-12-15' },
  { id: '4', org_id: '1', scope: 2 as const, category: 'Purchased Heat', source: 'District Heating', activity_data: 50000, unit: 'kWh', emission_factor: 0.000168, co2e_tonnes: 8.4, confidence: 'medium' as const, data_source: 'Sage', period_start: '2025-01-01', period_end: '2025-12-31', created_at: '2025-12-15' },
  { id: '5', org_id: '1', scope: 3 as const, category: 'Business Travel', source: 'Flights - Short Haul', activity_data: 85, unit: 'flights', emission_factor: 0.255, co2e_tonnes: 21.68, confidence: 'medium' as const, data_source: 'Expense Reports', period_start: '2025-01-01', period_end: '2025-12-31', created_at: '2025-12-15' },
  { id: '6', org_id: '1', scope: 3 as const, category: 'Purchased Goods', source: 'IT Equipment', activity_data: 150000, unit: 'GBP', emission_factor: 0.00032, co2e_tonnes: 48.0, confidence: 'low' as const, data_source: 'Xero', period_start: '2025-01-01', period_end: '2025-12-31', created_at: '2025-12-15' },
  { id: '7', org_id: '1', scope: 3 as const, category: 'Employee Commuting', source: 'Staff Commuting Survey', activity_data: 120, unit: 'employees', emission_factor: 1.2, co2e_tonnes: 144.0, confidence: 'estimated' as const, data_source: 'Survey', period_start: '2025-01-01', period_end: '2025-12-31', created_at: '2025-12-15' },
  { id: '8', org_id: '1', scope: 3 as const, category: 'Waste', source: 'General Waste Disposal', activity_data: 25, unit: 'tonnes', emission_factor: 0.467, co2e_tonnes: 11.68, confidence: 'medium' as const, data_source: 'Waste Contractor', period_start: '2025-01-01', period_end: '2025-12-31', created_at: '2025-12-15' },
];

const confidenceVariant: Record<string, 'success' | 'warning' | 'error' | 'neutral'> = {
  high: 'success',
  medium: 'warning',
  low: 'error',
  estimated: 'error',
};

const gateRules = [
  { code: 'G1-001', description: 'Carbon inventory covers all material Scope 1 sources', severity: 'blocker' as const, passed: true },
  { code: 'G1-002', description: 'Carbon inventory covers all material Scope 2 sources', severity: 'blocker' as const, passed: true },
  { code: 'G1-003', description: 'Scope 3 screening completed for all 15 categories', severity: 'blocker' as const, passed: false },
  { code: 'G1-004', description: 'Baseline year defined and documented', severity: 'blocker' as const, passed: true },
  { code: 'G1-005', description: 'Data quality score above minimum threshold', severity: 'warning' as const, passed: true },
  { code: 'G1-006', description: 'Emission factors from approved sources (DEFRA/GHG Protocol)', severity: 'warning' as const, passed: true },
  { code: 'G1-007', description: 'Organisational boundary documented', severity: 'info' as const, passed: true },
];

export function Gate1Page() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [actionMenuOpen, setActionMenuOpen] = useState(false);
  const agentRun = useAgentRun();

  const handleUploadSuccess = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ['emissions'] });
  }, [queryClient]);

  // Fetch real carbon_auditor agent so we have its id to call /agents/{id}/run
  const { data: agents } = useQuery({
    queryKey: ['agents', user?.org_id],
    queryFn: () => getAgents(user!.org_id),
    enabled: !!user?.org_id,
  });
  const carbonAuditor = agents?.find((a) => a.name === 'Carbon Auditor' || a.gate === 1);
  const liveAgent = carbonAuditor ?? mockAgent;

  const handleRunAction = (action: string) => {
    setActionMenuOpen(false);
    if (!carbonAuditor) {
      // eslint-disable-next-line no-console
      console.warn('Carbon Auditor agent not found in API response');
      return;
    }
    agentRun.mutate({ agentId: carbonAuditor.id, action });
  };

  const { data: emissions } = useQuery({
    queryKey: ['emissions', user?.org_id],
    queryFn: () => getEmissions(user!.org_id),
    enabled: !!user?.org_id,
    placeholderData: mockEmissions as EmissionsEntry[],
  });

  const allEmissions = (emissions || mockEmissions) as (EmissionsEntry & Record<string, unknown>)[];

  const scope1Total = allEmissions.filter((e) => e.scope === 1).reduce((s, e) => s + e.co2e_tonnes, 0);
  const scope2Total = allEmissions.filter((e) => e.scope === 2).reduce((s, e) => s + e.co2e_tonnes, 0);
  const scope3Total = allEmissions.filter((e) => e.scope === 3).reduce((s, e) => s + e.co2e_tonnes, 0);
  const total = scope1Total + scope2Total + scope3Total;

  const columns = [
    { key: 'source', header: 'Source', sortable: true },
    { key: 'category', header: 'Category', sortable: true },
    { key: 'activity_data', header: 'Activity Data', sortable: true, render: (row: EmissionsEntry & Record<string, unknown>) => row.activity_data.toLocaleString() },
    { key: 'unit', header: 'Unit' },
    { key: 'emission_factor', header: 'EF', render: (row: EmissionsEntry & Record<string, unknown>) => row.emission_factor.toFixed(6) },
    { key: 'co2e_tonnes', header: 'CO2e (t)', sortable: true, render: (row: EmissionsEntry & Record<string, unknown>) => row.co2e_tonnes.toFixed(2) },
    { key: 'confidence', header: 'Confidence', render: (row: EmissionsEntry & Record<string, unknown>) => <Badge variant={confidenceVariant[row.confidence]}>{row.confidence}</Badge> },
    { key: 'data_source', header: 'Data Source' },
  ];

  const renderEmissionsTable = (scope?: number) => {
    const filtered = scope ? allEmissions.filter((e) => e.scope === scope) : allEmissions;
    return <Table columns={columns} data={filtered} pageSize={10} />;
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-text)]" style={{ fontFamily: 'var(--font-display)' }}>
            Gate 1: Assess — Carbon Auditor
          </h1>
          <p className="text-sm text-[var(--color-text-muted)]">
            Build your carbon inventory and establish baseline emissions
          </p>
        </div>
        <div className="relative">
          <Button
            onClick={() => setActionMenuOpen(!actionMenuOpen)}
            disabled={agentRun.isPending || !carbonAuditor}
          >
            <Play className="w-4 h-4" />
            {agentRun.isPending ? 'Running…' : 'Run Carbon Auditor'}
            <ChevronDown className="w-4 h-4" />
          </Button>
          {actionMenuOpen && (
            <div className="absolute right-0 mt-2 w-56 bg-white border border-[var(--color-border)] rounded-lg shadow-lg z-10">
              {['scan_invoices', 'build_inventory', 'calculate_baseline'].map((action) => (
                <button
                  key={action}
                  onClick={() => handleRunAction(action)}
                  disabled={agentRun.isPending}
                  className="block w-full text-left px-4 py-2.5 text-sm hover:bg-gray-50 disabled:opacity-50 text-[var(--color-text)]"
                >
                  {action.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      <AgentStatusCard agent={liveAgent} />

      <CsvUploadPanel onSuccess={handleUploadSuccess} />

      <Tabs
        tabs={[
          { id: 'scope1', label: 'Scope 1', content: renderEmissionsTable(1) },
          { id: 'scope2', label: 'Scope 2', content: renderEmissionsTable(2) },
          { id: 'scope3', label: 'Scope 3', content: renderEmissionsTable(3) },
          { id: 'all', label: 'All', content: renderEmissionsTable() },
        ]}
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card header={<h2 className="text-base font-semibold text-[var(--color-text)]">Baseline Summary</h2>}>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-[var(--color-text-muted)]">Scope 1</span>
              <span className="text-sm font-medium">{scope1Total.toFixed(1)} tCO2e</span>
            </div>
            <Progress value={scope1Total} max={total} label="" showPercentage={false} size="sm" color="bg-[#1B6B3A]" />
            <div className="flex justify-between items-center">
              <span className="text-sm text-[var(--color-text-muted)]">Scope 2</span>
              <span className="text-sm font-medium">{scope2Total.toFixed(1)} tCO2e</span>
            </div>
            <Progress value={scope2Total} max={total} label="" showPercentage={false} size="sm" color="bg-[#D4A843]" />
            <div className="flex justify-between items-center">
              <span className="text-sm text-[var(--color-text-muted)]">Scope 3</span>
              <span className="text-sm font-medium">{scope3Total.toFixed(1)} tCO2e</span>
            </div>
            <Progress value={scope3Total} max={total} label="" showPercentage={false} size="sm" color="bg-[#6B7280]" />
            <div className="pt-3 border-t border-[var(--color-border)] flex justify-between">
              <span className="text-sm font-semibold text-[var(--color-text)]">Total</span>
              <span className="text-sm font-bold text-[var(--color-text)]">{total.toFixed(1)} tCO2e</span>
            </div>
          </div>
        </Card>

        <Card header={<h2 className="text-base font-semibold text-[var(--color-text)]">Data Sources</h2>}>
          <div className="space-y-3">
            {[
              { name: 'Xero', status: 'connected', records: 47 },
              { name: 'Sage', status: 'connected', records: 12 },
              { name: 'Utility Bills', status: 'manual', records: 6 },
              { name: 'Expense Reports', status: 'manual', records: 85 },
            ].map((src) => (
              <div key={src.name} className="flex items-center justify-between py-2 border-b border-[var(--color-border)] last:border-0">
                <div className="flex items-center gap-2">
                  <Link2 className="w-4 h-4 text-[var(--color-text-muted)]" />
                  <span className="text-sm font-medium text-[var(--color-text)]">{src.name}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={src.status === 'connected' ? 'success' : 'neutral'}>
                    {src.status}
                  </Badge>
                  <span className="text-xs text-[var(--color-text-muted)]">{src.records} records</span>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card header={<h2 className="text-base font-semibold text-[var(--color-text)]">Governance Checkpoint</h2>}>
          <div className="space-y-2">
            {gateRules.map((rule) => (
              <div key={rule.code} className="flex items-start gap-2 py-1.5">
                {rule.passed ? (
                  <CheckCircle className="w-4 h-4 text-[var(--color-success)] shrink-0 mt-0.5" />
                ) : (
                  <XCircle className="w-4 h-4 text-[var(--color-error)] shrink-0 mt-0.5" />
                )}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-[var(--color-text-muted)]">{rule.code}</span>
                    <RuleBadge severity={rule.severity} />
                  </div>
                  <p className="text-xs text-[var(--color-text)] mt-0.5">{rule.description}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
