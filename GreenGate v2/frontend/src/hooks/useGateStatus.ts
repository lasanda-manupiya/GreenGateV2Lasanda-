import { useQuery } from '@tanstack/react-query';
import { getGateStatus } from '../api/organisations';
import { useAuth } from '../auth/useAuth';
import type { GateStatus } from '../types';

export function useGateStatus() {
  const { user } = useAuth();

  return useQuery<GateStatus[]>({
    queryKey: ['gateStatus', user?.org_id],
    queryFn: () => getGateStatus(user!.org_id),
    enabled: !!user?.org_id,
    staleTime: 30000,
    placeholderData: [
      { gate: 1, name: 'Assess', agent: 'Carbon Auditor', status: 'complete', progress: 100, description: 'Build carbon inventory and baseline' },
      { gate: 2, name: 'Plan', agent: 'Strategy Builder', status: 'active', progress: 65, description: 'Create Carbon Reduction Plan' },
      { gate: 3, name: 'Implement', agent: 'Delivery Tracker', status: 'locked', progress: 0, description: 'Track reduction measures' },
      { gate: 4, name: 'Verify', agent: 'Compliance Checker', status: 'locked', progress: 0, description: 'Verify and validate data' },
      { gate: 5, name: 'Report', agent: 'Report Writer', status: 'locked', progress: 0, description: 'Generate framework reports' },
      { gate: 6, name: 'Secure', agent: 'Security Auditor', status: 'active', progress: 42, description: 'Continuous security compliance' },
    ],
  });
}
