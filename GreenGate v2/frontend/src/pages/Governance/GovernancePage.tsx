import { useState } from 'react';
import { Card } from '../../components/ui/Card';
import { AuditLogTable } from '../../components/governance/AuditLogTable';
import { Select } from '../../components/ui/Select';
import { Input } from '../../components/ui/Input';
import { ShieldCheck, AlertTriangle, Activity } from 'lucide-react';
import type { AuditEntry } from '../../types';

const mockEntries: AuditEntry[] = [
  { id: '1', org_id: '1', gate: 1, actor_type: 'agent', actor_id: 'a1', actor_name: 'Carbon Auditor', action: 'Scanned 47 invoices from Xero', result: 'pass', details: 'Extracted emissions data from 47 purchase invoices for Q3 2025. 12 line items identified as emission-relevant.', created_at: new Date(Date.now() - 3600000).toISOString() },
  { id: '2', org_id: '1', gate: 2, actor_type: 'agent', actor_id: 'a2', actor_name: 'Strategy Builder', action: 'Generated CRP draft v3', result: 'pass', details: 'Carbon Reduction Plan aligned with PPN 06/21 requirements. 5/6 sections auto-populated.', created_at: new Date(Date.now() - 7200000).toISOString() },
  { id: '3', org_id: '1', gate: 1, actor_type: 'agent', actor_id: 'a1', actor_name: 'Carbon Auditor', action: 'Baseline calculation updated', result: 'warn', details: 'Scope 3 data has low confidence for categories: employee commuting, purchased goods, capital goods.', created_at: new Date(Date.now() - 14400000).toISOString() },
  { id: '4', org_id: '1', gate: 6, actor_type: 'agent', actor_id: 'a6', actor_name: 'Security Auditor', action: 'ISO 27001 controls check', result: 'fail', details: 'A.12.3.1 Information backup - evidence not found. Backup testing records missing from document repository.', created_at: new Date(Date.now() - 28800000).toISOString() },
  { id: '5', org_id: '1', gate: 4, actor_type: 'user', actor_id: 'u1', actor_name: 'Jane Smith', action: 'Approved Gate 1 submission', result: 'pass', details: 'Carbon inventory approved by board sponsor. Baseline year 2025 confirmed.', created_at: new Date(Date.now() - 43200000).toISOString() },
  { id: '6', org_id: '1', gate: 2, actor_type: 'user', actor_id: 'u2', actor_name: 'John Doe', action: 'Reviewed CRP targets', result: 'info', details: 'Near-term SBTi targets reviewed. Recommended increasing 2030 target from 40% to 42%.', created_at: new Date(Date.now() - 57600000).toISOString() },
  { id: '7', org_id: '1', gate: 6, actor_type: 'agent', actor_id: 'a6', actor_name: 'Security Auditor', action: 'GDPR compliance check', result: 'warn', details: 'ROPA incomplete for 2 processing activities. Art.30 requirement partially met.', created_at: new Date(Date.now() - 72000000).toISOString() },
  { id: '8', org_id: '1', gate: 1, actor_type: 'agent', actor_id: 'a1', actor_name: 'Carbon Auditor', action: 'Data source connection verified', result: 'pass', details: 'Xero API connection healthy. 234 transactions available for processing.', created_at: new Date(Date.now() - 86400000).toISOString() },
  { id: '9', org_id: '1', gate: 3, actor_type: 'agent', actor_id: 'a3', actor_name: 'Delivery Tracker', action: 'Reduction measure status update', result: 'info', details: 'EV fleet transition: 3/10 vehicles replaced. On track for Q2 target.', created_at: new Date(Date.now() - 100800000).toISOString() },
  { id: '10', org_id: '1', gate: 5, actor_type: 'agent', actor_id: 'a5', actor_name: 'Report Writer', action: 'CDP questionnaire draft started', result: 'info', details: 'Auto-populated 12/45 questions from existing data. Manual input required for remaining.', created_at: new Date(Date.now() - 115200000).toISOString() },
  { id: '11', org_id: '1', gate: 6, actor_type: 'agent', actor_id: 'a6', actor_name: 'Security Auditor', action: 'Cyber Essentials patch check', result: 'fail', details: '3 critical patches overdue: CVE-2026-1234, CVE-2026-1235, CVE-2026-1236. SLA breach.', created_at: new Date(Date.now() - 129600000).toISOString() },
  { id: '12', org_id: '1', gate: 1, actor_type: 'user', actor_id: 'u1', actor_name: 'Jane Smith', action: 'Manual emission entry added', result: 'pass', details: 'Added refrigerant loss data: 5kg R410A from office HVAC system.', created_at: new Date(Date.now() - 144000000).toISOString() },
];

