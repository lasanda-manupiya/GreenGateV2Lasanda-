import { useState, useCallback } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../../auth/useAuth';
import { listUsers, inviteUser, updateUserRole, toggleUserActive } from '../../api/users';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import { Modal } from '../../components/ui/Modal';
import { Spinner } from '../../components/ui/Spinner';
import { Users, UserPlus, Shield, ShieldCheck, Eye, Edit3, ChevronDown, CheckCircle, XCircle } from 'lucide-react';
import type { User } from '../../types';

const ROLE_INFO: Record<string, { label: string; variant: 'success' | 'warning' | 'error' | 'neutral'; description: string }> = {
  superadmin: { label: 'Super Admin', variant: 'error', description: 'Full platform access, can manage admins and all settings' },
  admin: { label: 'Admin', variant: 'warning', description: 'Can manage users, upload data, run agents, scan folders' },
  editor: { label: 'Editor', variant: 'success', description: 'Can upload CSV data, run agents, edit emissions entries' },
  viewer: { label: 'Viewer', variant: 'neutral', description: 'Read-only access to dashboard, reports, and data' },
};

export function TeamPage() {
  const { user: currentUser } = useAuth();
  const queryClient = useQueryClient();
  const [showInvite, setShowInvite] = useState(false);
  const [roleMenuOpen, setRoleMenuOpen] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Invite form state
  const [inviteName, setInviteName] = useState('');
  const [inviteEmail, setInviteEmail] = useState('');
  const [invitePassword, setInvitePassword] = useState('');
  const [inviteRole, setInviteRole] = useState('viewer');
  const [inviteLoading, setInviteLoading] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ['users'],
    queryFn: listUsers,
    enabled: !!currentUser,
  });

  const isSuperAdmin = currentUser?.role === 'superadmin';
  const isAdmin = currentUser?.role === 'admin' || isSuperAdmin;

  const handleInvite = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setInviteLoading(true);
    try {
      await inviteUser({
        full_name: inviteName,
        email: inviteEmail,
        password: invitePassword,
        role: inviteRole,
      });
      setSuccess(`${inviteName} has been invited as ${ROLE_INFO[inviteRole]?.label || inviteRole}`);
      setShowInvite(false);
      setInviteName('');
      setInviteEmail('');
      setInvitePassword('');
      setInviteRole('viewer');
      queryClient.invalidateQueries({ queryKey: ['users'] });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to invite user');
    } finally {
      setInviteLoading(false);
    }
  }, [inviteName, inviteEmail, invitePassword, inviteRole, queryClient]);

  const handleRoleChange = useCallback(async (userId: string, newRole: string) => {
    setRoleMenuOpen(null);
    setActionLoading(userId);
    setError(null);
    try {
      await updateUserRole(userId, newRole);
      setSuccess('Role updated successfully');
      queryClient.invalidateQueries({ queryKey: ['users'] });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update role');
    } finally {
      setActionLoading(null);
    }
  }, [queryClient]);

  const handleToggleActive = useCallback(async (userId: string, userName: string, isActive: boolean) => {
    setActionLoading(userId);
    setError(null);
    try {
      await toggleUserActive(userId);
      setSuccess(`${userName} has been ${isActive ? 'deactivated' : 'reactivated'}`);
      queryClient.invalidateQueries({ queryKey: ['users'] });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update user');
    } finally {
      setActionLoading(null);
    }
  }, [queryClient]);

  const users = data?.users || [];

  const availableRoles = isSuperAdmin
    ? ['viewer', 'editor', 'admin']
    : ['viewer', 'editor'];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-text)]" style={{ fontFamily: 'var(--font-display)' }}>
            Team Management
          </h1>
          <p className="text-sm text-[var(--color-text-muted)]">
            Manage your organisation's users and their access levels
          </p>
        </div>
        {isAdmin && (
          <Button onClick={() => setShowInvite(true)}>
            <UserPlus className="w-4 h-4" />
            Invite User
          </Button>
        )}
      </div>

      {/* Success message */}
      {success && (
        <div className="flex items-center gap-2 p-3 bg-green-50 border border-green-200 rounded-lg">
          <CheckCircle className="w-4 h-4 text-green-600 shrink-0" />
          <p className="text-sm text-green-800">{success}</p>
          <button onClick={() => setSuccess(null)} className="ml-auto text-green-600 hover:text-green-800 text-xs">dismiss</button>
        </div>
      )}

      {/* Error message */}
      {error && (
        <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg">
          <XCircle className="w-4 h-4 text-red-500 shrink-0" />
          <p className="text-sm text-red-700">{error}</p>
          <button onClick={() => setError(null)} className="ml-auto text-red-600 hover:text-red-800 text-xs">dismiss</button>
        </div>
      )}

      {/* Role Legend */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {Object.entries(ROLE_INFO).map(([role, info]) => (
          <div key={role} className="p-3 bg-white border border-[var(--color-border)] rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              {role === 'superadmin' ? <ShieldCheck className="w-4 h-4 text-red-500" /> :
               role === 'admin' ? <Shield className="w-4 h-4 text-amber-500" /> :
               role === 'editor' ? <Edit3 className="w-4 h-4 text-green-600" /> :
               <Eye className="w-4 h-4 text-gray-500" />}
              <Badge variant={info.variant}>{info.label}</Badge>
            </div>
            <p className="text-xs text-[var(--color-text-muted)]">{info.description}</p>
          </div>
        ))}
      </div>

      {/* User List */}
      <Card
        header={
          <div className="flex items-center gap-2">
            <Users className="w-4 h-4 text-[var(--color-primary)]" />
            <h2 className="text-base font-semibold text-[var(--color-text)]">
              Team Members ({data?.total || 0})
            </h2>
          </div>
        }
      >
        <div className="divide-y divide-[var(--color-border)]">
          {users.map((u: User) => {
            const roleInfo = ROLE_INFO[u.role] || ROLE_INFO.viewer;
            const isCurrentUser = u.id === currentUser?.id;
            const canModify = isAdmin && !isCurrentUser && u.role !== 'superadmin';

            return (
              <div key={u.id} className="flex items-center justify-between py-4 first:pt-0 last:pb-0">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-[var(--color-primary)]/10 flex items-center justify-center">
                    <span className="text-sm font-semibold text-[var(--color-primary)]">
                      {u.full_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)}
                    </span>
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-[var(--color-text)]">{u.full_name}</span>
                      {isCurrentUser && (
                        <span className="text-xs text-[var(--color-text-muted)]">(you)</span>
                      )}
                      {!u.is_active && (
                        <Badge variant="error">Deactivated</Badge>
                      )}
                    </div>
                    <span className="text-xs text-[var(--color-text-muted)]">{u.email}</span>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  {/* Role badge / dropdown */}
                  {canModify ? (
                    <div className="relative">
                      <button
                        onClick={() => setRoleMenuOpen(roleMenuOpen === u.id ? null : u.id)}
                        className="flex items-center gap-1 px-2 py-1 rounded border border-[var(--color-border)] hover:bg-gray-50 text-sm"
                        disabled={actionLoading === u.id}
                      >
                        {actionLoading === u.id ? (
                          <Spinner size="sm" />
                        ) : (
                          <>
                            <Badge variant={roleInfo.variant}>{roleInfo.label}</Badge>
                            <ChevronDown className="w-3 h-3 text-[var(--color-text-muted)]" />
                          </>
                        )}
                      </button>
                      {roleMenuOpen === u.id && (
                        <div className="absolute right-0 mt-1 w-40 bg-white border border-[var(--color-border)] rounded-lg shadow-lg z-10">
                          {availableRoles.map((role) => (
                            <button
                              key={role}
                              onClick={() => handleRoleChange(u.id, role)}
                              className={`block w-full text-left px-3 py-2 text-sm hover:bg-gray-50 ${
                                u.role === role ? 'bg-gray-50 font-medium' : ''
                              }`}
                            >
                              {ROLE_INFO[role]?.label || role}
                              {u.role === role && ' (current)'}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  ) : (
                    <Badge variant={roleInfo.variant}>{roleInfo.label}</Badge>
                  )}

                  {/* Deactivate button */}
                  {canModify && (
                    <button
                      onClick={() => handleToggleActive(u.id, u.full_name, u.is_active)}
                      disabled={actionLoading === u.id}
                      className={`text-xs px-2 py-1 rounded border ${
                        u.is_active
                          ? 'border-red-200 text-red-600 hover:bg-red-50'
                          : 'border-green-200 text-green-600 hover:bg-green-50'
                      }`}
                    >
                      {u.is_active ? 'Deactivate' : 'Reactivate'}
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </Card>

      {/* Invite Modal */}
      {showInvite && (
        <Modal isOpen={showInvite} title="Invite Team Member" onClose={() => setShowInvite(false)}>
          <form onSubmit={handleInvite} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-[var(--color-text)] mb-1">Full Name</label>
              <input
                type="text"
                value={inviteName}
                onChange={(e) => setInviteName(e.target.value)}
                required
                className="w-full text-sm border border-[var(--color-border)] rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]/20 focus:border-[var(--color-primary)]"
                placeholder="Jane Smith"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--color-text)] mb-1">Email</label>
              <input
                type="email"
                value={inviteEmail}
                onChange={(e) => setInviteEmail(e.target.value)}
                required
                className="w-full text-sm border border-[var(--color-border)] rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]/20 focus:border-[var(--color-primary)]"
                placeholder="jane@company.co.uk"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--color-text)] mb-1">Temporary Password</label>
              <input
                type="text"
                value={invitePassword}
                onChange={(e) => setInvitePassword(e.target.value)}
                required
                minLength={4}
                className="w-full text-sm border border-[var(--color-border)] rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]/20 focus:border-[var(--color-primary)]"
                placeholder="Temp1234"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--color-text)] mb-1">Role</label>
              <select
                value={inviteRole}
                onChange={(e) => setInviteRole(e.target.value)}
                className="w-full text-sm border border-[var(--color-border)] rounded-lg px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]/20"
              >
                <option value="viewer">Viewer — read-only access</option>
                <option value="editor">Editor — can upload data and run agents</option>
                {isSuperAdmin && <option value="admin">Admin — can manage users and settings</option>}
              </select>
            </div>
            <div className="flex justify-end gap-3 pt-2">
              <Button variant="secondary" onClick={() => setShowInvite(false)} type="button">
                Cancel
              </Button>
              <Button type="submit" disabled={inviteLoading}>
                {inviteLoading ? <Spinner size="sm" /> : <UserPlus className="w-4 h-4" />}
                Send Invite
              </Button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}
