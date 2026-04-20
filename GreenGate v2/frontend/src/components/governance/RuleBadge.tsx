interface RuleBadgeProps {
  severity: 'blocker' | 'warning' | 'info';
  className?: string;
}

const severityConfig = {
  blocker: { bg: 'bg-red-100', text: 'text-red-800', label: 'Blocker' },
  warning: { bg: 'bg-amber-100', text: 'text-amber-800', label: 'Warning' },
  info: { bg: 'bg-blue-100', text: 'text-blue-800', label: 'Info' },
};

export function RuleBadge({ severity, className = '' }: RuleBadgeProps) {
  const config = severityConfig[severity];
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${config.bg} ${config.text} ${className}`}
    >
      {config.label}
    </span>
  );
}
