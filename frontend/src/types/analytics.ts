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

export interface Message {
  id: string;
  content: string;
  createdAt: string;
  direction: 'inbound' | 'outbound';
  status: string;
  phoneNumber: string;
  aiConfidence?: number;
  templateUsed?: string;
}

export interface Conversation {
  id: string;
  startedAt: string;
  topic: string;
  sentiment: 'positive' | 'neutral' | 'negative';
  messageCount: number;
  avgResponseTime: number;
  phoneNumber: string;
  messages: Message[];
}

export interface OverviewMetrics {
  totalInteractions: string;
  totalCost: number;
  averageResponseTime: string;
  successRate: number;
}

export interface SMSMetrics {
  totalCount: string;
  responseTime: string;
  deliveryRate: number;
  optOutRate: number;
  aiCost: number;
  serviceCost: number;
  qualityMetrics: Array<{
    name: string;
    value: number;
  }>;
  responseTypes: Array<{
    name: string;
    value: number;
  }>;
  dailyCosts: Array<{
    date: string;
    cost: number;
  }>;
  hourlyActivity: Array<{
    hour: number;
    count: number;
  }>;
  conversations: Array<{
    phoneNumber: string;
    lastMessage: string;
    timestamp: string;
  }>;
}

export interface VoiceMetrics {
  totalCount: string;
  inboundCalls: number;
  outboundCalls: number;
  averageDuration: number;
  successRate: number;
  hourlyActivity: Array<{
    hour: number;
    count: number;
    successRate: number;
    duration: number;
  }>;
}

export interface EmailMetrics {
  totalCount: string;
  responseTime: string;
  openRate: number;
  clickRate: number;
  bounceRate: number;
  hourlyActivity: Array<{
    hour: number;
    count: number;
    opens: number;
    clicks: number;
  }>;
}

export interface AnalyticsData {
  overview: OverviewMetrics;
  sms: SMSMetrics;
  voice: VoiceMetrics;
  email: EmailMetrics;
  dateRange: {
    start: string;
    end: string;
  };
}
