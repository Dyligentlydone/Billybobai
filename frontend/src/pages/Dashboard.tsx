import { useQuery } from 'react-query';
import axios from 'axios';
import { useBusiness } from '../contexts/BusinessContext';
import BusinessSelector from '../components/business/BusinessSelector';
import AnalyticsDashboard from '../components/analytics/AnalyticsDashboard';

interface DashboardStats {
  activeWorkflows: number;
  messagesToday: number;
  successRate: number;
}

export default function Dashboard() {
  const { selectedBusinessId } = useBusiness();

  const { data: stats, isLoading } = useQuery<DashboardStats>(
    ['dashboard-stats', selectedBusinessId],
    async () => {
      if (!selectedBusinessId) return null;
      const { data } = await axios.get(`/api/dashboard/${selectedBusinessId}`);
      return data;
    },
    {
      enabled: !!selectedBusinessId,
      refetchInterval: 30000 // Refresh every 30 seconds
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
        <div className="mt-4 sm:mt-0">
          <BusinessSelector />
        </div>
      </div>

      {selectedBusinessId && (
        <AnalyticsDashboard clientId={selectedBusinessId} />
      )}

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16m-7 6h7" />
                </svg>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Active Workflows</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {isLoading ? (
                      <div className="animate-pulse h-6 w-12 bg-gray-200 rounded"></div>
                    ) : (
                      stats?.activeWorkflows ?? '-'
                    )}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Messages Today</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {isLoading ? (
                      <div className="animate-pulse h-6 w-12 bg-gray-200 rounded"></div>
                    ) : (
                      stats?.messagesToday ?? '-'
                    )}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Success Rate</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {isLoading ? (
                      <div className="animate-pulse h-6 w-12 bg-gray-200 rounded"></div>
                    ) : (
                      stats?.successRate ? `${stats.successRate}%` : '-'
                    )}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {!selectedBusinessId && (
        <div className="bg-white shadow sm:rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900">No Business Selected</h3>
            <div className="mt-2 max-w-xl text-sm text-gray-500">
              <p>Please select or enter a business ID above to view statistics.</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
