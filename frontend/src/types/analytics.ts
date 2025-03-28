export interface BaseMetrics {
  totalCount: number;
  responseTime: number;
  aiCost: number;
  serviceCost: number;
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

export interface SMSMetrics extends BaseMetrics {
  deliveryRate: number;
  optOutRate: number;
}

export interface EmailMetrics extends BaseMetrics {
  openRate: number;
  clickRate: number;
  bounceRate: number;
  unsubscribeRate: number;
}

export interface VoiceMetrics extends BaseMetrics {
  callDuration: number;
  completionRate: number;
  transferRate: number;
  voicemailRate: number;
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
