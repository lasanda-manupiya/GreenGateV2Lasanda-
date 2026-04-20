import { Badge } from '../ui/Badge';
import { Activity } from 'lucide-react';
import type { AuditEntry } from '../../types';

interface ActivityFeedProps {
  entries: AuditEntry[];
  maxItems?: number;
  className?: string;
}

const resultVariant: Record<string, 'success' | 'error' | 'warning' | 'info'> = {
  pass: 'success',
  fail: 'error',
  warn: 'warning',
  info: 'info',
};

export function ActivityFeed({ entries, maxItems = 10, className = '' }: ActivityFeedProps) {
  const items = entries.slice(0, maxItems);

  const formatTime = (dateStr: string) => {
    const d = new Date(dateStr);
    return d.toLocaleString('en-GB', {
      day: '2-digit',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (items.length === 0) {
    return (
      <div className={`text-center py-8 text-[var(--color-text-muted)] text-sm ${className}`}>
        No recent activity
      </div>
    );
  }

  return (
    <div className={`space-y-0 ${className}`}>
      {items.map((entry) => (
        <div
          key={entry.id}
          className="flex items-start gap-3 py-3 border-b border-[var(--color-border)] last:border-0"
        >
          <div className="mt-0.5">
            <Activity className="w-4 h-4 text-[var(--color-text-muted)]" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-sm font-medium text-[var(--color-text)]">
                {entry.actor_name}
              </span>
              <span className="text-sm text-[var(--color-text-muted)]">{entry.action}</span>
              <Badge variant={resultVariant[entry.result] || 'neutral'}>
                {entry.result}
              </Badge>
            </div>
            <p className="text-xs text-[var(--color-text-muted)] mt-0.5 truncate">
              {entry.details}
            </p>
            <span className="text-xs text-[var(--color-text-muted)]">
              {formatTime(entry.created_at)} &middot; Gate {entry.gate}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}
