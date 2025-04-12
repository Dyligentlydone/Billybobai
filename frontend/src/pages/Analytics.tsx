import { useState } from 'react';
import AnalyticsDashboard from '../components/analytics/AnalyticsDashboard';
import BusinessSelector from '../components/business/BusinessSelector';

// Mock data for development
const MOCK_DATA = {
  sms: {
    totalCount: 1250,
    responseTime: 3.2,
    aiCost: 25.50,
    serviceCost: 45.75,
    deliveryRate: 98.5,
    optOutRate: 1.2,
    qualityMetrics: Array.from({ length: 7 }, (_, i) => ({
      date: new Date(Date.now() - (6 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      sentiment: 85 + Math.random() * 10,
      quality: 90 + Math.random() * 8
    })),
    responseTypes: [
      { type: 'Quick Reply', count: 450 },
      { type: 'AI Generated', count: 650 },
      { type: 'Fallback', count: 150 }
    ],
    dailyCosts: Array.from({ length: 7 }, (_, i) => ({
      date: new Date(Date.now() - (6 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      ai: 3 + Math.random() * 2,
      service: 5 + Math.random() * 3,
      total: 8 + Math.random() * 5
    }))
  },
  email: {
    totalCount: 850,
    responseTime: 5.1,
    aiCost: 18.25,
    serviceCost: 30.50,
    openRate: 45.2,
    clickRate: 12.5,
    bounceRate: 2.1,
    unsubscribeRate: 0.8,
    qualityMetrics: Array.from({ length: 7 }, (_, i) => ({
      date: new Date(Date.now() - (6 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      sentiment: 82 + Math.random() * 10,
      quality: 88 + Math.random() * 8
    })),
    responseTypes: [
      { type: 'Opened', count: 384 },
      { type: 'Clicked', count: 106 },
      { type: 'No Action', count: 360 }
    ],
    dailyCosts: Array.from({ length: 7 }, (_, i) => ({
      date: new Date(Date.now() - (6 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      ai: 2 + Math.random() * 1.5,
      service: 4 + Math.random() * 2,
      total: 6 + Math.random() * 3.5
    }))
  },
  voice: {
    totalCount: 320,
    responseTime: 8.5,
    aiCost: 35.75,
    serviceCost: 85.20,
    callDuration: 245,
    transferRate: 15.3,
    qualityMetrics: Array.from({ length: 7 }, (_, i) => ({
      date: new Date(Date.now() - (6 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      sentiment: 80 + Math.random() * 12,
      quality: 85 + Math.random() * 10
    })),
    responseTypes: [
      { type: 'Handled', count: 272 },
      { type: 'Transferred', count: 48 }
    ],
    dailyCosts: Array.from({ length: 7 }, (_, i) => ({
      date: new Date(Date.now() - (6 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      ai: 5 + Math.random() * 3,
      service: 12 + Math.random() * 5,
      total: 17 + Math.random() * 8
    }))
  },
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

export default function Analytics() {
  const [selectedBusiness, setSelectedBusiness] = useState<string>('');

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <BusinessSelector onBusinessChange={setSelectedBusiness} />
      </div>
      <AnalyticsDashboard businessId={selectedBusiness} clientId="demo" mockData={MOCK_DATA} />
    </div>
  );
}
