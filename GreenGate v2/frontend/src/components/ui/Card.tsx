import type { ReactNode } from 'react';

interface CardProps {
  header?: ReactNode;
  children: ReactNode;
  className?: string;
  hover?: boolean;
  padding?: boolean;
}

export function Card({
  header,
  children,
  className = '',
  hover = false,
  padding = true,
}: CardProps) {
  return (
    <div
      className={`bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl shadow-sm ${
        hover ? 'hover:shadow-md transition-shadow cursor-pointer' : ''
      } ${className}`}
    >
      {header && (
        <div className="px-6 py-4 border-b border-[var(--color-border)]">{header}</div>
      )}
      <div className={padding ? 'p-6' : ''}>{children}</div>
    </div>
  );
}
