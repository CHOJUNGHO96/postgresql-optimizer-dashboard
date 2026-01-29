import { useState, useCallback, type ReactNode } from 'react';
import { ChevronRight, ChevronDown, Copy, Check } from 'lucide-react';
import { cn } from '@/lib/utils';

interface JsonTreeViewProps {
  data: unknown;
  className?: string;
  defaultExpanded?: boolean;
  maxDepth?: number;
}

export function JsonTreeView({
  data,
  className,
  defaultExpanded = true,
  maxDepth = 10,
}: JsonTreeViewProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(data, null, 2));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Clipboard API not available
    }
  }, [data]);

  return (
    <div className={cn('relative', className)}>
      <button
        onClick={handleCopy}
        className="absolute right-2 top-2 z-10 rounded-md p-1.5 text-gray-400 hover:bg-gray-200 hover:text-gray-600 dark:hover:bg-gray-700 dark:hover:text-gray-300"
        title="JSON 복사"
        aria-label="JSON 복사"
      >
        {copied ? (
          <Check className="h-4 w-4 text-green-500" />
        ) : (
          <Copy className="h-4 w-4" />
        )}
      </button>
      <div className="overflow-auto rounded-lg border border-gray-200 bg-gray-50 p-4 font-mono text-sm dark:border-gray-700 dark:bg-gray-900">
        <JsonNode value={data} depth={0} defaultExpanded={defaultExpanded} maxDepth={maxDepth} />
      </div>
    </div>
  );
}

interface JsonNodeProps {
  value: unknown;
  depth: number;
  defaultExpanded: boolean;
  maxDepth: number;
  keyName?: string;
}

function JsonNode({ value, depth, defaultExpanded, maxDepth, keyName }: JsonNodeProps) {
  const [expanded, setExpanded] = useState(defaultExpanded && depth < maxDepth);

  const toggle = useCallback(() => {
    setExpanded((prev) => !prev);
  }, []);

  const indent = depth * 16;

  // Primitive values
  if (value === null) {
    return (
      <JsonLine indent={indent} keyName={keyName}>
        <span className="text-orange-500 dark:text-orange-400">null</span>
      </JsonLine>
    );
  }

  if (typeof value === 'boolean') {
    return (
      <JsonLine indent={indent} keyName={keyName}>
        <span className="text-purple-600 dark:text-purple-400">
          {value ? 'true' : 'false'}
        </span>
      </JsonLine>
    );
  }

  if (typeof value === 'number') {
    return (
      <JsonLine indent={indent} keyName={keyName}>
        <span className="text-blue-600 dark:text-blue-400">{value}</span>
      </JsonLine>
    );
  }

  if (typeof value === 'string') {
    return (
      <JsonLine indent={indent} keyName={keyName}>
        <span className="text-green-600 dark:text-green-400">"{value}"</span>
      </JsonLine>
    );
  }

  // Array
  if (Array.isArray(value)) {
    if (value.length === 0) {
      return (
        <JsonLine indent={indent} keyName={keyName}>
          <span className="text-gray-500">[]</span>
        </JsonLine>
      );
    }

    return (
      <div>
        <button
          onClick={toggle}
          className="flex items-center gap-1 hover:bg-gray-200 dark:hover:bg-gray-800 rounded px-1 -ml-1"
          style={{ paddingLeft: indent }}
        >
          {expanded ? (
            <ChevronDown className="h-3 w-3 text-gray-500" />
          ) : (
            <ChevronRight className="h-3 w-3 text-gray-500" />
          )}
          {keyName && (
            <span className="text-red-600 dark:text-red-400">"{keyName}"</span>
          )}
          {keyName && <span className="text-gray-500 mr-1">:</span>}
          <span className="text-gray-500">
            [{!expanded && `${value.length} items`}
          </span>
        </button>
        {expanded && (
          <>
            {value.map((item, index) => (
              <JsonNode
                key={index}
                value={item}
                depth={depth + 1}
                defaultExpanded={defaultExpanded}
                maxDepth={maxDepth}
              />
            ))}
            <div style={{ paddingLeft: indent }} className="text-gray-500">
              ]
            </div>
          </>
        )}
        {!expanded && <span className="text-gray-500">]</span>}
      </div>
    );
  }

  // Object
  if (typeof value === 'object') {
    const entries = Object.entries(value as Record<string, unknown>);

    if (entries.length === 0) {
      return (
        <JsonLine indent={indent} keyName={keyName}>
          <span className="text-gray-500">{'{}'}</span>
        </JsonLine>
      );
    }

    return (
      <div>
        <button
          onClick={toggle}
          className="flex items-center gap-1 hover:bg-gray-200 dark:hover:bg-gray-800 rounded px-1 -ml-1"
          style={{ paddingLeft: indent }}
        >
          {expanded ? (
            <ChevronDown className="h-3 w-3 text-gray-500" />
          ) : (
            <ChevronRight className="h-3 w-3 text-gray-500" />
          )}
          {keyName && (
            <span className="text-red-600 dark:text-red-400">"{keyName}"</span>
          )}
          {keyName && <span className="text-gray-500 mr-1">:</span>}
          <span className="text-gray-500">
            {'{'}
            {!expanded && `${entries.length} properties`}
          </span>
        </button>
        {expanded && (
          <>
            {entries.map(([key, val]) => (
              <JsonNode
                key={key}
                keyName={key}
                value={val}
                depth={depth + 1}
                defaultExpanded={defaultExpanded}
                maxDepth={maxDepth}
              />
            ))}
            <div style={{ paddingLeft: indent }} className="text-gray-500">
              {'}'}
            </div>
          </>
        )}
        {!expanded && <span className="text-gray-500">{'}'}</span>}
      </div>
    );
  }

  return null;
}

interface JsonLineProps {
  indent: number;
  keyName?: string;
  children: ReactNode;
}

function JsonLine({ indent, keyName, children }: JsonLineProps) {
  return (
    <div style={{ paddingLeft: indent }} className="py-0.5">
      {keyName && (
        <>
          <span className="text-red-600 dark:text-red-400">"{keyName}"</span>
          <span className="text-gray-500">: </span>
        </>
      )}
      {children}
    </div>
  );
}
