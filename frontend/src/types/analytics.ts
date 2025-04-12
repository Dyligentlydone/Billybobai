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
  totalCount: number;
  responseTime: number;
  aiCost: number;
  serviceCost: number;
  deliveryRate: number;
  optOutRate: number;
  qualityMetrics: Array<{
    date: string;
    sentiment: number;
    quality: number;
  }>;
  responseTypes: Array<{
    type: string;
    count: number;
  }>;
  dailyCosts: Array<{
    date: string;
    ai: number;
    service: number;
    total: number;
  }>;
}

export interface EmailMetrics {
  totalCount: number;
  responseTime: number;
  aiCost: number;
  serviceCost: number;
  openRate: number;
  clickRate: number;
  bounceRate: number;
  unsubscribeRate: number;
  qualityMetrics: Array<{
    date: string;
    sentiment: number;
    quality: number;
  }>;
  responseTypes: Array<{
    type: string;
    count: number;
  }>;
  dailyCosts: Array<{
    date: string;
    ai: number;
    service: number;
    total: number;
  }>;
}

export interface VoiceMetrics {
  totalCount: number;
  responseTime: number;
  aiCost: number;
  serviceCost: number;
  callDuration: number;
  transferRate: number;
  qualityMetrics: Array<{
    date: string;
    sentiment: number;
    quality: number;
  }>;
  responseTypes: Array<{
    type: string;
    count: number;
  }>;
  dailyCosts: Array<{
    date: string;
    ai: number;
    service: number;
    total: number;
  }>;
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
