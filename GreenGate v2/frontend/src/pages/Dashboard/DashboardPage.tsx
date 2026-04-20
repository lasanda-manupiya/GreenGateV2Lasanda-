import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../../auth/useAuth';
import { getDashboard } from '../../api/reports';
import { KpiCard } from '../../components/charts/KpiCard';
import { EmissionsChart } from '../../components/charts/EmissionsChart';
import { GateProgressBar } from '../../components/gates/GateProgressBar';
import { ActivityFeed } from '../../components/agents/ActivityFeed';
import { Card } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import {
  BarChart3,
  ShieldCheck,
  Database,
  Bot,
  Play,
  FileText,
  Archive,
  AlertTriangle,
  Calendar,
} from 'lucide-react';
import type { DashboardData } from '../../types';

const mockDashboard: DashboardData = {
  total_emissions: 2847,
  compliance_score: 72,
  data_coverage: 85,
  active_agents: 3,
  emissions_by_scope: [
    { scope: 1, total: 450 },
    { scope: 2, total: 820 },
    { scope: 3, total: 1577 },
  ],
  recent_activity: [
    {
      id: '1',
      org_id: '1',
      gate: 1,
      actor_type: 'agent',
      actor_id: 'a1',
      actor_name: 'Carbon Auditor',
      action: 'Scanned 47 invoices from Xero',
      result: 'pass',
      details: 'Extracted emissions data from 47 purchase invoices for Q3 2025',
      created_at: new Date(Date.now() - 3600000).toISOString(),
    },
    {
      id: '2',
      org_id: '1',
      gate: 2,
      actor_type: 'agent',
      actor_id: 'a2',
      actor_name: 'Strategy Builder',
      action: 'Generated CRP draft v3',
      result: 'pass',
      details: 'Carbon Reduction Plan aligned with PPN 06/21 requirements',
      created_at: new Date(Date.now() - 7200000).toISOString(),
    },
    {
      id: '3',
      org_id: '1',
      gate: 1,
      actor_type: 'agent',
      actor_id: 'a1',
      actor_name: 'Carbon Auditor',
      action: 'Baseline calculation updated',
      result: 'warn',
      details: 'Scope 3 data has low confidence for 3 categories',
      created_at: new Date(Date.now() - 14400000).toISOString(),
    },
    {
      id: '4',
      org_id: '1',
      gate: 6,
      actor_type: 'agent',
      actor_id: 'a6',
      actor_name: 'Security Auditor',
      action: 'ISO 27001 controls check',
      result: 'fail',
      details: 'A.12.3.1 Information backup - evidence not found',
      created_at: new Date(Date.now() - 28800000).toISOString(),
    },
    {
      id: '5',
      org_id: '1',
      gate: 4,
      actor_type: 'user',
      actor_id: 'u1',
      actor_name: 'Jane Smith',
      action: 'Approved Gate 1 submission',
      result: 'pass',
      details: 'Carbon inventory approved by board sponsor',
      created_at: new Date(Date.now() - 43200000).toISOString(),
    },
  ],
  regulatory_alerts: [
    {
      id: '1',
      framework: 'PPN 06/21',
      title: 'CRP submission deadline',
      deadline: '2026-04-01',
      severity: 'high',
      description: 'Carbon Reduction Plan must be submitted with next procurement bid',
    },
    {
      id: '2',
      framework: 'CDP',
      title: 'CDP disclosure window opens',
      deadline: '2026-05-15',
      severity: 'medium',
      description: 'Annual CDP questionnaire available for completion',
    },
    {
      id: '3',
      framework: 'UK SRS',
      title: 'UK SRS reporting period end',
      deadline: '2026-06-30',
      severity: 'low',
      description: 'End of reporting period for UK Sustainability Reporting Standards',
    },
  ],
  gates: [
    { gate: 1, name: 'Assess', agent: 'Carbon Auditor', status: 'complete', progress: 100, description: 'Build carbon inventory and baseline' },
    { gate: 2, name: 'Plan', agent: 'Strategy Builder', status: 'active', progress: 65, description: 'Create Carbon Reduction Plan' },
    { gate: 3, name: 'Implement', agent: 'Delivery Tracker', status: 'locked', progress: 0, description: 'Track reduction measures' },
    { gate: 4, name: 'Verify', agent: 'Compliance Checker', status: 'locked', progress: 0, description: 'Verify and validate data' },
    { gate: 5, name: 'Report', agent: 'Report Writer', status: 'locked', progress: 0, description: 'Generate framework reports' },
    { gate: 6, name: 'Secure', agent: 'Security Auditor', status: 'active', progress: 42, description: 'Continuous security compliance' },
  ],
};

