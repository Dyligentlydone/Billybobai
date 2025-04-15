import { useQuery } from 'react-query';
import axios from 'axios';
import { useBusiness } from '../contexts/BusinessContext';
import BusinessSelector from '../components/business/BusinessSelector';
import AnalyticsDashboard from '../components/analytics/AnalyticsDashboard';
import { AnalyticsData } from '../types/analytics';

// Mock data for development/error cases
const MOCK_STATS: AnalyticsData = {
  sms: {
    totalCount: 0,
    responseTime: 0,
    aiCost: 0,
    serviceCost: 0,
    deliveryRate: 0,
    optOutRate: 0,
    qualityMetrics: [],
    responseTypes: [],
    dailyCosts: []
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
    qualityMetrics: [],
    responseTypes: [],
    dailyCosts: []
  },
  voice: {
    totalCount: 0,
    responseTime: 0,
    aiCost: 0,
    serviceCost: 0,
    callDuration: 0,
    transferRate: 0,
    qualityMetrics: [],
    responseTypes: [],
    dailyCosts: []
  },
  overview: {
    totalInteractions: 0,
    totalCost: 0,
    averageResponseTime: 0,
    successRate: 0
  },
  dateRange: {
    start: new Date().toISOString(),
    end: new Date().toISOString()
  }
};

export default function Dashboard() {
  const { selectedBusinessId } = useBusiness();

  const { data: stats = MOCK_STATS, isLoading, isError } = useQuery<AnalyticsData>(
    ['dashboard-stats', selectedBusinessId],
    async () => {
      if (!selectedBusinessId) return MOCK_STATS;
      try {
        const { data } = await axios.get(`/api/dashboard/${selectedBusinessId}`);
        return data;
      } catch (error) {
        console.error('Failed to fetch dashboard stats:', error);
        return MOCK_STATS;
      }
    },
    {
      enabled: !!selectedBusinessId,
      refetchInterval: 30000, // Refresh every 30 seconds
      retry: false,
      refetchOnWindowFocus: false
    }
  );

  return (
    <div className="space-y-6">
      <div className="sm:flex sm:items-center sm:justify-between">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-semibold text-gray-900">Dashboard</h1>
          <p className="mt-2 text-sm text-gray-700">
            Welcome to Twilio Automation Hub. Manage your communication workflows across multiple channels.
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <BusinessSelector />
        </div>
      </div>

      {!selectedBusinessId ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <h3 className="mt-2 text-sm font-semibold text-gray-900">No business selected</h3>
          <p className="mt-1 text-sm text-gray-500">Please select a business to view its dashboard.</p>
        </div>
      ) : (
        <AnalyticsDashboard 
          clientId={selectedBusinessId} 
          data={stats} 
          isLoading={isLoading} 
        />
      )}
    </div>
  );
}