export function GovernancePage() {
  const [gateFilter, setGateFilter] = useState('');
  const [actorFilter, setActorFilter] = useState('');
  const [resultFilter, setResultFilter] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');

  const filtered = mockEntries.filter((entry) => {
    if (gateFilter && entry.gate !== parseInt(gateFilter)) return false;
    if (actorFilter && entry.actor_type !== actorFilter) return false;
    if (resultFilter && entry.result !== resultFilter) return false;
    if (dateFrom && new Date(entry.created_at) < new Date(dateFrom)) return false;
    if (dateTo && new Date(entry.created_at) > new Date(dateTo + 'T23:59:59')) return false;
    return true;
  });

  const totalActions = mockEntries.length;
  const passRate = Math.round((mockEntries.filter((e) => e.result === 'pass').length / totalActions) * 100);
  const violations = mockEntries.filter((e) => e.result === 'fail').length;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-[var(--color-text)]" style={{ fontFamily: 'var(--font-display)' }}>
          Governance Log
        </h1>
        <p className="text-sm text-[var(--color-text-muted)]">
          Complete audit trail of all governance actions across gates
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center">
              <Activity className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-[var(--color-text)]" style={{ fontFamily: 'var(--font-display)' }}>{totalActions}</p>
              <p className="text-xs text-[var(--color-text-muted)]">Total Actions</p>
            </div>
          </div>
        </Card>
        <Card>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-emerald-50 flex items-center justify-center">
              <ShieldCheck className="w-5 h-5 text-emerald-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-[var(--color-text)]" style={{ fontFamily: 'var(--font-display)' }}>{passRate}%</p>
              <p className="text-xs text-[var(--color-text-muted)]">Pass Rate</p>
            </div>
          </div>
        </Card>
        <Card>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-red-50 flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-[var(--color-text)]" style={{ fontFamily: 'var(--font-display)' }}>{violations}</p>
              <p className="text-xs text-[var(--color-text-muted)]">Violations</p>
            </div>
          </div>
        </Card>
      </div>

      <Card>
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 mb-4">
          <Input
            label="Date From"
            type="date"
            value={dateFrom}
            onChange={(e) => setDateFrom(e.target.value)}
          />
          <Input
            label="Date To"
            type="date"
            value={dateTo}
            onChange={(e) => setDateTo(e.target.value)}
          />
          <Select
            label="Gate"
            options={[
              { value: '', label: 'All Gates' },
              { value: '1', label: 'Gate 1' },
              { value: '2', label: 'Gate 2' },
              { value: '3', label: 'Gate 3' },
              { value: '4', label: 'Gate 4' },
              { value: '5', label: 'Gate 5' },
              { value: '6', label: 'Gate 6' },
            ]}
            value={gateFilter}
            onChange={(e) => setGateFilter(e.target.value)}
          />
          <Select
            label="Actor Type"
            options={[
              { value: '', label: 'All Actors' },
              { value: 'user', label: 'User' },
              { value: 'agent', label: 'Agent' },
            ]}
            value={actorFilter}
            onChange={(e) => setActorFilter(e.target.value)}
          />
          <Select
            label="Result"
            options={[
              { value: '', label: 'All Results' },
              { value: 'pass', label: 'Pass' },
              { value: 'fail', label: 'Fail' },
              { value: 'warn', label: 'Warn' },
              { value: 'info', label: 'Info' },
            ]}
            value={resultFilter}
            onChange={(e) => setResultFilter(e.target.value)}
          />
        </div>
        <AuditLogTable entries={filtered} />
      </Card>
    </div>
  );
}
