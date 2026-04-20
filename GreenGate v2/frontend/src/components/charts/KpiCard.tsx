import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { Card } from '../ui/Card';

interface KpiCardProps {
  title: string;
  value: string | number;
  unit?: string;
  trend?: 'up' | 'down' | 'flat';
  trendValue?: string;
  description?: string;
  icon?: React.ReactNode;
}

const trendConfig = {
  up: { icon: TrendingUp, color: 'text-emerald-600', bg: 'bg-emerald-50' },
  down: { icon: TrendingDown, color: 'text-red-600', bg: 'bg-red-50' },
  flat: { icon: Minus, color: 'text-gray-500', bg: 'bg-gray-50' },
};

export function KpiCard({
  title,
  value,
  unit,
  trend,
  trendValue,
  description,
  icon,
}: KpiCardProps) {
  const trendCfg = trend ? trendConfig[trend] : null;
  const TrendIcon = trendCfg?.icon;

  return (
    <Card>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-[var(--color-text-muted)] mb-1">{title}</p>
          <div className="flex items-baseline gap-1.5">
            <span
              className="text-2xl font-bold text-[var(--color-text)]"
              style={{ fontFamily: 'var(--font-display)' }}
            >
              {value}
            </span>
            {unit && (
              <span className="text-sm text-[var(--color-text-muted)]">{unit}</span>
            )}
          </div>
          {trendCfg && TrendIcon && (
            <div className={`flex items-center gap-1 mt-2 ${trendCfg.color}`}>
              <TrendIcon className="w-3.5 h-3.5" />
              {trendValue && <span className="text-xs font-medium">{trendValue}</span>}
            </div>
          )}
          {description && (
            <p className="text-xs text-[var(--color-text-muted)] mt-1">{description}</p>
          )}
        </div>
        {icon && (
          <div className="w-10 h-10 rounded-lg bg-[var(--color-primary-light)] flex items-center justify-center">
            {icon}
          </div>
        )}
      </div>
    </Card>
  );
}
