import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthGuard } from './auth/AuthGuard';
import { DashboardLayout } from './components/layout/DashboardLayout';
import { LoginPage } from './pages/Login';
import { OnboardingWizard } from './pages/Onboarding/OnboardingWizard';
import { DashboardPage } from './pages/Dashboard/DashboardPage';
import { Gate1Page } from './pages/Gate1/Gate1Page';
import { Gate2Page } from './pages/Gate2/Gate2Page';
import { Gate6Page } from './pages/Gate6/Gate6Page';
import { AgentsPage } from './pages/Agents/AgentsPage';
import { GovernancePage } from './pages/Governance/GovernancePage';
import { EvidencePage } from './pages/Evidence/EvidencePage';
import { TeamPage } from './pages/Team/TeamPage';
import { AdminPage } from './pages/Admin/AdminPage';

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/onboarding"
        element={
          <AuthGuard>
            <OnboardingWizard />
          </AuthGuard>
        }
      />
      <Route
        path="/"
        element={
          <AuthGuard>
            <DashboardLayout />
          </AuthGuard>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="gate/1" element={<Gate1Page />} />
        <Route path="gate/2" element={<Gate2Page />} />
        <Route path="gate/3" element={<div className="text-center py-12 text-[var(--color-text-muted)]">Gate 3: Implement — Coming soon</div>} />
        <Route path="gate/4" element={<div className="text-center py-12 text-[var(--color-text-muted)]">Gate 4: Verify — Coming soon</div>} />
        <Route path="gate/5" element={<div className="text-center py-12 text-[var(--color-text-muted)]">Gate 5: Report — Coming soon</div>} />
        <Route path="gate/6" element={<Gate6Page />} />
        <Route path="agents" element={<AgentsPage />} />
        <Route path="governance" element={<GovernancePage />} />
        <Route path="evidence" element={<EvidencePage />} />
        <Route path="team" element={<TeamPage />} />
        <Route path="admin" element={<AdminPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

export default App;
