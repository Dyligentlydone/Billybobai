import React from 'react';
import { Tab } from '@headlessui/react';
import { AnalyticsData } from '../../types/analytics';
import { mockAnalyticsData } from '../../data/mockAnalytics';
import SMSAnalytics from './SMSAnalytics';
import { useQuery } from 'react-query';
import axios from 'axios';

function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(' ');
}

interface Props {
  clientId: string;
  data?: any;
  isLoading?: boolean;
}

const AnalyticsDashboard: React.FC<Props> = ({ clientId, data, isLoading = false }) => {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!data) return null;

  const renderOverview = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <div className="bg-white rounded-lg shadow p-4">
        <h3 className="text-sm text-gray-500">Total Interactions</h3>
        <p className="mt-1 text-2xl font-semibold">{data?.overview.totalInteractions}</p>
      </div>
      <div className="bg-white rounded-lg shadow p-4">
        <h3 className="text-sm text-gray-500">Total Cost</h3>
        <p className="mt-1 text-2xl font-semibold">${data?.overview.totalCost.toFixed(2)}</p>
      </div>
      <div className="bg-white rounded-lg shadow p-4">
        <h3 className="text-sm text-gray-500">Avg Response Time</h3>
        <p className="mt-1 text-2xl font-semibold">{data?.overview.averageResponseTime}s</p>
      </div>
      <div className="bg-white rounded-lg shadow p-4">
        <h3 className="text-sm text-gray-500">Success Rate</h3>
        <p className="mt-1 text-2xl font-semibold">{data?.overview.successRate}%</p>
      </div>
    </div>
  );

  const categories = ['SMS', 'Email', 'Voice'];

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h2>
      </div>
      {renderOverview()}
      <Tab.Group>
        <Tab.List className="flex space-x-1 rounded-xl bg-blue-900/20 p-1 mb-6">
          {categories.map((category) => (
            <Tab
              key={category}
              className={({ selected }) =>
                classNames(
                  'w-full rounded-lg py-2.5 text-sm font-medium leading-5',
                  'ring-white ring-opacity-60 ring-offset-2 ring-offset-blue-400 focus:outline-none focus:ring-2',
                  selected
                    ? 'bg-white text-blue-700 shadow'
                    : 'text-blue-100 hover:bg-white/[0.12] hover:text-white'
                )
              }
            >
              {category}
            </Tab>
          ))}
        </Tab.List>
        <Tab.Panels className="mt-2">
          <Tab.Panel
            className={classNames(
              'rounded-xl bg-white p-3',
              'ring-white ring-opacity-60 ring-offset-2 ring-offset-blue-400 focus:outline-none focus:ring-2'
            )}
          >
            <SMSAnalytics metrics={data?.sms} businessId={''} clientId={clientId} />
          </Tab.Panel>
          <Tab.Panel
            className={classNames(
              'rounded-xl bg-white p-3',
              'ring-white ring-opacity-60 ring-offset-2 ring-offset-blue-400 focus:outline-none focus:ring-2'
            )}
          >
            <div className="text-center text-gray-500 py-12">
              Email analytics coming soon...
            </div>
          </Tab.Panel>
          <Tab.Panel
            className={classNames(
              'rounded-xl bg-white p-3',
              'ring-white ring-opacity-60 ring-offset-2 ring-offset-blue-400 focus:outline-none focus:ring-2'
            )}
          >
            <div className="text-center text-gray-500 py-12">
              Voice analytics coming soon...
            </div>
          </Tab.Panel>
        </Tab.Panels>
      </Tab.Group>
    </div>
  );
};

export default AnalyticsDashboard;
