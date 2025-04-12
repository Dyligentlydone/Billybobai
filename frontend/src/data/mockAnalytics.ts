import { AnalyticsData } from '../types/analytics';

export const mockAnalyticsData: AnalyticsData = {
  sms: {
    totalCount: 1000,
    responseTime: 2.5,
    aiCost: 50.0,
    serviceCost: 100.0,
    deliveryRate: 0.98,
    optOutRate: 0.02,
    qualityMetrics: [
      { date: '2025-04-01', sentiment: 0.8, quality: 0.9 },
      { date: '2025-04-02', sentiment: 0.85, quality: 0.88 }
    ],
    responseTypes: [
      { type: 'auto', count: 800 },
      { type: 'manual', count: 200 }
    ],
    dailyCosts: [
      { date: '2025-04-01', ai: 25, service: 50, total: 75 },
      { date: '2025-04-02', ai: 25, service: 50, total: 75 }
    ]
  },
  email: {
    totalCount: 500,
    responseTime: 3.0,
    aiCost: 25.0,
    serviceCost: 50.0,
    openRate: 0.65,
    clickRate: 0.25,
    bounceRate: 0.02,
    unsubscribeRate: 0.01,
    qualityMetrics: [
      { date: '2025-04-01', sentiment: 0.75, quality: 0.85 },
      { date: '2025-04-02', sentiment: 0.78, quality: 0.87 }
    ],
    responseTypes: [
      { type: 'auto', count: 400 },
      { type: 'manual', count: 100 }
    ],
    dailyCosts: [
      { date: '2025-04-01', ai: 12.5, service: 25, total: 37.5 },
      { date: '2025-04-02', ai: 12.5, service: 25, total: 37.5 }
    ]
  },
  voice: {
    totalCount: 200,
    responseTime: 4.0,
    aiCost: 100.0,
    serviceCost: 200.0,
    callDuration: 180,
    transferRate: 0.15,
    qualityMetrics: [
      { date: '2025-04-01', sentiment: 0.7, quality: 0.8 },
      { date: '2025-04-02', sentiment: 0.72, quality: 0.82 }
    ],
    responseTypes: [
      { type: 'auto', count: 150 },
      { type: 'transfer', count: 50 }
    ],
    dailyCosts: [
      { date: '2025-04-01', ai: 50, service: 100, total: 150 },
      { date: '2025-04-02', ai: 50, service: 100, total: 150 }
    ]
  },
  overview: {
    totalInteractions: 1700,
    totalCost: 525.0,
    averageResponseTime: 3.2,
    successRate: 0.95
  },
  dateRange: {
    start: '2025-04-01',
    end: '2025-04-02'
  }
};
