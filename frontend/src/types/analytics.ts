export interface MetricCategory {
  enabled: boolean;
  name: string;
  description: string;
  metrics: {
    [key: string]: number | string;
  };
  charts?: {
    type: 'line' | 'bar' | 'pie';
    data: any[];
  }[];
}

export interface SMSMetrics {
  delivery_metrics: MetricCategory;
  engagement_metrics: MetricCategory;
  quality_compliance: MetricCategory;
  cost_efficiency: MetricCategory;
  performance_metrics: MetricCategory;
  business_impact: MetricCategory;
  ai_specific: MetricCategory;
  security_fraud: MetricCategory;
}

export interface EmailMetrics {
  // Similar structure to SMSMetrics
  // Will be implemented later
  [key: string]: any;
}

export interface VoiceMetrics {
  // Similar structure to SMSMetrics
  // Will be implemented later
  [key: string]: any;
}

export interface AnalyticsData {
  sms: SMSMetrics;
  email: EmailMetrics;
  voice: VoiceMetrics;
  overview: {
    totalInteractions: number;
    totalCost: number;
    averageResponseTime: number;
    successRate: number;
  };
  dateRange: {
    start: string;
    end: string;
  };
}
