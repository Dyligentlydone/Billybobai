import { useState } from 'react';
import { useQuery } from 'react-query';
import axios from 'axios';
import AnalyticsDashboard from '../components/analytics/AnalyticsDashboard';
import BusinessSelector from '../components/business/BusinessSelector';
import { useBusiness } from '../contexts/BusinessContext';

// Mock data for development/error cases
const MOCK_DATA = {
  sms: {
    totalCount: 0,
    responseTime: 0,
    aiCost: 0,
    serviceCost: 0,
    deliveryRate: 0,
    optOutRate: 0,
    qualityMetrics: Array.from({ length: 7 }, (_, i) => ({
      date: new Date(Date.now() - (6 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      sentiment: 0,
      quality: 0
    })),
    responseTypes: [
      { type: 'Quick Reply', count: 0 },
      { type: 'AI Generated', count: 0 },
      { type: 'Fallback', count: 0 }
    ],
    dailyCosts: Array.from({ length: 7 }, (_, i) => ({
      date: new Date(Date.now() - (6 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      ai: 0,
      service: 0,
      total: 0
    }))
  },
  email: {
    totalCount: 0,
    responseTime: 0,
    aiCost: 0,
    serviceCost: 0,
    openRate: 0,
    clickRate: 0,
    bounceRate: 0,
    unsubscribeRate: 0,
    qualityMetrics: Array.from({ length: 7 }, (_, i) => ({
      date: new Date(Date.now() - (6 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      sentiment: 0,
      quality: 0
    })),
    responseTypes: [
      { type: 'Opened', count: 0 },
      { type: 'Clicked', count: 0 },
      { type: 'No Action', count: 0 }
    ],
    dailyCosts: Array.from({ length: 7 }, (_, i) => ({
      date: new Date(Date.now() - (6 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      ai: 0,
      service: 0,
      total: 0
    }))
  },
  overview: {
    totalInteractions: 0,
    totalCost: 0,
    averageResponseTime: 0,
    successRate: 0
  },
  dateRange: {
    start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0]
  }
};

export default function Analytics() {
  const { selectedBusinessId } = useBusiness();

  const { data = MOCK_DATA, isLoading, isError } = useQuery(
    ['analytics', selectedBusinessId],
    async () => {
      if (!selectedBusinessId) return MOCK_DATA;
      try {
        const { data } = await axios.get(`/api/analytics/${selectedBusinessId}`);
        return data;
      } catch (error) {
        console.error('Failed to fetch analytics:', error);
        return MOCK_DATA;
      }
    },
    {
      enabled: !!selectedBusinessId,
      retry: false,
      refetchOnWindowFocus: false,
      refetchInterval: 30000 // Refresh every 30 seconds
    }
  );

  return (
    <div className="space-y-6">
      <div className="sm:flex sm:items-center sm:justify-between">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-semibold text-gray-900">Analytics</h1>
          <p className="mt-2 text-sm text-gray-700">
            View detailed analytics and insights for your communication workflows.
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <BusinessSelector />
        </div>
      </div>

      {!selectedBusinessId ? (
        <div className="bg-white shadow sm:rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900">No Business Selected</h3>
            <div className="mt-2 max-w-xl text-sm text-gray-500">
              <p>Please select a business above to view analytics.</p>
            </div>
          </div>
        </div>
      ) : (
        <AnalyticsDashboard 
          clientId={selectedBusinessId} 
          data={data} 
          isLoading={isLoading} 
        />
      )}
    </div>
  );
}
