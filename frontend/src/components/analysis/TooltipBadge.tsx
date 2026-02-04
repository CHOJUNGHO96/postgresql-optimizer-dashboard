import { useState } from 'react';
import { cn } from '@/lib/utils';

type TooltipBadgeVariant = 'success' | 'warning' | 'danger' | 'info' | 'default';

interface TooltipBadgeProps {
  variant: TooltipBadgeVariant;
  tooltip: string;
  children: React.ReactNode;
  className?: string;
}

const variantStyles: Record<TooltipBadgeVariant, string> = {
  success:
    'bg-green-100 text-green-800 border-green-200 dark:bg-green-900/30 dark:text-green-400 dark:border-green-800',
  warning:
    'bg-yellow-100 text-yellow-800 border-yellow-200 dark:bg-yellow-900/30 dark:text-yellow-400 dark:border-yellow-800',
  danger:
    'bg-red-100 text-red-800 border-red-200 dark:bg-red-900/30 dark:text-red-400 dark:border-red-800',
  info: 'bg-blue-100 text-blue-800 border-blue-200 dark:bg-blue-900/30 dark:text-blue-400 dark:border-blue-800',
  default:
    'bg-gray-100 text-gray-800 border-gray-200 dark:bg-gray-800 dark:text-gray-300 dark:border-gray-700',
};

export function TooltipBadge({
  variant,
  tooltip,
  children,
  className,
}: TooltipBadgeProps) {
  const [showTooltip, setShowTooltip] = useState(false);

  return (
    <div className="relative inline-block">
      <span
        className={cn(
          'inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-xs font-medium cursor-help transition-colors',
          variantStyles[variant],
          className
        )}
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
      >
        {children}
      </span>
      {showTooltip && (
        <div
          className={cn(
            'absolute z-50 bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 text-xs',
            'bg-gray-900 text-white rounded-lg shadow-lg',
            'dark:bg-gray-700',
            'max-w-xs whitespace-normal text-center',
            'pointer-events-none'
          )}
        >
          {tooltip}
          <div
            className={cn(
              'absolute top-full left-1/2 -translate-x-1/2 -mt-1',
              'border-4 border-transparent border-t-gray-900',
              'dark:border-t-gray-700'
            )}
          />
        </div>
      )}
    </div>
  );
}
