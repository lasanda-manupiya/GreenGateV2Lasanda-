import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { Select } from '../../components/ui/Select';
import { Card } from '../../components/ui/Card';
import { Progress } from '../../components/ui/Progress';
import { Check, Link2, Users, Eye, Building2 } from 'lucide-react';

const steps = [
  { id: 1, label: 'Organisation', icon: Building2 },
  { id: 2, label: 'Frameworks', icon: Check },
  { id: 3, label: 'Data Sources', icon: Link2 },
  { id: 4, label: 'Team', icon: Users },
  { id: 5, label: 'Review', icon: Eye },
];

const sectorOptions = [
  { value: 'healthcare', label: 'Healthcare' },
  { value: 'education', label: 'Education' },
  { value: 'finance', label: 'Finance' },
  { value: 'technology', label: 'Technology' },
  { value: 'manufacturing', label: 'Manufacturing' },
  { value: 'public_sector', label: 'Public Sector' },
  { value: 'other', label: 'Other' },
];

const sizeOptions = [
  { value: 'micro', label: 'Micro (1-9 employees)' },
  { value: 'small', label: 'Small (10-49)' },
  { value: 'medium', label: 'Medium (50-249)' },
  { value: 'large', label: 'Large (250+)' },
];

const countryOptions = [
  { value: 'GB', label: 'United Kingdom' },
  { value: 'US', label: 'United States' },
  { value: 'DE', label: 'Germany' },
  { value: 'FR', label: 'France' },
  { value: 'AU', label: 'Australia' },
  { value: 'CA', label: 'Canada' },
];

const frameworks = [
  { id: 'ghg', name: 'GHG Protocol', description: 'Corporate standard for greenhouse gas accounting' },
  { id: 'ppn006', name: 'PPN 06/21', description: 'UK Government procurement policy note on carbon reduction' },
  { id: 'sbti', name: 'SBTi', description: 'Science Based Targets initiative' },
  { id: 'nhs_evergreen', name: 'NHS Evergreen', description: 'NHS sustainable supplier assessment' },
  { id: 'uk_srs', name: 'UK SRS', description: 'UK Sustainability Reporting Standards' },
  { id: 'cdp', name: 'CDP', description: 'Carbon Disclosure Project' },
];

const dataSources = [
  { id: 'xero', name: 'Xero', description: 'Cloud accounting platform', icon: '📊' },
  { id: 'sage', name: 'Sage', description: 'Business accounting software', icon: '📈' },
  { id: 'quickbooks', name: 'QuickBooks', description: 'Financial management tool', icon: '💹' },
];

