import React from 'react';
import { useQuery } from 'react-query';
import axios from 'axios';
import { useBusiness } from '../contexts/BusinessContext';
import BusinessSelector from '../components/business/BusinessSelector';
import { useAnalytics } from '../hooks/useAnalytics';
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

  // Use new analytics hook for metrics
  const {
    analytics,
    isLoading: analyticsLoading,
    isError: analyticsError,
  } = useAnalytics(selectedBusinessId || '');

  // Fetch business list for selector (using new endpoint)
  const { data: businessList } = useQuery(['businesses'], async () => {
    const res = await axios.get('/api/businesses');
    return res.data;
  });

  if (analyticsError) {
    return (
      <div className="p-4">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          Error loading analytics data
        </div>
      </div>
    );
  }

  if (analyticsLoading) {
    return (
      <div className="p-4">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-24 bg-gray-200 rounded"></div>
            ))}
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {[...Array(2)].map((_, i) => (
              <div key={i} className="h-80 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="sm:flex sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Analytics</h1>
          <p className="mt-2 text-sm text-gray-700">
            View analytics and insights for your business communications
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
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
        <Tab.Panels>
          <Tab.Panel>
            {analytics && (
              <OverviewAnalytics
                metrics={analytics}
                businessId={selectedBusinessId || ''}
                clientId={selectedBusinessId || ''}
              />
            )}
          </Tab.Panel>
          <Tab.Panel>
            {analytics && (
              <SMSAnalytics
                metrics={analytics.sms}
                businessId={selectedBusinessId || ''}
                clientId={selectedBusinessId || ''}
              />
            )}
          </Tab.Panel>
          <Tab.Panel>
            {analytics && (
              <VoiceAnalytics
                metrics={analytics.voice}
                businessId={selectedBusinessId || ''}
                clientId={selectedBusinessId || ''}
              />
            )}
          </Tab.Panel>
          <Tab.Panel>
            {analytics && (
              <EmailAnalytics
                metrics={analytics.email}
                businessId={selectedBusinessId || ''}
                clientId={selectedBusinessId || ''}
              />
            )}
          </Tab.Panel>
        </Tab.Panels>
      </Tab.Group>
    </div>
  );
}
