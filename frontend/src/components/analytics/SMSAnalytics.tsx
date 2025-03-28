import React, { useState } from 'react';
import { Switch } from '@headlessui/react';
import { SMSMetrics } from '../../types/analytics';
import { SMSConversations } from '../conversations/SMSConversations';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { Tab } from '@headlessui/react';

interface Props {
  metrics: SMSMetrics;
  businessId: string;
}

function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(' ');
}

const SMSAnalytics: React.FC<Props> = ({ metrics, businessId }) => {
  const [enabledCategories, setEnabledCategories] = useState<Record<string, boolean>>({
    delivery_metrics: true,
    engagement_metrics: false,
    quality_compliance: true,
    cost_efficiency: true,
    performance_metrics: true,
    business_impact: true,
    ai_specific: true,
    security_fraud: true
  });

  const categoryLabels: Record<string, string> = {
    delivery_metrics: 'Delivery Metrics',
    engagement_metrics: 'Engagement Metrics',
    quality_compliance: 'Quality & Compliance',
    cost_efficiency: 'Cost & Efficiency',
    performance_metrics: 'Performance Metrics',
    business_impact: 'Business Impact',
    ai_specific: 'AI Metrics',
    security_fraud: 'Security & Fraud'
  };

  const toggleCategory = (category: string) => {
    setEnabledCategories(prev => ({
      ...prev,
      [category]: !prev[category]
    }));
  };

  const renderMetricToggles = () => (
    <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Metric Categories</h3>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {Object.entries(categoryLabels).map(([key, label]) => (
          <div key={key} className="flex items-center justify-between bg-gray-50 p-3 rounded-lg">
            <span className="text-sm font-medium text-gray-700">{label}</span>
            <Switch
              checked={enabledCategories[key]}
              onChange={() => toggleCategory(key)}
              className={`${
                enabledCategories[key] ? 'bg-indigo-600' : 'bg-gray-200'
              } relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none`}
            >
              <span className="sr-only">Toggle {label}</span>
              <span
                className={`${
                  enabledCategories[key] ? 'translate-x-6' : 'translate-x-1'
                } inline-block h-4 w-4 transform rounded-full bg-white transition-transform`}
              />
            </Switch>
          </div>
        ))}
      </div>
    </div>
  );

  const renderMetricCard = (label: string, value: string | number) => (
    <div className="bg-white rounded-lg shadow p-4">
      <h4 className="text-sm text-gray-500">{label}</h4>
      <div className="mt-1 text-xl font-semibold">{value}</div>
    </div>
  );

  const renderChart = (category: string, chart: { type: string; data: any[] }) => {
    if (chart.type === 'line') {
      return (
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={chart.data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="value" stroke="#4F46E5" name={category} />
          </LineChart>
        </ResponsiveContainer>
      );
    }
    return (
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={chart.data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="value" fill="#4F46E5" name={category} />
        </BarChart>
      </ResponsiveContainer>
    );
  };

  const renderMetricCategory = (categoryKey: string) => {
    const category = metrics[categoryKey as keyof SMSMetrics];
    if (!category || !enabledCategories[categoryKey]) return null;

    return (
      <div key={categoryKey} className="bg-white rounded-lg shadow-sm p-6 mb-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">{categoryLabels[categoryKey]}</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
          {Object.entries(category.metrics).map(([key, value]) => (
            renderMetricCard(key, value)
          ))}
        </div>
        {category.charts && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            {category.charts.map((chart, index) => (
              <div key={index} className="bg-gray-50 p-4 rounded-lg">
                {renderChart(categoryKey, chart)}
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  const renderMetrics = () => (
    <div className="space-y-6">
      {renderMetricToggles()}
      {Object.keys(categoryLabels).map(category => renderMetricCategory(category))}
    </div>
  );

  return (
    <div className="w-full">
      <Tab.Group>
        <Tab.List className="flex space-x-1 rounded-xl bg-blue-900/20 p-1 mb-6">
          {['Metrics', 'Conversations'].map((tab) => (
            <Tab
              key={tab}
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
              {tab}
            </Tab>
          ))}
        </Tab.List>
        <Tab.Panels>
          <Tab.Panel
            className={classNames(
              'rounded-xl bg-white p-3',
              'ring-white ring-opacity-60 ring-offset-2 ring-offset-blue-400 focus:outline-none focus:ring-2'
            )}
          >
            {renderMetrics()}
          </Tab.Panel>
          <Tab.Panel
            className={classNames(
              'rounded-xl bg-white p-3',
              'ring-white ring-opacity-60 ring-offset-2 ring-offset-blue-400 focus:outline-none focus:ring-2'
            )}
          >
            <SMSConversations businessId={businessId} />
          </Tab.Panel>
        </Tab.Panels>
      </Tab.Group>
    </div>
  );
};

export default SMSAnalytics;
