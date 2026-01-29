import {
  Search,
  GitMerge,
  Calculator,
  ArrowUpDown,
  CircleDot,
  Scan,
  Database,
} from 'lucide-react';
import { Badge } from '@/components/common';
import { getNodeTypeInfo, cn } from '@/lib/utils';
import type { PlanNodeType, NodeTypeCategory } from '@/types';

interface NodeTypeBadgeProps {
  nodeType: PlanNodeType;
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
  showDescription?: boolean;
  className?: string;
}

const categoryIcons: Record<NodeTypeCategory, React.ReactNode> = {
  scan: <Search className="h-3.5 w-3.5" />,
  join: <GitMerge className="h-3.5 w-3.5" />,
  aggregate: <Calculator className="h-3.5 w-3.5" />,
  sort: <ArrowUpDown className="h-3.5 w-3.5" />,
  other: <CircleDot className="h-3.5 w-3.5" />,
};

const categoryBadgeVariants: Record<NodeTypeCategory, 'info' | 'primary' | 'warning' | 'success' | 'default'> = {
  scan: 'info',
  join: 'primary',
  aggregate: 'warning',
  sort: 'success',
  other: 'default',
};

export function NodeTypeBadge({
  nodeType,
  size = 'md',
  showIcon = true,
  showDescription = false,
  className,
}: NodeTypeBadgeProps) {
  const info = getNodeTypeInfo(nodeType);
  const Icon = categoryIcons[info.category];
  const variant = categoryBadgeVariants[info.category];

  return (
    <div className={cn('inline-flex flex-col items-start gap-1', className)}>
      <Badge variant={variant} size={size}>
        {showIcon && Icon}
        <span>{info.label}</span>
      </Badge>
      {showDescription && (
        <span className="text-xs text-gray-500 dark:text-gray-400">
          {info.description}
        </span>
      )}
    </div>
  );
}

interface NodeTypeCardProps {
  nodeType: PlanNodeType;
  className?: string;
}

export function NodeTypeCard({ nodeType, className }: NodeTypeCardProps) {
  const info = getNodeTypeInfo(nodeType);
  const Icon = categoryIcons[info.category];

  // Get specific icon for certain node types
  const getSpecificIcon = () => {
    if (nodeType === 'Seq Scan') return <Scan className="h-6 w-6" />;
    if (nodeType.includes('Index')) return <Database className="h-6 w-6" />;
    return Icon;
  };

  return (
    <div
      className={cn(
        'flex items-center gap-4 rounded-xl border p-4 transition-all',
        info.bgColor,
        className
      )}
    >
      <div
        className={cn(
          'flex h-12 w-12 items-center justify-center rounded-lg',
          info.color,
          'bg-white/50 dark:bg-black/20'
        )}
      >
        {getSpecificIcon()}
      </div>
      <div>
        <p className={cn('text-lg font-bold', info.color)}>{info.label}</p>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          {info.description}
        </p>
      </div>
    </div>
  );
}
