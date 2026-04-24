import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { useAuth } from '../../auth/useAuth';
import { generateCrp, type GenerateCrpResponse } from '../../api/crp';
import { Card } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { Tabs } from '../../components/ui/Tabs';
import { Input } from '../../components/ui/Input';
import { AgentStatusCard } from '../../components/agents/AgentStatusCard';
import { TrajectoryChart } from '../../components/charts/TrajectoryChart';
import { FileText, Download, CheckCircle, Circle, Star } from 'lucide-react';
import type { Agent, CrpDocument, TrajectoryPoint } from '../../types';

const mockAgent: Agent = {
  id: 'a2',
  name: 'Strategy Builder',
  gate: 2,
  description: 'Generates Carbon Reduction Plans and aligns with frameworks',
  status: 'idle',
  last_active: new Date(Date.now() - 7200000).toISOString(),
  policy_profile: { framework_priority: 'PPN 06/21', auto_align: true },
  actions: ['generate_crp', 'recommend_frameworks', 'calculate_sbti'],
};

const mockCrp: CrpDocument = {
  id: 'crp-1',
  org_id: '1',
  version: 3,
  status: 'draft',
  sections: [
    { title: 'Commitment Statement', content: 'Our organisation is committed to achieving Net Zero greenhouse gas emissions by 2050, with an interim target of 50% reduction by 2030 against our 2025 baseline.', aligned: true },
    { title: 'Baseline Emissions (FY 2025)', content: 'Scope 1: 40.58 tCO2e | Scope 2: 74.64 tCO2e | Scope 3: 225.36 tCO2e | Total: 340.58 tCO2e. Baseline established using operational control approach per GHG Protocol.', aligned: true },
    { title: 'Emission Reduction Targets', content: 'Near-term: 42% absolute reduction in Scope 1 and 2 by 2030. Long-term: 90% reduction across all scopes by 2050. Targets aligned with SBTi 1.5C pathway.', aligned: true },
    { title: 'Carbon Reduction Measures', content: '1. Transition fleet to EVs (est. -15 tCO2e/yr)\n2. Switch to 100% renewable electricity (est. -66 tCO2e/yr)\n3. Implement remote working policy (est. -30 tCO2e/yr)\n4. Sustainable procurement policy (est. -20 tCO2e/yr)', aligned: true },
    { title: 'Governance & Sign-off', content: 'Carbon reduction plan approved by the Board of Directors. Named director: Dr. Sarah Chen, Chief Sustainability Officer. Annual review cycle with quarterly progress reporting.', aligned: false },
  ],
  ppn006_alignment: {
    'commitment': true,
    'baseline': true,
    'targets': true,
    'measures': true,
    'governance': false,
    'reporting': true,
  },
  created_at: new Date().toISOString(),
};

const mockTrajectory: TrajectoryPoint[] = [
  { year: 2025, target_emissions: 340, actual_emissions: 340, reduction_pct: 0 },
  { year: 2026, target_emissions: 310, actual_emissions: null, reduction_pct: 8.8 },
  { year: 2027, target_emissions: 282, actual_emissions: null, reduction_pct: 17 },
  { year: 2028, target_emissions: 256, actual_emissions: null, reduction_pct: 24.7 },
  { year: 2029, target_emissions: 233, actual_emissions: null, reduction_pct: 31.5 },
  { year: 2030, target_emissions: 197, actual_emissions: null, reduction_pct: 42 },
  { year: 2035, target_emissions: 119, actual_emissions: null, reduction_pct: 65 },
  { year: 2040, target_emissions: 68, actual_emissions: null, reduction_pct: 80 },
  { year: 2045, target_emissions: 34, actual_emissions: null, reduction_pct: 90 },
  { year: 2050, target_emissions: 0, actual_emissions: null, reduction_pct: 100 },
];

const frameworkRecommendations = [
  { id: 'ppn006', name: 'PPN 06/21', relevance: 95, description: 'Mandatory for UK government procurement. Your CRP directly supports this requirement.', category: 'Mandatory' },
  { id: 'ghg', name: 'GHG Protocol', relevance: 90, description: 'Foundation for all carbon accounting. Already aligned through Gate 1 inventory.', category: 'Best Practice' },
  { id: 'sbti', name: 'SBTi', relevance: 85, description: 'Science-based targets enhance credibility. Near-term targets calculated for 1.5C pathway.', category: 'Recommended' },
  { id: 'cdp', name: 'CDP', relevance: 70, description: 'Annual disclosure enhances transparency with investors and customers.', category: 'Recommended' },
  { id: 'uk_srs', name: 'UK SRS', relevance: 60, description: 'UK Sustainability Reporting Standards becoming mandatory for large organisations.', category: 'Upcoming' },
];

type GenerateCrpResponse = Awaited<ReturnType<typeof generateCrp>>;

