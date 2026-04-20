interface ProgressProps {
  value: number;
  max?: number;
  label?: string;
  showPercentage?: boolean;
  size?: 'sm' | 'md' | 'lg';
  color?: string;
  className?: string;
}

const sizeClasses = {
  sm: 'h-1.5',
  md: 'h-2.5',
  lg: 'h-4',
};

export function Progress({
  value,
  max = 100,
  label,
  showPercentage = true,
  size = 'md',
  color = 'bg-[var(--color-primary)]',
  className = '',
}: ProgressProps) {
  const percentage = Math.min(Math.round((value / max) * 100), 100);

  return (
    <div className={`w-full ${className}`}>
      {(label || showPercentage) && (
        <div className="flex items-center justify-between mb-1.5">
          {label && (
            <span className="text-sm font-medium text-[var(--color-text)]">{label}</span>
          )}
          {showPercentage && (
            <span className="text-sm text-[var(--color-text-muted)]">{percentage}%</span>
          )}
        </div>
      )}
      <div className={`w-full bg-gray-200 rounded-full overflow-hidden ${sizeClasses[size]}`}>
        <div
          className={`${color} ${sizeClasses[size]} rounded-full transition-all duration-500`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
