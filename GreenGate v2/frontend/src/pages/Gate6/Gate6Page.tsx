import { Card } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { Tabs } from '../../components/ui/Tabs';
import { AgentStatusCard } from '../../components/agents/AgentStatusCard';
import { Play, ShieldCheck, AlertTriangle } from 'lucide-react';
import type { Agent, SecurityCheck } from '../../types';

const mockAgent: Agent = {
  id: 'a6',
  name: 'Security Auditor',
  gate: 6,
  description: 'Continuous security and data protection compliance',
  status: 'idle',
  last_active: new Date(Date.now() - 28800000).toISOString(),
  policy_profile: { frameworks: ['iso27001', 'gdpr', 'nhs_dspt', 'cyber_essentials'] },
  actions: ['run_iso27001', 'run_gdpr', 'run_nhs_dspt', 'run_cyber_essentials'],
};

interface FrameworkChecks {
  id: string;
  name: string;
  checks: SecurityCheck[];
}

const mockFrameworkChecks: FrameworkChecks[] = [
  {
    id: 'iso27001',
    name: 'ISO 27001',
    checks: [
      { id: 'c1', org_id: '1', framework: 'iso27001', check_code: 'A.5.1', description: 'Information security policies', status: 'pass', evidence_ref: 'DOC-ISP-001', notes: 'Policy document v3.2 reviewed and approved', checked_at: '2026-03-01T10:00:00Z' },
      { id: 'c2', org_id: '1', framework: 'iso27001', check_code: 'A.6.1', description: 'Internal organisation - security roles', status: 'pass', evidence_ref: 'DOC-ORG-002', notes: 'CISO appointed, roles documented in RACI matrix', checked_at: '2026-03-01T10:05:00Z' },
      { id: 'c3', org_id: '1', framework: 'iso27001', check_code: 'A.8.1', description: 'Asset management - inventory', status: 'pass', evidence_ref: 'DOC-AST-003', notes: 'CMDB up to date, quarterly review scheduled', checked_at: '2026-03-01T10:10:00Z' },
      { id: 'c4', org_id: '1', framework: 'iso27001', check_code: 'A.9.1', description: 'Access control policy', status: 'pass', evidence_ref: 'DOC-ACC-004', notes: 'RBAC implemented, MFA enforced', checked_at: '2026-03-01T10:15:00Z' },
      { id: 'c5', org_id: '1', framework: 'iso27001', check_code: 'A.12.3', description: 'Information backup', status: 'fail', evidence_ref: '', notes: 'Backup testing evidence not found', checked_at: '2026-03-01T10:20:00Z' },
      { id: 'c6', org_id: '1', framework: 'iso27001', check_code: 'A.14.1', description: 'Security requirements for information systems', status: 'not_started', evidence_ref: '', notes: '', checked_at: null },
      { id: 'c7', org_id: '1', framework: 'iso27001', check_code: 'A.16.1', description: 'Incident management', status: 'pass', evidence_ref: 'DOC-INC-007', notes: 'IR plan in place, last drill: Feb 2026', checked_at: '2026-03-01T10:30:00Z' },
      { id: 'c8', org_id: '1', framework: 'iso27001', check_code: 'A.18.1', description: 'Compliance with legal requirements', status: 'pass', evidence_ref: 'DOC-LEG-008', notes: 'Legal register maintained', checked_at: '2026-03-01T10:35:00Z' },
    ],
  },
  {
    id: 'gdpr',
    name: 'GDPR',
    checks: [
      { id: 'g1', org_id: '1', framework: 'gdpr', check_code: 'Art.5', description: 'Principles of processing', status: 'pass', evidence_ref: 'DOC-GDP-001', notes: 'Privacy policy aligned with 7 principles', checked_at: '2026-03-01T11:00:00Z' },
      { id: 'g2', org_id: '1', framework: 'gdpr', check_code: 'Art.6', description: 'Lawful basis for processing', status: 'pass', evidence_ref: 'DOC-GDP-002', notes: 'Processing activities mapped to legal bases', checked_at: '2026-03-01T11:05:00Z' },
      { id: 'g3', org_id: '1', framework: 'gdpr', check_code: 'Art.13', description: 'Information to data subjects', status: 'pass', evidence_ref: 'DOC-GDP-003', notes: 'Privacy notices updated March 2026', checked_at: '2026-03-01T11:10:00Z' },
      { id: 'g4', org_id: '1', framework: 'gdpr', check_code: 'Art.30', description: 'Records of processing activities', status: 'fail', evidence_ref: '', notes: 'ROPA incomplete for 2 processing activities', checked_at: '2026-03-01T11:15:00Z' },
      { id: 'g5', org_id: '1', framework: 'gdpr', check_code: 'Art.35', description: 'Data Protection Impact Assessment', status: 'pass', evidence_ref: 'DOC-GDP-005', notes: 'DPIA completed for all high-risk processing', checked_at: '2026-03-01T11:20:00Z' },
      { id: 'g6', org_id: '1', framework: 'gdpr', check_code: 'Art.37', description: 'Data Protection Officer', status: 'pass', evidence_ref: 'DOC-GDP-006', notes: 'DPO appointed and registered with ICO', checked_at: '2026-03-01T11:25:00Z' },
    ],
  },
  {
    id: 'nhs_dspt',
    name: 'NHS DSPT',
    checks: [
      { id: 'n1', org_id: '1', framework: 'nhs_dspt', check_code: 'NDG-1', description: 'Personal confidential data', status: 'pass', evidence_ref: 'DOC-NHS-001', notes: 'Caldicott principles applied', checked_at: '2026-03-01T12:00:00Z' },
      { id: 'n2', org_id: '1', framework: 'nhs_dspt', check_code: 'NDG-3', description: 'Staff training', status: 'pass', evidence_ref: 'DOC-NHS-002', notes: '95% staff completed IG training', checked_at: '2026-03-01T12:05:00Z' },
      { id: 'n3', org_id: '1', framework: 'nhs_dspt', check_code: 'NDG-7', description: 'Data security standards', status: 'not_started', evidence_ref: '', notes: '', checked_at: null },
      { id: 'n4', org_id: '1', framework: 'nhs_dspt', check_code: 'NDG-10', description: 'Accountability framework', status: 'pass', evidence_ref: 'DOC-NHS-004', notes: 'SIRO and Caldicott Guardian appointed', checked_at: '2026-03-01T12:15:00Z' },
    ],
  },
  {
    id: 'cyber_essentials',
    name: 'Cyber Essentials',
    checks: [
      { id: 'ce1', org_id: '1', framework: 'cyber_essentials', check_code: 'CE-1', description: 'Firewalls and Internet Gateways', status: 'pass', evidence_ref: 'DOC-CE-001', notes: 'Firewall rules reviewed quarterly', checked_at: '2026-03-01T13:00:00Z' },
      { id: 'ce2', org_id: '1', framework: 'cyber_essentials', check_code: 'CE-2', description: 'Secure Configuration', status: 'pass', evidence_ref: 'DOC-CE-002', notes: 'CIS benchmarks applied to all systems', checked_at: '2026-03-01T13:05:00Z' },
      { id: 'ce3', org_id: '1', framework: 'cyber_essentials', check_code: 'CE-3', description: 'User Access Control', status: 'pass', evidence_ref: 'DOC-CE-003', notes: 'Least privilege enforced, quarterly access reviews', checked_at: '2026-03-01T13:10:00Z' },
      { id: 'ce4', org_id: '1', framework: 'cyber_essentials', check_code: 'CE-4', description: 'Malware Protection', status: 'pass', evidence_ref: 'DOC-CE-004', notes: 'EDR deployed on all endpoints', checked_at: '2026-03-01T13:15:00Z' },
      { id: 'ce5', org_id: '1', framework: 'cyber_essentials', check_code: 'CE-5', description: 'Patch Management', status: 'fail', evidence_ref: '', notes: '3 critical patches overdue by > 14 days', checked_at: '2026-03-01T13:20:00Z' },
    ],
  },
];

