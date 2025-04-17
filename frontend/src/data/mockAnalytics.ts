import { AnalyticsData } from '../types/analytics';

export const mockAnalyticsData: AnalyticsData = {
  sms: {
    totalCount: '1234',
    responseTime: '2.5s',
    deliveryRate: 0.98,
    optOutRate: 0.02,
    aiCost: 150.00,
    serviceCost: 75.00,
    qualityMetrics: [
      { name: 'Sentiment', value: 0.85 },
      { name: 'Quality', value: 0.92 }
    ],
    responseTypes: [
      { name: 'Quick Reply', value: 45 },
      { name: 'Custom', value: 30 },
      { name: 'Automated', value: 25 }
    ],
    dailyCosts: [
      { date: '2025-04-10', cost: 25.50 },
      { date: '2025-04-11', cost: 27.80 }
    ],
    hourlyActivity: Array.from({ length: 24 }, (_, i) => ({
      hour: i,
      count: Math.floor(Math.random() * 100)
    })),
    conversations: []
  },
  voice: {
    totalCount: '567',
    inboundCalls: 345,
    outboundCalls: 222,
    averageDuration: 180,
    successRate: 0.95,
    hourlyActivity: Array.from({ length: 24 }, (_, i) => ({
      hour: i,
      count: Math.floor(Math.random() * 50),
      successRate: 0.9 + Math.random() * 0.1,
      duration: Math.floor(Math.random() * 300)
    }))
  },
  email: {
    totalCount: '789',
    responseTime: '4.2s',
    openRate: 0.65,
    clickRate: 0.25,
    bounceRate: 0.02,
    hourlyActivity: Array.from({ length: 24 }, (_, i) => ({
      hour: i,
      count: Math.floor(Math.random() * 75),
      opens: Math.floor(Math.random() * 50),
      clicks: Math.floor(Math.random() * 20)
    }))
  },
  overview: {
    totalInteractions: '2590',
    totalCost: 450.75,
    averageResponseTime: '3.1s',
    successRate: 0.94
  },
  dateRange: {
    start: '2025-03-17T00:00:00Z',
    end: '2025-04-17T00:00:00Z'
  }
};
