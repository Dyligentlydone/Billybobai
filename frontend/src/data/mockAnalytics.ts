import { AnalyticsData } from '../types/analytics';

export const mockAnalyticsData: AnalyticsData = {
  sms: {
    totalCount: '2,500',
    responseTime: '3.2s',
    deliveryRate: 0.98,
    optOutRate: 0.02,
    aiConfidence: 0.89,
    qualityMetrics: [
      { date: '2025-04-10', sentiment: 0.8, quality: 0.9 },
      { date: '2025-04-11', sentiment: 0.75, quality: 0.85 },
      { date: '2025-04-12', sentiment: 0.82, quality: 0.88 }
    ],
    responseTypes: [
      { type: 'FAQ', count: 150 },
      { type: 'Custom', count: 350 },
      { type: 'Fallback', count: 50 }
    ],
    dailyCosts: [
      { date: '2025-04-10', ai: 25, service: 15, total: 40 },
      { date: '2025-04-11', ai: 28, service: 15, total: 43 },
      { date: '2025-04-12', ai: 22, service: 15, total: 37 }
    ],
    hourlyActivity: [
      { hour: 8, count: 120 },
      { hour: 9, count: 180 },
      { hour: 10, count: 210 }
    ],
    conversations: []
  },
  voice: {
    totalCalls: 500,
    inboundCalls: 300,
    outboundCalls: 200,
    averageDuration: 180,
    successRate: 0.95,
    hourlyActivity: [
      { hour: 8, count: 25 },
      { hour: 9, count: 35 },
      { hour: 10, count: 40 }
    ]
  },
  email: {
    totalCount: 1000,
    openRate: 0.65,
    clickRate: 0.32,
    bounceRate: 0.02,
    hourlyActivity: [
      { hour: 8, count: 50 },
      { hour: 9, count: 75 },
      { hour: 10, count: 85 }
    ]
  },
  overview: {
    totalInteractions: 4000,
    totalCost: 2500,
    averageResponseTime: 3.5,
    successRate: 0.96
  },
  dateRange: {
    start: '2025-03-17',
    end: '2025-04-17'
  }
};
