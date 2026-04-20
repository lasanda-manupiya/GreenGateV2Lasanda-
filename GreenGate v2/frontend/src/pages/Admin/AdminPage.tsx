import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../../auth/useAuth';
import { getPlatformStats, getOrgUsers } from '../../api/platform';
import { Card } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { Spinner } from '../../components/ui/Spinner';
import { Building2, Users, UserCheck, ChevronDown, ChevronRight, ShieldCheck } from 'lucide-react';
import type { User } from '../../types';

const ROLE_VARIANT: Record<string, 'success' | 'warning' | 'error' | 'neutral'> = {
  superadmin: 'error',
  admin: 'warning',
  editor: 'success',
  viewer: 'neutral',
};

const ROLE_LABEL: Record<string, string> = {
  superadmin: 'Super Admin',
  admin: 'Admin',
  editor: 'Editor',
  viewer: 'Viewer',
};

export function AdminPage() {
  const { user } = useAuth();
  const [expandedOrg, setExpandedOrg] = useState<string | null>(null);
  const [orgUsers, setOrgUsers] = useState<Record<string, User[]>>({});
  const [loadingOrg, setLoadingOrg] = useState<string | null>(null);

  const { data: stats, isLoading } = useQuery({
    queryKey: ['platform-stats'],
    queryFn: getPlatformStats,
    enabled: user?.role === 'superadmin',
  });

  if (user?.role !== 'superadmin') {
    return (
      <div className="text-center py-12">
        <ShieldCheck className="w-12 h-12 text-red-300 mx-auto mb-4" />
        <h2 className="text-lg font-semibold text-[var(--color-text)]">Access Denied</h2>
        <p className="text-sm text-[var(--color-text-muted)]">Only the platform super admin can access this page.</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  const handleToggleOrg = async (orgId: string) => {
    if (expandedOrg === orgId) {
      setExpandedOrg(null);
      return;
    }
    setExpandedOrg(orgId);
    if (!orgUsers[orgId]) {
      setLoadingOrg(orgId);
      try {
        const users = await getOrgUsers(orgId);
        setOrgUsers((prev) => ({ ...prev, [orgId]: users }));
      } catch {
        // ignore
      } finally {
        setLoadingOrg(null);
      }
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-[var(--color-text)]" style={{ fontFamily: 'var(--font-display)' }}>
          Platform Administration
        </h1>
        <p className="text-sm text-[var(--color-text-muted)]">
          Manage all companies and users on the SustainGate platform
        </p>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-[var(--color-primary)]/10 flex items-center justify-center">
              <Building2 className="w-5 h-5 text-[var(--color-primary)]" />
            </div>
            <div>
              <p className="text-2xl font-bold text-[var(--color-text)]">{stats?.total_organisations || 0}</p>
              <p className="text-xs text-[var(--color-text-muted)]">Companies</p>
            </div>
          </div>
        </Card>
        <Card>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center">
              <Users className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-[var(--color-text)]">{stats?.total_users || 0}</p>
              <p className="text-xs text-[var(--color-text-muted)]">Total Users</p>
            </div>
          </div>
        </Card>
        <Card>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-green-50 flex items-center justify-center">
              <UserCheck className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-[var(--color-text)]">{stats?.active_users || 0}</p>
              <p className="text-xs text-[var(--color-text-muted)]">Active Users</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Companies list */}
      <Card
        header={
          <div className="flex items-center gap-2">
            <Building2 className="w-4 h-4 text-[var(--color-primary)]" />
            <h2 className="text-base font-semibold text-[var(--color-text)]">
              All Companies ({stats?.total_organisations || 0})
            </h2>
          </div>
        }
      >
        <div className="divide-y divide-[var(--color-border)]">
          {stats?.organisations.map((org) => (
            <div key={org.id}>
              {/* Org row */}
              <button
                onClick={() => handleToggleOrg(org.id)}
                className="w-full flex items-center justify-between py-4 first:pt-0 hover:bg-gray-50 -mx-4 px-4 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-[var(--color-primary)]/10 flex items-center justify-center">
                    <span className="text-sm font-bold text-[var(--color-primary)]">
                      {org.name.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <div className="text-left">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-[var(--color-text)]">{org.name}</span>
                      {org.sector && (
                        <Badge variant="neutral">{org.sector}</Badge>
                      )}
                    </div>
                    <div className="flex items-center gap-3 text-xs text-[var(--color-text-muted)]">
                      <span>{org.user_count} users</span>
                      <span>Gate {org.current_gate}</span>
                      {org.admin_email && <span>Admin: {org.admin_email}</span>}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={org.onboarding_complete ? 'success' : 'warning'}>
                    {org.onboarding_complete ? 'Active' : 'Onboarding'}
                  </Badge>
                  {expandedOrg === org.id ? (
                    <ChevronDown className="w-4 h-4 text-[var(--color-text-muted)]" />
                  ) : (
                    <ChevronRight className="w-4 h-4 text-[var(--color-text-muted)]" />
                  )}
                </div>
              </button>

              {/* Expanded users */}
              {expandedOrg === org.id && (
                <div className="pb-4 pl-14">
                  {loadingOrg === org.id ? (
                    <div className="py-2"><Spinner size="sm" /></div>
                  ) : orgUsers[org.id]?.length ? (
                    <div className="space-y-2">
                      {orgUsers[org.id].map((u) => (
                        <div key={u.id} className="flex items-center justify-between py-2 px-3 bg-gray-50 rounded-lg">
                          <div className="flex items-center gap-2">
                            <div className="w-7 h-7 rounded-full bg-[var(--color-primary)]/10 flex items-center justify-center">
                              <span className="text-xs font-semibold text-[var(--color-primary)]">
                                {u.full_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)}
                              </span>
                            </div>
                            <div>
                              <span className="text-sm text-[var(--color-text)]">{u.full_name}</span>
                              <span className="text-xs text-[var(--color-text-muted)] ml-2">{u.email}</span>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <Badge variant={ROLE_VARIANT[u.role] || 'neutral'}>
                              {ROLE_LABEL[u.role] || u.role}
                            </Badge>
                            {!u.is_active && <Badge variant="error">Inactive</Badge>}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-xs text-[var(--color-text-muted)] py-2">No users found</p>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
