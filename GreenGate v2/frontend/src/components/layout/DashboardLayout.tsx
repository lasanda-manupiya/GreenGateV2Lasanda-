import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Shield,
  Target,
  TrendingUp,
  CheckCircle,
  FileText,
  Lock,
  Bot,
  Scale,
  Archive,
  Users,
  ShieldCheck,
  LogOut,
  X,
} from 'lucide-react';
import { useAuth } from '../../auth/useAuth';
import { useAppStore } from '../../store/appStore';
import { MobileHeader } from './MobileHeader';

interface NavItem {
  to: string;
  label: string;
  icon: typeof LayoutDashboard;
  requiredRole?: string;
}

const navItems: NavItem[] = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/gate/1', label: 'Gate 1: Assess', icon: Shield },
  { to: '/gate/2', label: 'Gate 2: Plan', icon: Target },
  { to: '/gate/3', label: 'Gate 3: Implement', icon: TrendingUp },
  { to: '/gate/4', label: 'Gate 4: Verify', icon: CheckCircle },
  { to: '/gate/5', label: 'Gate 5: Report', icon: FileText },
  { to: '/gate/6', label: 'Gate 6: Secure', icon: Lock },
  { to: '/agents', label: 'Agents', icon: Bot },
  { to: '/governance', label: 'Governance', icon: Scale },
  { to: '/evidence', label: 'Evidence', icon: Archive },
  { to: '/team', label: 'Team', icon: Users, requiredRole: 'admin' },
  { to: '/admin', label: 'Platform Admin', icon: ShieldCheck, requiredRole: 'superadmin' },
];

export function DashboardLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { sidebarOpen, setSidebarOpen, currentOrg } = useAppStore();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const orgName = currentOrg?.name || user?.organisation?.name || 'My Organisation';

  const ROLE_LEVEL: Record<string, number> = { superadmin: 4, admin: 3, editor: 2, viewer: 1 };
  const userLevel = ROLE_LEVEL[user?.role || 'viewer'] || 1;

  const visibleNavItems = navItems.filter((item) => {
    if (!item.requiredRole) return true;
    return userLevel >= (ROLE_LEVEL[item.requiredRole] || 0);
  });

  return (
    <div className="min-h-screen bg-[var(--color-background)]">
      <MobileHeader />

      {sidebarOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black/50 z-40"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside
        className={`fixed top-0 left-0 z-50 h-full w-64 bg-[#1B6B3A] text-white flex flex-col transition-transform duration-300 lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex items-center justify-between px-6 py-5 border-b border-white/10">
          <span
            className="text-xl font-bold tracking-tight"
            style={{ fontFamily: 'var(--font-display)' }}
          >
            SustainGate
          </span>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-1 rounded hover:bg-white/10"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="px-4 py-3 border-b border-white/10">
          <p className="text-xs text-white/60 uppercase tracking-wider">Organisation</p>
          <p className="text-sm font-medium truncate mt-0.5">{orgName}</p>
        </div>

        <nav className="flex-1 overflow-y-auto py-3 px-3">
          {visibleNavItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors mb-0.5 ${
                  isActive
                    ? 'bg-white/20 text-white'
                    : 'text-white/70 hover:bg-white/10 hover:text-white'
                }`
              }
            >
              <item.icon className="w-4.5 h-4.5 shrink-0" />
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="px-4 py-4 border-t border-white/10">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center text-sm font-medium">
              {(user?.full_name || user?.name || 'U').charAt(0).toUpperCase()}
            </div>
            <div className="min-w-0">
              <p className="text-sm font-medium truncate">{user?.full_name || user?.name || 'User'}</p>
              <p className="text-xs text-white/60 truncate">{user?.email || ''}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 text-sm text-white/70 hover:text-white transition-colors w-full px-1"
          >
            <LogOut className="w-4 h-4" />
            Sign out
          </button>
        </div>
      </aside>

      <main className="lg:ml-64 pt-14 lg:pt-0 min-h-screen">
        <div className="p-6 lg:p-8 max-w-7xl mx-auto">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
