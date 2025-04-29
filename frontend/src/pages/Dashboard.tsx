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
        const { data } = await axios.get(`/api/analytics/${selectedBusinessId}`, {
          params: {
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

  const mockData = {
    sms: {
      qualityMetrics: [
        { name: 'Sentiment', value: 0.85 },
        { name: 'Quality', value: 0.92 }
      ],
      dailyCosts: [
        { date: '2025-04-10', cost: 25.50 },
        { date: '2025-04-11', cost: 27.80 }
      ],
      hourlyActivity: Array.from({ length: 24 }, (_, i) => ({
        hour: i,
        count: Math.floor(Math.random() * 100)
      }))
    },
    voice: {
      hourlyActivity: Array.from({ length: 24 }, (_, i) => ({
        hour: i,
        count: Math.floor(Math.random() * 50),
        successRate: 0.9 + Math.random() * 0.1,
        duration: Math.floor(Math.random() * 300)
      }))
    },
    email: {
      hourlyActivity: Array.from({ length: 24 }, (_, i) => ({
        hour: i,
        count: Math.floor(Math.random() * 75),
        opens: Math.floor(Math.random() * 50),
        clicks: Math.floor(Math.random() * 20)
      }))
    }
  };

  const costBreakdown = stats.sms.dailyCosts.map(cost => ({
    name: cost.date,
    value: cost.cost
  }));

  const aiMetrics = stats.sms.qualityMetrics.map(metric => ({
    name: metric.name,
    value: metric.value
  }));

  const hourlyActivity = mockData.sms.hourlyActivity;
  const hourlyVoiceActivity = mockData.voice.hourlyActivity;
  const hourlyEmailActivity = mockData.email.hourlyActivity;

  const recentActivity = stats.sms.conversations.map(conv => ({
    name: conv.phoneNumber,
    value: conv.lastMessage
  }));

  return (
    <div className="space-y-6">
      <div className="sm:flex sm:items-center sm:justify-between">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-semibold text-gray-900">Dashboard</h1>
          <p className="mt-2 text-sm text-gray-700">
            Welcome to Dyligent. Manage your communication workflows across multiple channels.
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
      <div className="bg-white shadow rounded-lg p-4">
        <h2 className="text-lg font-medium mb-4">Recent Activity</h2>
        <div className="space-y-4">
          {recentActivity.map((activity, index) => (
            <div key={index} className="flex items-center justify-between">
              <div className="flex items-center">
                <div className={`w-2 h-2 rounded-full ${activity.value ? 'bg-green-500' : 'bg-gray-500'}`} />
                <span className="ml-3 text-sm text-gray-500">{activity.value}</span>
              </div>
              <span className="text-sm text-gray-400">{activity.name}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white shadow rounded-lg p-4">
        <h2 className="text-lg font-medium mb-4">Cost Breakdown</h2>
        <div className="space-y-4">
          {costBreakdown.map((item, index) => (
            <div key={index} className="flex items-center justify-between">
              <span className="text-sm text-gray-500">{item.name}</span>
              <span className="text-sm font-medium">${item.value.toFixed(2)}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white shadow rounded-lg p-4">
        <h2 className="text-lg font-medium mb-4">AI Performance</h2>
        <div className="space-y-4">
          {aiMetrics.map((metric, index) => (
            <div key={index} className="flex items-center justify-between">
              <span className="text-sm text-gray-500">{metric.name}</span>
              <span className="text-sm font-medium">{(metric.value * 100).toFixed(1)}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function getStatusColor(status: string) {
  switch (status) {
    case 'success':
      return 'bg-green-500';
    case 'error':
      return 'bg-red-500';
    default:
      return 'bg-gray-500';
  }
}
