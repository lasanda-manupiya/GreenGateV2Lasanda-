import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../auth/useAuth';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Select } from '../components/ui/Select';
import { Leaf } from 'lucide-react';

const sectors = [
  { value: 'healthcare', label: 'Healthcare' },
  { value: 'education', label: 'Education' },
  { value: 'finance', label: 'Finance' },
  { value: 'technology', label: 'Technology' },
  { value: 'manufacturing', label: 'Manufacturing' },
  { value: 'retail', label: 'Retail' },
  { value: 'energy', label: 'Energy' },
  { value: 'transport', label: 'Transport' },
  { value: 'construction', label: 'Construction' },
  { value: 'public_sector', label: 'Public Sector' },
  { value: 'other', label: 'Other' },
];

export function LoginPage() {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [orgName, setOrgName] = useState('');
  const [sector, setSector] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login, register } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || '/dashboard';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isRegister) {
        await register({ full_name: name, email, password, organisation_name: orgName, sector });
      } else {
        await login({ email, password });
      }
      navigate(from, { replace: true });
    } catch (err: unknown) {
      const message =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : undefined;
      setError(message || 'Authentication failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[var(--color-background)] flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-xl bg-[var(--color-primary)] mb-4">
            <Leaf className="w-7 h-7 text-white" />
          </div>
          <h1
            className="text-3xl font-bold text-[var(--color-text)] mb-2"
            style={{ fontFamily: 'var(--font-display)' }}
          >
            SustainGate
          </h1>
          <p className="text-[var(--color-text-muted)] text-sm">
            Governance built in, not bolted on.
          </p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-[var(--color-border)] p-8">
          <h2 className="text-xl font-semibold text-[var(--color-text)] mb-6">
            {isRegister ? 'Create your account' : 'Sign in to your account'}
          </h2>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {isRegister && (
              <>
                <Input
                  label="Full Name"
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Jane Smith"
                  required
                />
                <Input
                  label="Organisation Name"
                  type="text"
                  value={orgName}
                  onChange={(e) => setOrgName(e.target.value)}
                  placeholder="Acme Ltd"
                  required
                />
                <Select
                  label="Sector"
                  options={sectors}
                  value={sector}
                  onChange={(e) => setSector(e.target.value)}
                  placeholder="Select your sector"
                  required
                />
              </>
            )}
            <Input
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@company.com"
              required
            />
            <Input
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
            />
            <Button type="submit" loading={loading} className="w-full">
              {isRegister ? 'Create Account' : 'Sign In'}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <button
              onClick={() => {
                setIsRegister(!isRegister);
                setError('');
              }}
              className="text-sm text-[var(--color-primary)] hover:underline"
            >
              {isRegister
                ? 'Already have an account? Sign in'
                : "Don't have an account? Create one"}
            </button>
          </div>
        </div>

        <p className="text-center text-xs text-[var(--color-text-muted)] mt-6">
          Sustainable procurement &amp; carbon governance platform
        </p>
      </div>
    </div>
  );
}
