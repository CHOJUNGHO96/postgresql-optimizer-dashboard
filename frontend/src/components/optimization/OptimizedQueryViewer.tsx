import { Card, CardContent, CardHeader, CardTitle, Badge } from '@/components/common';
import type { OptimizedQueryResponse } from '@/types/optimization';

interface OptimizedQueryViewerProps {
  optimization: OptimizedQueryResponse;
  originalQuery: string;
}

export function OptimizedQueryViewer({
  optimization,
  originalQuery,
}: OptimizedQueryViewerProps) {
  const {
    optimized_query,
    optimization_rationale,
    optimization_category,
    applied_techniques,
    changes_summary,
  } = optimization;

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Optimized Query</CardTitle>
            {optimization_category && (
              <Badge variant="info">{optimization_category}</Badge>
            )}
          </div>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">AI-generated optimized SQL query</p>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <h4 className="text-sm font-semibold mb-2 text-muted-foreground">
                Original Query
              </h4>
              <pre className="bg-muted p-3 rounded-md text-xs overflow-x-auto">
                {originalQuery}
              </pre>
            </div>
            <div>
              <h4 className="text-sm font-semibold mb-2 text-green-600">
                Optimized Query
              </h4>
              <pre className="bg-muted p-3 rounded-md text-xs overflow-x-auto">
                {optimized_query}
              </pre>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Optimization Rationale</CardTitle>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">Why these changes were made</p>
        </CardHeader>
        <CardContent>
          <p className="text-sm whitespace-pre-wrap">{optimization_rationale}</p>
        </CardContent>
      </Card>

      {applied_techniques.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Applied Techniques</CardTitle>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">Optimization methods used</p>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {applied_techniques.map((technique, index) => (
                <Badge key={index} variant="info">
                  {technique}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {changes_summary && (
        <Card>
          <CardHeader>
            <CardTitle>Changes Summary</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {changes_summary.before && (
              <div>
                <h4 className="text-sm font-semibold mb-1">Before:</h4>
                <p className="text-sm text-muted-foreground">
                  {changes_summary.before}
                </p>
              </div>
            )}
            <hr className="my-3 border-gray-200 dark:border-gray-700" />
            {changes_summary.after && (
              <div>
                <h4 className="text-sm font-semibold mb-1">After:</h4>
                <p className="text-sm text-muted-foreground">
                  {changes_summary.after}
                </p>
              </div>
            )}
            {changes_summary.key_changes && changes_summary.key_changes.length > 0 && (
              <>
                <hr className="my-3 border-gray-200 dark:border-gray-700" />
                <div>
                  <h4 className="text-sm font-semibold mb-2">Key Changes:</h4>
                  <ul className="list-disc list-inside space-y-1">
                    {changes_summary.key_changes.map((change, index) => (
                      <li key={index} className="text-sm text-muted-foreground">
                        {change}
                      </li>
                    ))}
                  </ul>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
