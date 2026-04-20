import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Bot, Clock } from 'lucide-react';
import type { Agent } from '../../types';

interface AgentStatusCardProps {
  agent: Agent;
  onRun?: () => void;
}

const statusConfig = {
  idle: { variant: 'neutral' as const, dot: 'bg-gray-400' },
  running: { variant: 'info' as const, dot: 'bg-blue-500 animate-pulse' },
  paused: { variant: 'warning' as const, dot: 'bg-amber-500' },
  error: { variant: 'error' as const, dot: 'bg-red-500' },
};

export function AgentStatusCard({ agent, onRun }: AgentStatusCardProps) {
  const config = statusConfig[agent.status];

  const formatLastActive = (date: string | null) => {
    if (!date) return 'Never';
    const d = new Date(date);
    const now = new Date();
    const diffMs = now.getTime() - d.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHrs = Math.floor(diffMins / 60);
    if (diffHrs < 24) return `${diffHrs}h ago`;
    return `${Math.floor(diffHrs / 24)}d ago`;
  };

  return (
    <Card hover>
      <div className="flex items-start gap-4">
        <div className="w-10 h-10 rounded-lg bg-[var(--color-primary-light)] flex items-center justify-center shrink-0">
          <Bot className="w-5 h-5 text-[var(--color-primary)]" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="text-sm font-semibold text-[var(--color-text)] truncate">
              {agent.name}
            </h3>
            <Badge variant={config.variant}>
              <span className={`inline-block w-1.5 h-1.5 rounded-full mr-1.5 ${config.dot}`} />
              {agent.status}
            </Badge>
          </div>
          <p className="text-xs text-[var(--color-text-muted)] mb-2">
            Gate {agent.gate} &middot; {agent.description}
          </p>
          <div className="flex items-center gap-1 text-xs text-[var(--color-text-muted)]">
            <Clock className="w-3 h-3" />
            Last active: {formatLastActive(agent.last_active)}
          </div>
          {agent.actions.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {agent.actions.map((action) => (
                <span
                  key={action}
                  className="text-xs bg-gray-100 text-[var(--color-text-muted)] px-2 py-0.5 rounded"
                >
                  {action}
                </span>
              ))}
            </div>
          )}
          {onRun && (
            <button
              onClick={onRun}
              className="mt-3 text-xs font-medium text-[var(--color-primary)] hover:underline"
            >
              Run Agent
            </button>
          )}
        </div>
      </div>
    </Card>
  );
}
