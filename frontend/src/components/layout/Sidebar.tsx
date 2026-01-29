import { useState } from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  History,
  Database,
  Menu,
  X,
  ChevronLeft,
  ActivitySquare,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { ThemeToggle } from '@/components/common';
import { useHealthCheck } from '@/hooks';

interface NavItem {
  to: string;
  label: string;
  icon: React.ReactNode;
}

const navItems: NavItem[] = [
  {
    to: '/',
    label: '쿼리 분석',
    icon: <LayoutDashboard className="h-5 w-5" />,
  },
  {
    to: '/history',
    label: '분석 히스토리',
    icon: <History className="h-5 w-5" />,
  },
];

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const { data: health } = useHealthCheck();

  const isHealthy = health?.status === 'ok';

  return (
    <>
      {/* Mobile menu button */}
      <button
        onClick={() => setMobileOpen(true)}
        className="fixed left-4 top-4 z-40 rounded-lg bg-white p-2 shadow-md dark:bg-gray-800 lg:hidden"
        aria-label="메뉴 열기"
      >
        <Menu className="h-6 w-6 text-gray-700 dark:text-gray-200" />
      </button>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setMobileOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed left-0 top-0 z-50 flex h-full flex-col border-r border-gray-200 bg-white transition-all duration-300 dark:border-gray-700 dark:bg-gray-900',
          collapsed ? 'w-16' : 'w-64',
          mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        )}
      >
        {/* Header */}
        <div className="flex h-16 items-center justify-between border-b border-gray-200 px-4 dark:border-gray-700">
          {!collapsed && (
            <div className="flex items-center gap-2">
              <Database className="h-7 w-7 text-pg-500" />
              <span className="text-lg font-bold text-gray-900 dark:text-white">
                PGS Optimizer
              </span>
            </div>
          )}
          {collapsed && (
            <Database className="mx-auto h-7 w-7 text-pg-500" />
          )}
          <button
            onClick={() => setMobileOpen(false)}
            className="rounded-lg p-1 hover:bg-gray-100 dark:hover:bg-gray-800 lg:hidden"
            aria-label="메뉴 닫기"
          >
            <X className="h-5 w-5 text-gray-500" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto p-3">
          <ul className="space-y-1">
            {navItems.map((item) => (
              <li key={item.to}>
                <NavLink
                  to={item.to}
                  onClick={() => setMobileOpen(false)}
                  className={({ isActive }) =>
                    cn(
                      'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                      isActive
                        ? 'bg-pg-500/10 text-pg-600 dark:bg-pg-500/20 dark:text-pg-400'
                        : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-gray-200',
                      collapsed && 'justify-center'
                    )
                  }
                  title={collapsed ? item.label : undefined}
                >
                  {item.icon}
                  {!collapsed && <span>{item.label}</span>}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        {/* Footer */}
        <div className="border-t border-gray-200 p-3 dark:border-gray-700">
          {/* Status indicator */}
          <div
            className={cn(
              'mb-3 flex items-center gap-2 rounded-lg px-3 py-2 text-xs',
              isHealthy
                ? 'bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-400'
                : 'bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-400'
            )}
          >
            <ActivitySquare className="h-4 w-4" />
            {!collapsed && (
              <span>서버: {isHealthy ? '정상' : '연결 안됨'}</span>
            )}
          </div>

          <div className="flex items-center justify-between">
            <ThemeToggle />
            <button
              onClick={() => setCollapsed(!collapsed)}
              className="hidden rounded-lg p-2 text-gray-500 hover:bg-gray-100 hover:text-gray-700 dark:hover:bg-gray-800 dark:hover:text-gray-200 lg:block"
              aria-label={collapsed ? '사이드바 확장' : '사이드바 축소'}
            >
              <ChevronLeft
                className={cn(
                  'h-5 w-5 transition-transform',
                  collapsed && 'rotate-180'
                )}
              />
            </button>
          </div>
        </div>
      </aside>

      {/* Spacer for main content */}
      <div
        className={cn(
          'hidden flex-shrink-0 transition-all duration-300 lg:block',
          collapsed ? 'w-16' : 'w-64'
        )}
      />
    </>
  );
}
