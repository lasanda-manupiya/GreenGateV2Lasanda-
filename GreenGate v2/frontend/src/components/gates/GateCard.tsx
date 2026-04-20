import { Badge } from '../ui/Badge';
import { Progress } from '../ui/Progress';
import { Card } from '../ui/Card';
import type { GateStatus } from '../../types';

interface GateCardProps {
  gate: GateStatus;
  onClick?: () => void;
}

const statusVariant: Record<string, 'success' | 'warning' | 'neutral'> = {
  complete: 'success',
  active: 'warning',
  locked: 'neutral',
};

export function GateCard({ gate, onClick }: GateCardProps) {
  return (
    <Card hover={!!onClick} className={onClick ? 'cursor-pointer' : ''}>
      <div onClick={onClick}>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase text-[var(--color-primary)] bg-[var(--color-primary-light)] px-2 py-0.5 rounded">
              Gate {gate.gate}
            </span>
            <Badge variant={statusVariant[gate.status] || 'neutral'}>
              {gate.status}
            </Badge>
          </div>
        </div>
        <h3 className="text-lg font-semibold text-[var(--color-text)] mb-1">{gate.name}</h3>
        <p className="text-sm text-[var(--color-text-muted)] mb-1">Agent: {gate.agent}</p>
        <p className="text-sm text-[var(--color-text-muted)] mb-4">{gate.description}</p>
        <Progress value={gate.progress} size="sm" />
      </div>
    </Card>
  );
}
