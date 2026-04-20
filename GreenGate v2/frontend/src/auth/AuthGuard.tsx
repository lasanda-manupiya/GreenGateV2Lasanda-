import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from './useAuth';
import { Spinner } from '../components/ui/Spinner';

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading, user } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-[var(--color-background)]">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (
    user?.organisation &&
    !user.organisation.onboarded &&
    location.pathname !== '/onboarding'
  ) {
    return <Navigate to="/onboarding" replace />;
  }

  return <>{children}</>;
}
