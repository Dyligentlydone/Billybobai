import React from 'react';
import { useQuery } from 'react-query';
import axios from 'axios';
import { useBusiness } from '../contexts/BusinessContext';
import BusinessSelector from '../components/business/BusinessSelector';
import MessageStatusMetrics from '../components/analytics/MessageStatusMetrics';
import { Tab } from '@headlessui/react';

function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(' ');
}

export default function Analytics() {
  const { selectedBusinessId } = useBusiness();
  
  // Calculate date range (last 30 days)
  const end = new Date();
  const start = new Date();
  start.setDate(start.getDate() - 30);
  
  const { data: analyticsData, isLoading } = useQuery(
    ['analytics', selectedBusinessId],
    async () => {
      if (!selectedBusinessId) return null;
      const { data } = await axios.get('/api/analytics', {
        params: {
          clientId: selectedBusinessId,
          startDate: start.toISOString().split('T')[0],
          endDate: end.toISOString().split('T')[0]
        }
      });
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
          <h1 className="text-2xl font-semibold text-gray-900">Analytics</h1>
          <p className="mt-2 text-sm text-gray-700">
            Detailed analytics and insights for your communication workflows.
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <BusinessSelector />
        </div>
      </div>

      <Tab.Group>
        <Tab.List className="flex space-x-1 rounded-xl bg-blue-900/20 p-1">
          <Tab
            className={({ selected }) =>
              classNames(
                'w-full rounded-lg py-2.5 text-sm font-medium leading-5',
                'ring-white ring-opacity-60 ring-offset-2 ring-offset-blue-400 focus:outline-none focus:ring-2',
                selected
                  ? 'bg-white shadow text-blue-700'
                  : 'text-blue-100 hover:bg-white/[0.12] hover:text-white'
              )
            }
          >
            Message Status
          </Tab>
          <Tab
            className={({ selected }) =>
              classNames(
                'w-full rounded-lg py-2.5 text-sm font-medium leading-5',
                'ring-white ring-opacity-60 ring-offset-2 ring-offset-blue-400 focus:outline-none focus:ring-2',
                selected
                  ? 'bg-white shadow text-blue-700'
                  : 'text-blue-100 hover:bg-white/[0.12] hover:text-white'
              )
            }
          >
            AI Performance
          </Tab>
          <Tab
            className={({ selected }) =>
              classNames(
                'w-full rounded-lg py-2.5 text-sm font-medium leading-5',
                'ring-white ring-opacity-60 ring-offset-2 ring-offset-blue-400 focus:outline-none focus:ring-2',
                selected
                  ? 'bg-white shadow text-blue-700'
                  : 'text-blue-100 hover:bg-white/[0.12] hover:text-white'
              )
            }
          >
            Cost Analysis
          </Tab>
        </Tab.List>
        <Tab.Panels className="mt-2">
          <Tab.Panel>
            {!selectedBusinessId ? (
              <div className="relative">
                <MessageStatusMetrics isPlaceholder={true} />
                <div className="absolute inset-0 bg-white/50 flex items-center justify-center">
                  <div className="text-center p-6 bg-white rounded-lg shadow-lg">
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      Select a Business
                    </h3>
                    <p className="text-sm text-gray-500">
                      Choose a business from the dropdown above to view real analytics data.
                    </p>
                  </div>
                </div>
              </div>
            ) : isLoading ? (
              <div className="text-center py-12">
                <div className="spinner">Loading...</div>
              </div>
            ) : analyticsData ? (
              <MessageStatusMetrics
                metrics={analyticsData.message_metrics}
                hourlyStats={analyticsData.hourly_stats}
                optOutTrends={analyticsData.opt_out_trends}
                errorDistribution={analyticsData.error_distribution}
              />
            ) : null}
          </Tab.Panel>
          <Tab.Panel>
            <div className="text-center py-12 bg-white rounded-lg">
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                AI Performance Analytics
              </h3>
              <p className="text-sm text-gray-500">
                Coming soon! This section will show AI response quality, sentiment analysis, and performance metrics.
              </p>
            </div>
          </Tab.Panel>
          <Tab.Panel>
            <div className="text-center py-12 bg-white rounded-lg">
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Cost Analysis
              </h3>
              <p className="text-sm text-gray-500">
                Coming soon! This section will show detailed cost breakdowns for SMS and AI usage.
              </p>
            </div>
          </Tab.Panel>
        </Tab.Panels>
      </Tab.Group>
    </div>
  );
}