const statusVariant: Record<string, 'success' | 'error' | 'neutral'> = {
  pass: 'success',
  fail: 'error',
  not_started: 'neutral',
};

const remediation = [
  { framework: 'ISO 27001', check: 'A.12.3', issue: 'Backup testing evidence not found', recommendation: 'Schedule and document quarterly backup restoration tests. Retain evidence of successful restores.', priority: 'High' },
  { framework: 'GDPR', check: 'Art.30', issue: 'ROPA incomplete for 2 processing activities', recommendation: 'Complete Records of Processing Activities for employee health monitoring and third-party marketing data.', priority: 'Medium' },
  { framework: 'Cyber Essentials', check: 'CE-5', issue: 'Critical patches overdue', recommendation: 'Apply patches CVE-2026-1234, CVE-2026-1235, CVE-2026-1236 within 14 days. Review patch management SLA.', priority: 'High' },
];

export function Gate6Page() {
  const renderChecklist = (fw: FrameworkChecks) => {
    const passed = fw.checks.filter((c) => c.status === 'pass').length;
    const total = fw.checks.length;

    return (
      <div className="space-y-4">
        <div className="flex items-center gap-4 mb-4">
          <Card className="flex-1">
            <div className="text-center">
              <p className="text-2xl font-bold text-[var(--color-text)]" style={{ fontFamily: 'var(--font-display)' }}>
                {passed}/{total}
              </p>
              <p className="text-xs text-[var(--color-text-muted)]">Controls Passed</p>
            </div>
          </Card>
          <Card className="flex-1">
            <div className="text-center">
              <p className="text-2xl font-bold text-[var(--color-text)]" style={{ fontFamily: 'var(--font-display)' }}>
                {Math.round((passed / total) * 100)}%
              </p>
              <p className="text-xs text-[var(--color-text-muted)]">Compliance Rate</p>
            </div>
          </Card>
        </div>

        <div className="space-y-2">
          {fw.checks.map((check) => (
            <div key={check.id} className="p-4 border border-[var(--color-border)] rounded-lg">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-mono font-medium text-[var(--color-primary)]">
                      {check.check_code}
                    </span>
                    <Badge variant={statusVariant[check.status]}>{check.status.replace('_', ' ')}</Badge>
                  </div>
                  <p className="text-sm text-[var(--color-text)]">{check.description}</p>
                  {check.notes && (
                    <p className="text-xs text-[var(--color-text-muted)] mt-1">{check.notes}</p>
                  )}
                </div>
                <div className="text-right shrink-0">
                  {check.evidence_ref && (
                    <span className="text-xs text-[var(--color-text-muted)]">{check.evidence_ref}</span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-text)]" style={{ fontFamily: 'var(--font-display)' }}>
            Gate 6: Secure — Security Auditor
          </h1>
          <p className="text-sm text-[var(--color-text-muted)]">
            Continuous security and data protection compliance monitoring
          </p>
        </div>
        <Button>
          <Play className="w-4 h-4" />
          Run Security Audit
        </Button>
      </div>

      <AgentStatusCard agent={mockAgent} />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {mockFrameworkChecks.map((fw) => {
          const passed = fw.checks.filter((c) => c.status === 'pass').length;
          const total = fw.checks.length;
          const allPassed = passed === total;
          return (
            <Card key={fw.id}>
              <div className="flex items-center gap-2 mb-1">
                {allPassed ? (
                  <ShieldCheck className="w-4 h-4 text-[var(--color-success)]" />
                ) : (
                  <AlertTriangle className="w-4 h-4 text-[var(--color-warning)]" />
                )}
                <span className="text-sm font-medium text-[var(--color-text)]">{fw.name}</span>
              </div>
              <p className="text-lg font-bold text-[var(--color-text)]">{passed}/{total}</p>
              <p className="text-xs text-[var(--color-text-muted)]">controls passed</p>
            </Card>
          );
        })}
      </div>

      <Tabs
        tabs={mockFrameworkChecks.map((fw) => ({
          id: fw.id,
          label: fw.name,
          content: renderChecklist(fw),
        }))}
      />

      <Card
        header={
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-[var(--color-warning)]" />
            <h2 className="text-base font-semibold text-[var(--color-text)]">Remediation Recommendations</h2>
          </div>
        }
      >
        <div className="space-y-3">
          {remediation.map((item, idx) => (
            <div key={idx} className="p-3 border border-[var(--color-border)] rounded-lg">
              <div className="flex items-center gap-2 mb-1">
                <Badge variant={item.priority === 'High' ? 'error' : 'warning'}>{item.priority}</Badge>
                <span className="text-xs font-medium text-[var(--color-text-muted)]">{item.framework} - {item.check}</span>
              </div>
              <p className="text-sm font-medium text-[var(--color-text)]">{item.issue}</p>
              <p className="text-xs text-[var(--color-text-muted)] mt-1">{item.recommendation}</p>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
