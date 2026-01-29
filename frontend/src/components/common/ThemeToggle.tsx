import { Moon, Sun } from 'lucide-react';
import { useThemeContext } from '@/contexts';
import { cn } from '@/lib/utils';

interface ThemeToggleProps {
  className?: string;
}

export function ThemeToggle({ className }: ThemeToggleProps) {
  const { theme, toggleTheme } = useThemeContext();

  return (
    <button
      onClick={toggleTheme}
      className={cn(
        'rounded-lg p-2 text-gray-500 transition-colors hover:bg-gray-100 hover:text-gray-700',
        'dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-gray-200',
        'focus:outline-none focus:ring-2 focus:ring-pg-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900',
        className
      )}
      aria-label={theme === 'dark' ? '라이트 모드로 전환' : '다크 모드로 전환'}
      title={theme === 'dark' ? '라이트 모드로 전환' : '다크 모드로 전환'}
    >
      {theme === 'dark' ? (
        <Sun className="h-5 w-5" aria-hidden="true" />
      ) : (
        <Moon className="h-5 w-5" aria-hidden="true" />
      )}
    </button>
  );
}
