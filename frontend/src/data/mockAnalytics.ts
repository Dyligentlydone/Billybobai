import { AnalyticsData } from '../types/analytics';

const generateTimeSeriesData = (days: number, baseValue: number, variance: number) => {
  return Array.from({ length: days }, (_, i) => ({
    date: new Date(Date.now() - (days - i - 1) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    value: baseValue + Math.random() * variance - variance / 2
  }));
};

export const mockAnalyticsData: AnalyticsData = {
  sms: {
    delivery_metrics: {
      enabled: true,
      name: 'Delivery Metrics',
      description: 'Message delivery performance and reliability metrics',
      metrics: {
        'Delivery Rate': '98.5%',
        'Error Rate': '1.5%',
        'Average Latency': '2.3s',
        'Geographic Success': '96.7%'
      },
      charts: [
        {
          type: 'line',
          data: generateTimeSeriesData(7, 98, 4)
        }
      ]
    },
    engagement_metrics: {
      enabled: false,
      name: 'Engagement Metrics',
      description: 'User interaction and response metrics',
      metrics: {
        'Response Rate': '42%',
        'Click Rate': '15%',
        'Avg Response Time': '5.2m',
        'Active Conversations': '156'
      },
      charts: [
        {
          type: 'line',
          data: generateTimeSeriesData(7, 40, 10)
        }
      ]
    },
    quality_compliance: {
      enabled: true,
      name: 'Quality & Compliance',
      description: 'Message quality and regulatory compliance metrics',
      metrics: {
        'Opt-out Rate': '0.3%',
        'Spam Reports': '0.1%',
        'Quality Score': '94/100',
        'Compliance Rate': '99.9%'
      },
      charts: [
        {
          type: 'bar',
          data: generateTimeSeriesData(7, 95, 6)
        }
      ]
    },
    cost_efficiency: {
      enabled: true,
      name: 'Cost & Efficiency',
      description: 'Financial and resource utilization metrics',
      metrics: {
        'Cost per Message': '$0.0072',
        'AI Cost per Chat': '$0.015',
        'Monthly ROI': '287%',
        'Cost Savings': '42%'
      },
      charts: [
        {
          type: 'line',
          data: generateTimeSeriesData(7, 0.007, 0.002)
        }
      ]
    },
    performance_metrics: {
      enabled: true,
      name: 'Performance Metrics',
      description: 'System performance and reliability metrics',
      metrics: {
        'System Uptime': '99.99%',
        'API Response Time': '245ms',
        'Rate Limit Usage': '45%',
        'Error Recovery': '99.5%'
      },
      charts: [
        {
          type: 'line',
          data: generateTimeSeriesData(7, 99.9, 0.2)
        }
      ]
    },
    business_impact: {
      enabled: true,
      name: 'Business Impact',
      description: 'Business outcome and customer satisfaction metrics',
      metrics: {
        'Conversion Rate': '23%',
        'CSAT Score': '4.6/5',
        'Resolution Rate': '92%',
        'Customer Retention': '94%'
      },
      charts: [
        {
          type: 'bar',
          data: generateTimeSeriesData(7, 90, 10)
        }
      ]
    },
    ai_specific: {
      enabled: true,
      name: 'AI Metrics',
      description: 'AI performance and quality metrics',
      metrics: {
        'Response Time': '1.2s',
        'Sentiment Score': '0.85',
        'Intent Accuracy': '93%',
        'Human Handoffs': '7%'
      },
      charts: [
        {
          type: 'line',
          data: generateTimeSeriesData(7, 93, 5)
        }
      ]
    },
    security_fraud: {
      enabled: true,
      name: 'Security & Fraud',
      description: 'Security and fraud prevention metrics',
      metrics: {
        'Threat Detection': '99.7%',
        'Suspicious Activity': '0.3%',
        'Auth Success': '99.9%',
        'Risk Score': '12/100'
      },
      charts: [
        {
          type: 'line',
          data: generateTimeSeriesData(7, 99.7, 0.5)
        }
      ]
    }
  },
  email: {}, // To be implemented
  voice: {}, // To be implemented
  overview: {
    totalInteractions: 2420,
    totalCost: 205.25,
    averageResponseTime: 3.4,
    successRate: 94.2
  },
  dateRange: {
    start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0]
  }
};
