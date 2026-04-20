import { useMutation, useQueryClient } from '@tanstack/react-query';
import { runAgent } from '../api/agents';
import { useAuth } from '../auth/useAuth';
import { useAppStore } from '../store/appStore';

export function useAgentRun() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const addNotification = useAppStore((s) => s.addNotification);

  return useMutation({
    mutationFn: ({ agentId, action }: { agentId: string; action: string }) =>
      runAgent(user!.org_id, agentId, action),
    onSuccess: (_data, variables) => {
      addNotification({
        type: 'success',
        message: `Agent ${variables.agentId} started action: ${variables.action}`,
      });
      queryClient.invalidateQueries({ queryKey: ['agents'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['emissions'] });
      queryClient.invalidateQueries({ queryKey: ['gateStatus'] });
    },
    onError: (error: Error) => {
      addNotification({
        type: 'error',
        message: `Agent run failed: ${error.message}`,
      });
    },
  });
}
