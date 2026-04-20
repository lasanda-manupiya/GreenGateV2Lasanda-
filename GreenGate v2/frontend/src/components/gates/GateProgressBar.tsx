import { Lock, Check, Circle } from 'lucide-react';
import type { GateStatus } from '../../types';

interface GateProgressBarProps {
  gates: GateStatus[];
  className?: string;
}

const statusIcons = {
  locked: Lock,
  active: Circle,
  complete: Check,
};

const statusColors = {
  locked: 'bg-gray-200 text-gray-400 border-gray-300',
  active: 'bg-[var(--color-secondary-light)] text-[var(--color-secondary)] border-[var(--color-secondary)]',
  complete: 'bg-emerald-100 text-emerald-600 border-emerald-500',
};

const lineColors = {
  locked: 'bg-gray-200',
  active: 'bg-[var(--color-secondary)]',
  complete: 'bg-emerald-500',
};

export function GateProgressBar({ gates, className = '' }: GateProgressBarProps) {
  const mainGates = gates.filter((g) => g.gate <= 5);
  const gate6 = gates.find((g) => g.gate === 6);

  return (
    <div className={className}>
      <div className="flex items-center justify-between mb-6">
        {mainGates.map((gate, idx) => {
          const Icon = statusIcons[gate.status];
          return (
            <div key={gate.gate} className="flex items-center flex-1">
              <div className="flex flex-col items-center">
                <div
                  className={`w-10 h-10 rounded-full border-2 flex items-center justify-center ${statusColors[gate.status]}`}
                >
                  <Icon className="w-4 h-4" />
                </div>
                <span className="text-xs font-medium text-[var(--color-text)] mt-2">
                  Gate {gate.gate}
                </span>
                <span className="text-xs text-[var(--color-text-muted)] text-center max-w-[80px] truncate">
                  {gate.name}
                </span>
              </div>
              {idx < mainGates.length - 1 && (
                <div className={`flex-1 h-0.5 mx-2 mt-[-24px] ${lineColors[gate.status]}`} />
              )}
            </div>
          );
        })}
      </div>
      {gate6 && (
        <div className="flex items-center gap-2 pt-3 border-t border-[var(--color-border)]">
          <Lock className="w-4 h-4 text-[var(--color-text-muted)]" />
          <span className="text-sm text-[var(--color-text-muted)]">
            Gate 6: {gate6.name} — Continuous
          </span>
          <span className="ml-auto text-xs text-[var(--color-text-muted)]">
            {gate6.progress}% complete
          </span>
        </div>
      )}
    </div>
  );
}
