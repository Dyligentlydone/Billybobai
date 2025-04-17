import React from 'react';
import { useQuery } from 'react-query';
import axios from 'axios';
import { useBusiness } from '../contexts/BusinessContext';
import BusinessSelector from '../components/business/BusinessSelector';
import { Tab } from '@headlessui/react';
import SMSAnalytics from '../components/analytics/SMSAnalytics';
import VoiceAnalytics from '../components/analytics/VoiceAnalytics';
import EmailAnalytics from '../components/analytics/EmailAnalytics';
import OverviewAnalytics from '../components/analytics/OverviewAnalytics';

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
            Detailed analytics and insights across all communication channels.
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
            Overview
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
            SMS
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
            Voice
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
            Email
          </Tab>
        </Tab.List>
        <Tab.Panels className="mt-2">
          <Tab.Panel>
            {isLoading ? (
              <div className="text-center py-12">
                <div className="spinner">Loading...</div>
              </div>
            ) : (
              <OverviewAnalytics isPlaceholder={!selectedBusinessId} />
            )}
          </Tab.Panel>
          <Tab.Panel>
            {isLoading ? (
              <div className="text-center py-12">
                <div className="spinner">Loading...</div>
              </div>
            ) : (
              <SMSAnalytics
                metrics={analyticsData?.message_metrics || {}}
                businessId={selectedBusinessId || ''}
                clientId={selectedBusinessId || ''}
                isPlaceholder={!selectedBusinessId}
              />
            )}
          </Tab.Panel>
          <Tab.Panel>
            {isLoading ? (
              <div className="text-center py-12">
                <div className="spinner">Loading...</div>
              </div>
            ) : (
              <VoiceAnalytics isPlaceholder={!selectedBusinessId} />
            )}
          </Tab.Panel>
          <Tab.Panel>
            {isLoading ? (
              <div className="text-center py-12">
                <div className="spinner">Loading...</div>
              </div>
            ) : (
              <EmailAnalytics isPlaceholder={!selectedBusinessId} />
            )}
          </Tab.Panel>
        </Tab.Panels>
      </Tab.Group>
    </div>
  );
}
