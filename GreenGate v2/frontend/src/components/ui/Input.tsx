import { type InputHTMLAttributes, forwardRef } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, className = '', id, ...props }, ref) => {
    const inputId = id || label?.toLowerCase().replace(/\s+/g, '-');
    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={inputId}
            className="block text-sm font-medium text-[var(--color-text)] mb-1.5"
          >
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          className={`w-full px-3 py-2 border rounded-lg text-sm bg-white text-[var(--color-text)] placeholder-[var(--color-text-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent transition-colors ${
            error
              ? 'border-[var(--color-error)] focus:ring-[var(--color-error)]'
              : 'border-[var(--color-border)]'
          } ${className}`}
          {...props}
        />
        {error && <p className="mt-1 text-xs text-[var(--color-error)]">{error}</p>}
        {helperText && !error && (
          <p className="mt-1 text-xs text-[var(--color-text-muted)]">{helperText}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