export function OnboardingWizard() {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [orgProfile, setOrgProfile] = useState({ sector: '', size: '', country: '' });
  const [selectedFrameworks, setSelectedFrameworks] = useState<string[]>([]);
  const [connectedSources, setConnectedSources] = useState<string[]>([]);
  const [teamAdmin, setTeamAdmin] = useState('');
  const [directorName, setDirectorName] = useState('');
  const [sponsorName, setSponsorName] = useState('');

  const toggleFramework = (id: string) => {
    setSelectedFrameworks((prev) =>
      prev.includes(id) ? prev.filter((f) => f !== id) : [...prev, id]
    );
  };

  const toggleSource = (id: string) => {
    setConnectedSources((prev) =>
      prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id]
    );
  };

  const canProceed = () => {
    switch (currentStep) {
      case 1:
        return orgProfile.sector && orgProfile.size && orgProfile.country;
      case 2:
        return selectedFrameworks.length > 0;
      case 3:
        return true;
      case 4:
        return true;
      case 5:
        return true;
      default:
        return false;
    }
  };

  const handleComplete = () => {
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen bg-[var(--color-background)] py-8 px-4">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-8">
          <h1
            className="text-2xl font-bold text-[var(--color-text)]"
            style={{ fontFamily: 'var(--font-display)' }}
          >
            Set up your organisation
          </h1>
          <p className="text-sm text-[var(--color-text-muted)] mt-1">
            Complete these steps to configure SustainGate for your needs
          </p>
        </div>

        <div className="flex items-center justify-between mb-8 px-4">
          {steps.map((step, idx) => {
            const StepIcon = step.icon;
            const isComplete = currentStep > step.id;
            const isActive = currentStep === step.id;
            return (
              <div key={step.id} className="flex items-center flex-1">
                <div className="flex flex-col items-center">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium border-2 transition-colors ${
                      isComplete
                        ? 'bg-[var(--color-primary)] border-[var(--color-primary)] text-white'
                        : isActive
                        ? 'border-[var(--color-primary)] text-[var(--color-primary)] bg-white'
                        : 'border-gray-300 text-gray-400 bg-white'
                    }`}
                  >
                    {isComplete ? <Check className="w-4 h-4" /> : <StepIcon className="w-4 h-4" />}
                  </div>
                  <span
                    className={`text-xs mt-1 ${
                      isActive ? 'text-[var(--color-primary)] font-medium' : 'text-[var(--color-text-muted)]'
                    }`}
                  >
                    {step.label}
                  </span>
                </div>
                {idx < steps.length - 1 && (
                  <div
                    className={`flex-1 h-0.5 mx-2 mt-[-16px] ${
                      currentStep > step.id ? 'bg-[var(--color-primary)]' : 'bg-gray-200'
                    }`}
                  />
                )}
              </div>
            );
          })}
        </div>

        <Progress value={currentStep} max={5} showPercentage={false} className="mb-6" />

        <Card className="mb-6">
          {currentStep === 1 && (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-[var(--color-text)]">
                Organisation Profile
              </h2>
              <p className="text-sm text-[var(--color-text-muted)]">
                Tell us about your organisation so we can tailor the platform.
              </p>
              <Select
                label="Sector"
                options={sectorOptions}
                value={orgProfile.sector}
                onChange={(e) => setOrgProfile({ ...orgProfile, sector: e.target.value })}
                placeholder="Select sector"
              />
              <Select
                label="Organisation Size"
                options={sizeOptions}
                value={orgProfile.size}
                onChange={(e) => setOrgProfile({ ...orgProfile, size: e.target.value })}
                placeholder="Select size"
              />
              <Select
                label="Country"
                options={countryOptions}
                value={orgProfile.country}
                onChange={(e) => setOrgProfile({ ...orgProfile, country: e.target.value })}
                placeholder="Select country"
              />
            </div>
          )}

          {currentStep === 2 && (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-[var(--color-text)]">
                Select Frameworks
              </h2>
              <p className="text-sm text-[var(--color-text-muted)]">
                Choose the sustainability frameworks relevant to your organisation.
              </p>
              <div className="grid gap-3">
                {frameworks.map((fw) => (
                  <label
                    key={fw.id}
                    className={`flex items-start gap-3 p-4 border rounded-lg cursor-pointer transition-colors ${
                      selectedFrameworks.includes(fw.id)
                        ? 'border-[var(--color-primary)] bg-[var(--color-primary-light)]'
                        : 'border-[var(--color-border)] hover:border-gray-300'
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={selectedFrameworks.includes(fw.id)}
                      onChange={() => toggleFramework(fw.id)}
                      className="mt-0.5 w-4 h-4 rounded border-gray-300 text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
                    />
                    <div>
                      <span className="text-sm font-medium text-[var(--color-text)]">
                        {fw.name}
                      </span>
                      <p className="text-xs text-[var(--color-text-muted)]">{fw.description}</p>
                    </div>
                  </label>
                ))}
              </div>
            </div>
          )}

          {currentStep === 3 && (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-[var(--color-text)]">
                Connect Data Sources
              </h2>
              <p className="text-sm text-[var(--color-text-muted)]">
                Connect your accounting platforms to automatically import financial data for
                carbon calculations.
              </p>
              <div className="grid gap-3 sm:grid-cols-3">
                {dataSources.map((src) => (
                  <div
                    key={src.id}
                    className={`p-4 border rounded-lg text-center transition-colors ${
                      connectedSources.includes(src.id)
                        ? 'border-[var(--color-primary)] bg-[var(--color-primary-light)]'
                        : 'border-[var(--color-border)]'
                    }`}
                  >
                    <div className="text-3xl mb-2">{src.icon}</div>
                    <h3 className="text-sm font-medium text-[var(--color-text)]">{src.name}</h3>
                    <p className="text-xs text-[var(--color-text-muted)] mb-3">
                      {src.description}
                    </p>
                    <Button
                      size="sm"
                      variant={connectedSources.includes(src.id) ? 'secondary' : 'primary'}
                      onClick={() => toggleSource(src.id)}
                      className="w-full"
                    >
                      {connectedSources.includes(src.id) ? 'Connected' : 'Connect'}
                    </Button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {currentStep === 4 && (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-[var(--color-text)]">Team Setup</h2>
              <p className="text-sm text-[var(--color-text-muted)]">
                Invite team members and assign governance roles.
              </p>
              <Input
                label="Invite Admin (email)"
                type="email"
                value={teamAdmin}
                onChange={(e) => setTeamAdmin(e.target.value)}
                placeholder="admin@company.com"
              />
              <Input
                label="Named Director / Board Sponsor"
                type="text"
                value={directorName}
                onChange={(e) => setDirectorName(e.target.value)}
                placeholder="Dr. Jane Smith"
              />
              <Input
                label="Carbon Reduction Sponsor"
                type="text"
                value={sponsorName}
                onChange={(e) => setSponsorName(e.target.value)}
                placeholder="John Doe, Head of Sustainability"
              />
            </div>
          )}

          {currentStep === 5 && (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-[var(--color-text)]">
                Review Your Setup
              </h2>
              <p className="text-sm text-[var(--color-text-muted)]">
                Check your selections before completing setup.
              </p>
              <div className="space-y-4">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <h3 className="text-sm font-medium text-[var(--color-text)] mb-2">
                    Organisation
                  </h3>
                  <p className="text-sm text-[var(--color-text-muted)]">
                    Sector: {orgProfile.sector || 'Not set'} | Size:{' '}
                    {orgProfile.size || 'Not set'} | Country: {orgProfile.country || 'Not set'}
                  </p>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <h3 className="text-sm font-medium text-[var(--color-text)] mb-2">
                    Frameworks
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedFrameworks.length > 0 ? (
                      selectedFrameworks.map((id) => (
                        <span
                          key={id}
                          className="text-xs bg-[var(--color-primary-light)] text-[var(--color-primary)] px-2 py-1 rounded"
                        >
                          {frameworks.find((f) => f.id === id)?.name}
                        </span>
                      ))
                    ) : (
                      <span className="text-sm text-[var(--color-text-muted)]">None selected</span>
                    )}
                  </div>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <h3 className="text-sm font-medium text-[var(--color-text)] mb-2">
                    Data Sources
                  </h3>
                  <p className="text-sm text-[var(--color-text-muted)]">
                    {connectedSources.length > 0
                      ? connectedSources
                          .map((id) => dataSources.find((s) => s.id === id)?.name)
                          .join(', ')
                      : 'None connected'}
                  </p>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <h3 className="text-sm font-medium text-[var(--color-text)] mb-2">Team</h3>
                  <p className="text-sm text-[var(--color-text-muted)]">
                    Admin: {teamAdmin || 'Not set'} | Director: {directorName || 'Not set'} |
                    Sponsor: {sponsorName || 'Not set'}
                  </p>
                </div>
              </div>
            </div>
          )}
        </Card>

        <div className="flex items-center justify-between">
          <Button
            variant="secondary"
            onClick={() => setCurrentStep(currentStep - 1)}
            disabled={currentStep === 1}
          >
            Back
          </Button>
          {currentStep < 5 ? (
            <Button onClick={() => setCurrentStep(currentStep + 1)} disabled={!canProceed()}>
              Next
            </Button>
          ) : (
            <Button onClick={handleComplete}>Complete Setup</Button>
          )}
        </div>
      </div>
    </div>
  );
}
