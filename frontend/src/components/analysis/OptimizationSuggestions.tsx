import { useState } from 'react';
import {
  Lightbulb,
  ChevronDown,
  ChevronUp,
  Copy,
  Check,
  Database,
  GitMerge,
  ArrowUpDown,
  Filter,
  Scan,
  Settings,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, Badge } from '@/components/common';
import { cn } from '@/lib/utils';
import type { OptimizationSuggestion, SuggestionCategory, SuggestionPriority } from '@/types';

interface OptimizationSuggestionsProps {
  suggestions: OptimizationSuggestion[];
  className?: string;
}

const priorityConfig: Record<SuggestionPriority, { badge: 'danger' | 'warning' | 'info' | 'default'; label: string }> = {
  critical: { badge: 'danger', label: '긴급' },
  high: { badge: 'warning', label: '높음' },
  medium: { badge: 'info', label: '보통' },
  low: { badge: 'default', label: '낮음' },
};

const categoryIcons: Record<SuggestionCategory, typeof Database> = {
  index: Database,
  join: GitMerge,
  sort: ArrowUpDown,
  filter: Filter,
  scan: Scan,
  general: Settings,
};

export function OptimizationSuggestions({
  suggestions,
  className,
}: OptimizationSuggestionsProps) {
  const hasSuggestions = suggestions.length > 0;

  return (
    <Card padding="lg" className={className}>
      <CardHeader>
        <div className="flex items-center gap-2">
          <Lightbulb className={cn(
            'h-5 w-5',
            hasSuggestions ? 'text-yellow-500' : 'text-gray-400'
          )} />
          <CardTitle>최적화 제안</CardTitle>
        </div>
        <Badge variant={hasSuggestions ? 'info' : 'default'}>
          {hasSuggestions ? `${suggestions.length}개 제안` : '최적화 제안 없음'}
        </Badge>
      </CardHeader>

      <CardContent>
        {hasSuggestions ? (
          <div className="space-y-3">
            {suggestions.map((suggestion) => (
              <SuggestionItem key={suggestion.id} suggestion={suggestion} />
            ))}
          </div>
        ) : (
          <div className="py-4 text-center text-gray-500 dark:text-gray-400">
            <Lightbulb className="mx-auto mb-2 h-8 w-8 text-gray-400" />
            <p>현재 쿼리에 대한 최적화 제안이 없습니다.</p>
            <p className="mt-1 text-sm">쿼리가 이미 최적화되어 있거나 추가 분석이 필요합니다.</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

interface SuggestionItemProps {
  suggestion: OptimizationSuggestion;
}

function SuggestionItem({ suggestion }: SuggestionItemProps) {
  const [isExpanded, setIsExpanded] = useState(suggestion.priority === 'critical');
  const [isCopied, setIsCopied] = useState(false);

  const config = priorityConfig[suggestion.priority];
  const CategoryIcon = categoryIcons[suggestion.category];

  const handleCopy = async () => {
    if (!suggestion.sql) return;

    try {
      await navigator.clipboard.writeText(suggestion.sql);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return (
    <div
      className={cn(
        'rounded-lg border transition-all',
        'border-gray-200 bg-gray-50 dark:border-gray-700 dark:bg-gray-800/50',
        isExpanded && 'ring-1 ring-gray-300 dark:ring-gray-600'
      )}
    >
      {/* Header */}
      <button
        className="flex w-full items-center justify-between gap-3 p-3 text-left"
        onClick={() => setIsExpanded(!isExpanded)}
        aria-expanded={isExpanded}
      >
        <div className="flex items-center gap-3">
          <div className={cn(
            'flex h-8 w-8 items-center justify-center rounded-lg',
            suggestion.priority === 'critical' && 'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400',
            suggestion.priority === 'high' && 'bg-orange-100 text-orange-600 dark:bg-orange-900/30 dark:text-orange-400',
            suggestion.priority === 'medium' && 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400',
            suggestion.priority === 'low' && 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
          )}>
            <CategoryIcon className="h-4 w-4" />
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <span className="font-medium text-gray-900 dark:text-white">
                {suggestion.title}
              </span>
              <Badge variant={config.badge} size="sm">
                {config.label}
              </Badge>
            </div>
          </div>
        </div>
        {isExpanded ? (
          <ChevronUp className="h-5 w-5 flex-shrink-0 text-gray-400" />
        ) : (
          <ChevronDown className="h-5 w-5 flex-shrink-0 text-gray-400" />
        )}
      </button>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="border-t border-gray-200 p-3 dark:border-gray-700">
          {/* Description */}
          <p className="mb-3 text-sm text-gray-600 dark:text-gray-400">
            {suggestion.description}
          </p>

          {/* SQL Code Block */}
          {suggestion.sql && (
            <div className="mb-3">
              <div className="relative">
                <pre className="overflow-x-auto rounded-lg bg-gray-900 p-3 text-sm text-gray-100 dark:bg-gray-950">
                  <code>{suggestion.sql}</code>
                </pre>
                <button
                  className={cn(
                    'absolute right-2 top-2 flex items-center gap-1 rounded px-2 py-1 text-xs transition-colors',
                    isCopied
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  )}
                  onClick={handleCopy}
                  aria-label={isCopied ? '복사됨' : 'SQL 복사'}
                >
                  {isCopied ? (
                    <>
                      <Check className="h-3 w-3" />
                      복사됨
                    </>
                  ) : (
                    <>
                      <Copy className="h-3 w-3" />
                      복사
                    </>
                  )}
                </button>
              </div>
            </div>
          )}

          {/* Expected Impact */}
          <div className="flex items-start gap-2 rounded-lg bg-green-50 p-2 text-sm dark:bg-green-900/20">
            <span className="mt-0.5 text-green-600 dark:text-green-400">📈</span>
            <div>
              <span className="font-medium text-green-700 dark:text-green-300">
                예상 개선:{' '}
              </span>
              <span className="text-green-600 dark:text-green-400">
                {suggestion.expectedImpact}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
