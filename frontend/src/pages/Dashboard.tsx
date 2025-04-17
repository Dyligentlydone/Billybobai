import { useQuery } from 'react-query';
import axios from 'axios';
import { useBusiness } from '../contexts/BusinessContext';
import BusinessSelector from '../components/business/BusinessSelector';
import AnalyticsDashboard from '../components/analytics/AnalyticsDashboard';
import { AnalyticsData } from '../types/analytics';

// Mock data for development/error cases
const MOCK_STATS: AnalyticsData = {
  sms: {
    totalCount: '0',
    responseTime: '0s',
    aiCost: 0,
    serviceCost: 0,
    deliveryRate: 0,
    optOutRate: 0,
    qualityMetrics: [],
    responseTypes: [],
    dailyCosts: [],
    hourlyActivity: [],
    conversations: []
  },
  email: {
    totalCount: '0',
    responseTime: '0s',
    openRate: 0,
    clickRate: 0,
    bounceRate: 0,
    hourlyActivity: []
  },
  voice: {
    totalCount: '0',
    inboundCalls: 0,
    outboundCalls: 0,
    averageDuration: 0,
    successRate: 0,
    hourlyActivity: []
  },
  overview: {
    totalInteractions: '0',
    totalCost: 0,
    averageResponseTime: '0s',
    successRate: 0
  },
  dateRange: {
    start: '',
    end: ''
  }
};

export default function Dashboard() {
  const { selectedBusinessId } = useBusiness();

  // Calculate date range for analytics
  const end = new Date();
  const start = new Date();
  start.setDate(start.getDate() - 30); // Last 30 days

  const { data: stats = MOCK_STATS, isLoading, isError } = useQuery<AnalyticsData>(
    ['dashboard-stats', selectedBusinessId],
    async () => {
      if (!selectedBusinessId) return MOCK_STATS;
      try {
        const { data } = await axios.get('/api/analytics', {
          params: {
            clientId: selectedBusinessId,
            startDate: start.toISOString().split('T')[0],
            endDate: end.toISOString().split('T')[0]
          }
        });
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

  const analyticsData: AnalyticsData = {
    sms: {
      totalCount: '1,234',
      responseTime: '2.5s',
      deliveryRate: 0.98,
      optOutRate: 0.02,
      aiCost: 150,
      serviceCost: 300,
      qualityMetrics: [
        { date: '2025-04-17', sentiment: 0.85, quality: 0.9 }
      ],
      responseTypes: [
        { type: 'Auto', count: 980 },
        { type: 'Manual', count: 254 }
      ],
      dailyCosts: [
        { date: '2025-04-17', ai: 50, service: 100, total: 150 }
      ],
      hourlyActivity: [
        { hour: 9, count: 125 },
        { hour: 10, count: 145 }
      ],
      conversations: []
    },
    voice: {
      totalCount: '456',
      inboundCalls: 300,
      outboundCalls: 156,
      averageDuration: 180,
      successRate: 0.95,
      hourlyActivity: [
        { hour: 9, count: 45 },
        { hour: 10, count: 55 }
      ]
    },
    email: {
      totalCount: '789',
      responseTime: '5m',
      openRate: 0.65,
      clickRate: 0.32,
      bounceRate: 0.02,
      hourlyActivity: [
        { hour: 9, count: 78 },
        { hour: 10, count: 89 }
      ]
    },
    overview: {
      totalInteractions: '2,479',
      totalCost: 2500,
      averageResponseTime: '3.5s',
      successRate: 0.96
    },
    dateRange: {
      start: '2025-04-10',
      end: '2025-04-17'
    }
  };

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