const severityVariant: Record<string, 'error' | 'warning' | 'info'> = {
  high: 'error',
  medium: 'warning',
  low: 'info',
};

export function DashboardPage() {
  const { user } = useAuth();

  const { data: dashboard } = useQuery<DashboardData>({
    queryKey: ['dashboard', user?.org_id],
    queryFn: () => getDashboard(user!.org_id),
    enabled: !!user?.org_id,
    placeholderData: mockDashboard,
  });

  const d = dashboard || mockDashboard;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1
            className="text-2xl font-bold text-[var(--color-text)]"
            style={{ fontFamily: 'var(--font-display)' }}
          >
            Welcome back{user?.name ? `, ${user.name.split(' ')[0]}` : ''}
          </h1>
          <p className="text-sm text-[var(--color-text-muted)]">
            Here is your sustainability governance overview.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="secondary" size="sm">
            <Play className="w-4 h-4" />
            Run Carbon Audit
          </Button>
          <Button variant="secondary" size="sm">
            <FileText className="w-4 h-4" />
            Generate CRP
          </Button>
          <Button variant="secondary" size="sm">
            <Archive className="w-4 h-4" />
            View Evidence
          </Button>
        </div>
      </div>

      <Card>
        <GateProgressBar gates={d.gates} />
      </Card>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          title="Total Emissions"
          value={d.total_emissions.toLocaleString()}
          unit="tCO2e"
          trend="down"
          trendValue="-8% vs last year"
          icon={<BarChart3 className="w-5 h-5 text-[var(--color-primary)]" />}
        />
        <KpiCard
          title="Compliance Score"
          value={d.compliance_score}
          unit="%"
          trend="up"
          trendValue="+5% this month"
          icon={<ShieldCheck className="w-5 h-5 text-[var(--color-primary)]" />}
        />
        <KpiCard
          title="Data Coverage"
          value={d.data_coverage}
          unit="%"
          trend="up"
          trendValue="+12% since onboarding"
          icon={<Database className="w-5 h-5 text-[var(--color-primary)]" />}
        />
        <KpiCard
          title="Active Agents"
          value={d.active_agents}
          unit="of 6"
          trend="flat"
          icon={<Bot className="w-5 h-5 text-[var(--color-primary)]" />}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card
            header={
              <h2 className="text-base font-semibold text-[var(--color-text)]">
                Emissions by Scope
              </h2>
            }
          >
            <EmissionsChart data={d.emissions_by_scope} />
          </Card>
        </div>

        <div>
          <Card
            header={
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-[var(--color-warning)]" />
                <h2 className="text-base font-semibold text-[var(--color-text)]">
                  Regulatory Alerts
                </h2>
              </div>
            }
          >
            <div className="space-y-3">
              {d.regulatory_alerts.map((alert) => (
                <div
                  key={alert.id}
                  className="p-3 rounded-lg border border-[var(--color-border)] hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center gap-2 mb-1">
                    <Badge variant={severityVariant[alert.severity]}>{alert.framework}</Badge>
                  </div>
                  <h3 className="text-sm font-medium text-[var(--color-text)]">{alert.title}</h3>
                  <p className="text-xs text-[var(--color-text-muted)] mt-0.5">
                    {alert.description}
                  </p>
                  <div className="flex items-center gap-1 mt-2 text-xs text-[var(--color-text-muted)]">
                    <Calendar className="w-3 h-3" />
                    {new Date(alert.deadline).toLocaleDateString('en-GB', {
                      day: 'numeric',
                      month: 'short',
                      year: 'numeric',
                    })}
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>

      <Card
        header={
          <h2 className="text-base font-semibold text-[var(--color-text)]">Recent Activity</h2>
        }
      >
        <ActivityFeed entries={d.recent_activity} />
      </Card>
    </div>
  );
}
