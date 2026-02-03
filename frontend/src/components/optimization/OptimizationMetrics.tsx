import { TrendingDown, Clock, DollarSign, Shield } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, Badge } from '@/components/common';
import type { OptimizedQueryResponse, RiskLevel } from '@/types/optimization';

interface OptimizationMetricsProps {
  optimization: OptimizedQueryResponse;
}

function getRiskBadgeVariant(risk: RiskLevel) {
  switch (risk) {
    case 'low':
      return 'success';
    case 'medium':
      return 'warning';
    case 'high':
      return 'danger';
  }
}

function getRiskColor(risk: RiskLevel) {
  switch (risk) {
    case 'low':
      return 'text-green-600';
    case 'medium':
      return 'text-yellow-600';
    case 'high':
      return 'text-red-600';
  }
}

export function OptimizationMetrics({ optimization }: OptimizationMetricsProps) {
  const { metrics, confidence_score, risk_assessment } = optimization;

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Cost Reduction</CardTitle>
          <DollarSign className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {metrics.estimated_cost_reduction !== null
              ? `${metrics.estimated_cost_reduction.toFixed(1)}%`
              : 'N/A'}
          </div>
          {metrics.optimized_total_cost !== null && (
            <p className="text-xs text-muted-foreground">
              Optimized cost: {metrics.optimized_total_cost.toFixed(2)}
            </p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Time Reduction</CardTitle>
          <Clock className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {metrics.estimated_time_reduction !== null
              ? `${metrics.estimated_time_reduction.toFixed(1)}%`
              : 'N/A'}
          </div>
          {metrics.optimized_execution_time_ms !== null && (
            <p className="text-xs text-muted-foreground">
              Execution: {metrics.optimized_execution_time_ms.toFixed(2)} ms
            </p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">AI Confidence</CardTitle>
          <TrendingDown className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {(confidence_score * 100).toFixed(0)}%
          </div>
          <p className="text-xs text-muted-foreground">
            Based on AI analysis
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Risk Level</CardTitle>
          <Shield className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2">
            <Badge variant={getRiskBadgeVariant(risk_assessment)}>
              {risk_assessment.toUpperCase()}
            </Badge>
          </div>
          <p className={`text-xs mt-1 ${getRiskColor(risk_assessment)}`}>
            {risk_assessment === 'low' && 'Safe to apply'}
            {risk_assessment === 'medium' && 'Test before production'}
            {risk_assessment === 'high' && 'Careful validation required'}
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
