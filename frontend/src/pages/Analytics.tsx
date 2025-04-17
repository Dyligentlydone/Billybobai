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

  const { data: analyticsData, isLoading, error } = useQuery(
    ['analytics', selectedBusinessId],
    async () => {
      if (!selectedBusinessId) return null;
      const response = await axios.get(`/api/analytics/${selectedBusinessId}`, {
        params: {
          start_date: start.toISOString(),
          end_date: end.toISOString()
        }
      });
      return response.data;
    },
    {
      enabled: !!selectedBusinessId,
      staleTime: 5 * 60 * 1000 // Consider data fresh for 5 minutes
    }
  );

  if (error) {
    return (
      <div className="p-4">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          Error loading analytics data
        </div>
      </div>
    );
  }

  if (isLoading) {
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
            <OverviewAnalytics
              metrics={{
                overview: {
                  totalInteractions: '0',
                  totalCost: 0,
                  averageResponseTime: '0s',
                  successRate: 0
                },
                sms: {
                  totalCount: '0',
                  responseTime: '0s',
                  deliveryRate: 0,
                  optOutRate: 0,
                  aiCost: 0,
                  serviceCost: 0,
                  qualityMetrics: [],
                  responseTypes: [],
                  dailyCosts: [],
                  hourlyActivity: [],
                  conversations: []
                },
                voice: {
                  totalCount: '0',
                  inboundCalls: 0,
                  outboundCalls: 0,
                  averageDuration: 0,
                  successRate: 0,
                  hourlyActivity: []
                },
                email: {
                  totalCount: '0',
                  responseTime: '0s',
                  openRate: 0,
                  clickRate: 0,
                  bounceRate: 0,
                  hourlyActivity: []
                },
                dateRange: {
                  start: start.toISOString(),
                  end: end.toISOString()
                }
              }}
              businessId={selectedBusinessId || ''}
              clientId={selectedBusinessId || ''}
            />
          </Tab.Panel>
          <Tab.Panel>
            <SMSAnalytics
              metrics={{
                totalCount: '0',
                responseTime: '0s',
                deliveryRate: 0,
                optOutRate: 0,
                aiCost: 0,
                serviceCost: 0,
                qualityMetrics: [],
                responseTypes: [],
                dailyCosts: [],
                hourlyActivity: [],
                conversations: []
              }}
              businessId={selectedBusinessId || ''}
              clientId={selectedBusinessId || ''}
            />
          </Tab.Panel>
          <Tab.Panel>
            <VoiceAnalytics
              metrics={{
                totalCount: '0',
                inboundCalls: 0,
                outboundCalls: 0,
                averageDuration: 0,
                successRate: 0,
                hourlyActivity: []
              }}
              businessId={selectedBusinessId || ''}
              clientId={selectedBusinessId || ''}
            />
          </Tab.Panel>
          <Tab.Panel>
            <EmailAnalytics
              metrics={{
                totalCount: '0',
                responseTime: '0s',
                openRate: 0,
                clickRate: 0,
                bounceRate: 0,
                hourlyActivity: []
              }}
              businessId={selectedBusinessId || ''}
              clientId={selectedBusinessId || ''}
            />
          </Tab.Panel>
        </Tab.Panels>
      </Tab.Group>
    </div>
  );
}
