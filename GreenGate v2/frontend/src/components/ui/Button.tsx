import { type ButtonHTMLAttributes, type ReactNode } from 'react';
import { Spinner } from './Spinner';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  children: ReactNode;
}

const variantClasses = {
  primary:
    'bg-[var(--color-primary)] text-white hover:bg-[var(--color-primary-dark)] focus:ring-[var(--color-primary)]',
  secondary:
    'border border-[var(--color-border)] bg-white text-[var(--color-text)] hover:bg-gray-50 focus:ring-[var(--color-primary)]',
  danger:
    'bg-[var(--color-error)] text-white hover:bg-red-700 focus:ring-[var(--color-error)]',
  ghost:
    'text-[var(--color-text-muted)] hover:text-[var(--color-text)] hover:bg-gray-100 focus:ring-gray-300',
};

const sizeClasses = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-sm',
  lg: 'px-6 py-3 text-base',
};

export function Button({
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled,
  children,
  className = '',
  ...props
}: ButtonProps) {
  return (
    <button
      className={`inline-flex items-center justify-center gap-2 font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <Spinner size="sm" className="text-current" />}
      {children}
    </button>
  );
}
