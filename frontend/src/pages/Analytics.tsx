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
      ai: 2 + Math.random() * 2,
      service: 4 + Math.random() * 2,
      total: 6 + Math.random() * 4
    }))
  },
  voice: {
    totalCount: 320,
    responseTime: 1.8,
    aiCost: 35.75,
    serviceCost: 85.25,
    callDuration: 145,
    completionRate: 88.5,
    transferRate: 15.2,
    voicemailRate: 8.5,
    qualityMetrics: Array.from({ length: 7 }, (_, i) => ({
      date: new Date(Date.now() - (6 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      sentiment: 88 + Math.random() * 10,
      quality: 92 + Math.random() * 6
    })),
    responseTypes: [
      { type: 'Completed', count: 283 },
      { type: 'Transferred', count: 49 },
      { type: 'Voicemail', count: 27 }
    ],
    dailyCosts: Array.from({ length: 7 }, (_, i) => ({
      date: new Date(Date.now() - (6 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      ai: 5 + Math.random() * 3,
      service: 12 + Math.random() * 4,
      total: 17 + Math.random() * 7
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
  const [selectedBusinessId, setSelectedBusinessId] = useState<string>('');

  return (
    <div className="space-y-6">
      <div className="sm:flex sm:items-center sm:justify-between">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-semibold text-gray-900">Analytics</h1>
          <p className="mt-2 text-sm text-gray-700">
            View metrics and performance for your automation workflows.
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <BusinessSelector onBusinessChange={setSelectedBusinessId} />
        </div>
      </div>
      
      {/* Always show dashboard with either real or mock data */}
      <AnalyticsDashboard 
        clientId={selectedBusinessId} 
        mockData={selectedBusinessId ? undefined : MOCK_DATA}
      />
    </div>
  );
}
