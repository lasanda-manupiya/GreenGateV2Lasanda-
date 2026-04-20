import { useState } from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Progress } from '../../components/ui/Progress';
import { Download, Package, CheckCircle, Clock, Shield } from 'lucide-react';

interface EvidenceBundle {
  gate: number;
  gateName: string;
  items: { name: string; status: 'available' | 'pending' | 'missing'; type: string }[];
}

const evidenceBundles: EvidenceBundle[] = [
  {
    gate: 1,
    gateName: 'Assess',
    items: [
      { name: 'Carbon Inventory Spreadsheet', status: 'available', type: 'xlsx' },
      { name: 'Emission Factor Sources', status: 'available', type: 'pdf' },
      { name: 'Data Source Connection Logs', status: 'available', type: 'json' },
      { name: 'Baseline Methodology Document', status: 'available', type: 'pdf' },
      { name: 'Scope 3 Screening Results', status: 'pending', type: 'pdf' },
    ],
  },
  {
    gate: 2,
    gateName: 'Plan',
    items: [
      { name: 'Carbon Reduction Plan (CRP)', status: 'available', type: 'pdf' },
      { name: 'SBTi Target Calculations', status: 'available', type: 'xlsx' },
      { name: 'Framework Alignment Report', status: 'available', type: 'pdf' },
      { name: 'Board Sign-off Document', status: 'missing', type: 'pdf' },
    ],
  },
  {
    gate: 3,
    gateName: 'Implement',
    items: [
      { name: 'Reduction Measures Register', status: 'pending', type: 'xlsx' },
      { name: 'Project Implementation Plans', status: 'missing', type: 'pdf' },
      { name: 'Progress Tracking Reports', status: 'missing', type: 'pdf' },
    ],
  },
  {
    gate: 4,
    gateName: 'Verify',
    items: [
      { name: 'Data Quality Assessment', status: 'pending', type: 'pdf' },
      { name: 'Verification Statement', status: 'missing', type: 'pdf' },
      { name: 'Anomaly Detection Report', status: 'missing', type: 'pdf' },
    ],
  },
  {
    gate: 5,
    gateName: 'Report',
    items: [
      { name: 'PPN 06/21 Submission Pack', status: 'available', type: 'zip' },
      { name: 'CDP Questionnaire Draft', status: 'pending', type: 'pdf' },
      { name: 'Annual Sustainability Report', status: 'missing', type: 'pdf' },
    ],
  },
  {
    gate: 6,
    gateName: 'Secure',
    items: [
      { name: 'ISO 27001 Control Evidence', status: 'available', type: 'zip' },
      { name: 'GDPR Compliance Pack', status: 'available', type: 'zip' },
      { name: 'NHS DSPT Assessment', status: 'pending', type: 'pdf' },
      { name: 'Cyber Essentials Certificate', status: 'missing', type: 'pdf' },
    ],
  },
];

const frameworkCompleteness = [
  { framework: 'GHG Protocol', score: 88 },
  { framework: 'PPN 06/21', score: 75 },
  { framework: 'SBTi', score: 65 },
  { framework: 'ISO 27001', score: 82 },
  { framework: 'GDPR', score: 78 },
  { framework: 'CDP', score: 40 },
];

const statusConfig = {
  available: { variant: 'success' as const, icon: CheckCircle, label: 'Available' },
  pending: { variant: 'warning' as const, icon: Clock, label: 'Pending' },
  missing: { variant: 'error' as const, icon: Shield, label: 'Missing' },
};

export function EvidencePage() {
  const [generating, setGenerating] = useState(false);

  const handleGenerate = () => {
    setGenerating(true);
    setTimeout(() => setGenerating(false), 2000);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-text)]" style={{ fontFamily: 'var(--font-display)' }}>
            Evidence Pack
          </h1>
          <p className="text-sm text-[var(--color-text-muted)]">
            Manage and export governance evidence for audits and submissions
          </p>
        </div>
        <div className="flex gap-2">
          <Button onClick={handleGenerate} loading={generating}>
            <Package className="w-4 h-4" />
            Generate Evidence Pack
          </Button>
          <Button variant="secondary">
            <Download className="w-4 h-4" />
            Download All
          </Button>
        </div>
      </div>

      <Card
        header={
          <h2 className="text-base font-semibold text-[var(--color-text)]">
            Evidence Completeness by Framework
          </h2>
        }
      >
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {frameworkCompleteness.map((fw) => (
            <div key={fw.framework}>
              <Progress
                value={fw.score}
                label={fw.framework}
                size="sm"
                color={
                  fw.score >= 80
                    ? 'bg-[var(--color-success)]'
                    : fw.score >= 60
                    ? 'bg-[var(--color-warning)]'
                    : 'bg-[var(--color-error)]'
                }
              />
            </div>
          ))}
        </div>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {evidenceBundles.map((bundle) => {
          const available = bundle.items.filter((i) => i.status === 'available').length;
          const total = bundle.items.length;

          return (
            <Card key={bundle.gate}>
              <div className="flex items-center justify-between mb-4">
                <div>
                  <span className="text-xs font-bold uppercase text-[var(--color-primary)] bg-[var(--color-primary-light)] px-2 py-0.5 rounded">
                    Gate {bundle.gate}
                  </span>
                  <h3 className="text-base font-semibold text-[var(--color-text)] mt-1">
                    {bundle.gateName}
                  </h3>
                </div>
                <span className="text-sm font-medium text-[var(--color-text-muted)]">
                  {available}/{total}
                </span>
              </div>
              <div className="space-y-2">
                {bundle.items.map((item, idx) => {
                  const cfg = statusConfig[item.status];
                  const StatusIcon = cfg.icon;
                  return (
                    <div
                      key={idx}
                      className="flex items-center justify-between py-2 border-b border-[var(--color-border)] last:border-0"
                    >
                      <div className="flex items-center gap-2 min-w-0">
                        <StatusIcon className={`w-4 h-4 shrink-0 ${
                          item.status === 'available' ? 'text-[var(--color-success)]' :
                          item.status === 'pending' ? 'text-[var(--color-warning)]' :
                          'text-[var(--color-error)]'
                        }`} />
                        <span className="text-sm text-[var(--color-text)] truncate">
                          {item.name}
                        </span>
                      </div>
                      <div className="flex items-center gap-2 shrink-0 ml-2">
                        <span className="text-xs text-[var(--color-text-muted)] uppercase">
                          {item.type}
                        </span>
                        {item.status === 'available' && (
                          <button className="p-1 hover:bg-gray-100 rounded transition-colors">
                            <Download className="w-3.5 h-3.5 text-[var(--color-primary)]" />
                          </button>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