export function Gate2Page() {
  const { user } = useAuth();
  const [baseYear, setBaseYear] = useState('2025');
  const [baseEmissions, setBaseEmissions] = useState('340');
  const [targetYear, setTargetYear] = useState('2030');

  const crpMutation = useMutation<GenerateCrpResponse, Error>({
    mutationFn: () => generateCrp(user!.org_id),
  });

  const crp = mockCrp;
  const trajectory = mockTrajectory;
  const generatedCrp = crpMutation.data?.crp;

  const handleDownloadCrpJson = () => {
    const payload = generatedCrp ?? crp;
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `crp-${user?.org_id ?? 'draft'}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const targetReduction = 42;
  const annualReduction = (targetReduction / (parseInt(targetYear) - parseInt(baseYear))).toFixed(1);
  const targetEmissions = (parseFloat(baseEmissions) * (1 - targetReduction / 100)).toFixed(1);

  const crpBuilder = (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-base font-semibold text-[var(--color-text)]">
            Carbon Reduction Plan v{crp.version}
          </h3>
          <p className="text-xs text-[var(--color-text-muted)]">
            Status: <Badge variant={crp.status === 'final' ? 'success' : 'warning'}>{crp.status}</Badge>
          </p>
        </div>
        <div className="flex gap-2">
          <Button size="sm" onClick={() => crpMutation.mutate()} loading={crpMutation.isPending}>
            <FileText className="w-4 h-4" />
            Generate CRP
          </Button>
          <Button size="sm" variant="secondary" onClick={handleDownloadCrpJson}>
            <Download className="w-4 h-4" />
            Download CRP JSON
          </Button>
        </div>
      </div>

      {generatedCrp && (
        <Card header={<h3 className="text-sm font-semibold text-[var(--color-text)]">Generated CRP (Live API Output)</h3>}>
          <pre className="text-xs whitespace-pre-wrap break-words text-[var(--color-text-muted)]">
            {JSON.stringify(generatedCrp, null, 2)}
          </pre>
        </Card>
      )}

      <div className="space-y-4">
        {crp.sections.map((section, idx) => (
          <div key={idx} className="p-4 border border-[var(--color-border)] rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              {section.aligned ? (
                <CheckCircle className="w-4 h-4 text-[var(--color-success)]" />
              ) : (
                <Circle className="w-4 h-4 text-[var(--color-text-muted)]" />
              )}
              <h4 className="text-sm font-semibold text-[var(--color-text)]">{section.title}</h4>
            </div>
            <p className="text-sm text-[var(--color-text-muted)] whitespace-pre-line">{section.content}</p>
          </div>
        ))}
      </div>

      <Card header={<h3 className="text-sm font-semibold text-[var(--color-text)]">PPN 06/21 Alignment Checklist</h3>}>
        <div className="space-y-2">
          {Object.entries(crp.ppn006_alignment).map(([key, aligned]) => (
            <div key={key} className="flex items-center gap-2">
              {aligned ? (
                <CheckCircle className="w-4 h-4 text-[var(--color-success)]" />
              ) : (
                <Circle className="w-4 h-4 text-[var(--color-warning)]" />
              )}
              <span className="text-sm text-[var(--color-text)] capitalize">{key}</span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );

  const frameworkRecs = (
    <div className="grid gap-4 sm:grid-cols-2">
      {frameworkRecommendations.map((fw) => (
        <Card key={fw.id} hover>
          <div className="flex items-start justify-between mb-2">
            <div>
              <h3 className="text-sm font-semibold text-[var(--color-text)]">{fw.name}</h3>
              <Badge variant={fw.category === 'Mandatory' ? 'error' : fw.category === 'Recommended' ? 'warning' : 'info'}>
                {fw.category}
              </Badge>
            </div>
            <div className="flex items-center gap-1">
              <Star className="w-4 h-4 text-[var(--color-secondary)]" />
              <span className="text-sm font-bold text-[var(--color-text)]">{fw.relevance}%</span>
            </div>
          </div>
          <p className="text-xs text-[var(--color-text-muted)]">{fw.description}</p>
        </Card>
      ))}
    </div>
  );

  const sbtiCalc = (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Input label="Base Year" type="number" value={baseYear} onChange={(e) => setBaseYear(e.target.value)} />
        <Input label="Base Emissions (tCO2e)" type="number" value={baseEmissions} onChange={(e) => setBaseEmissions(e.target.value)} />
        <Input label="Target Year" type="number" value={targetYear} onChange={(e) => setTargetYear(e.target.value)} />
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card>
          <p className="text-xs text-[var(--color-text-muted)]">Required Annual Reduction</p>
          <p className="text-xl font-bold text-[var(--color-text)]" style={{ fontFamily: 'var(--font-display)' }}>{annualReduction}%</p>
          <p className="text-xs text-[var(--color-text-muted)]">per year (linear)</p>
        </Card>
        <Card>
          <p className="text-xs text-[var(--color-text-muted)]">Target Year Emissions</p>
          <p className="text-xl font-bold text-[var(--color-text)]" style={{ fontFamily: 'var(--font-display)' }}>{targetEmissions} tCO2e</p>
          <p className="text-xs text-[var(--color-text-muted)]">by {targetYear}</p>
        </Card>
        <Card>
          <p className="text-xs text-[var(--color-text-muted)]">Total Reduction</p>
          <p className="text-xl font-bold text-[var(--color-primary)]" style={{ fontFamily: 'var(--font-display)' }}>{targetReduction}%</p>
          <p className="text-xs text-[var(--color-text-muted)]">SBTi 1.5C aligned</p>
        </Card>
      </div>
      <Card header={<h3 className="text-sm font-semibold text-[var(--color-text)]">Emissions Trajectory</h3>}>
        <TrajectoryChart data={trajectory} />
      </Card>
    </div>
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-[var(--color-text)]" style={{ fontFamily: 'var(--font-display)' }}>
          Gate 2: Plan — Strategy Builder
        </h1>
        <p className="text-sm text-[var(--color-text-muted)]">
          Create your Carbon Reduction Plan and align with regulatory frameworks
        </p>
      </div>

      <AgentStatusCard agent={mockAgent} />

      <Tabs
        tabs={[
          { id: 'crp', label: 'CRP Builder', content: crpBuilder },
          { id: 'frameworks', label: 'Framework Recommendations', content: frameworkRecs },
          { id: 'sbti', label: 'SBTi Calculator', content: sbtiCalc },
        ]}
      />
    </div>
  );
}
