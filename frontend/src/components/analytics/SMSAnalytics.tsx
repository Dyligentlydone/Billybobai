import React from 'react';
import { SMSMetrics } from '../../types/analytics';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';

interface Props {
  metrics: SMSMetrics;
  businessId: string;
  clientId: string;
  isPlaceholder?: boolean;
}

const SMSAnalytics: React.FC<Props> = ({ metrics, businessId, clientId, isPlaceholder }) => {
  // Sample data for placeholder state
  const placeholderData = {
    qualityMetrics: Array.from({ length: 7 }, (_, i) => ({
      date: `Day ${i + 1}`,
      sentiment: 0.7 + Math.random() * 0.2,
      quality: 0.8 + Math.random() * 0.15
    })),
    responseTypes: [
      { type: 'Quick Reply', count: 45 },
      { type: 'Custom', count: 30 },
      { type: 'Automated', count: 25 }
    ],
    dailyCosts: Array.from({ length: 7 }, (_, i) => ({
      date: `Day ${i + 1}`,
      ai: Math.random() * 50,
      service: Math.random() * 30,
      total: Math.random() * 80
    }))
  };

  const displayData = isPlaceholder ? {
    totalCount: '1,234',
    responseTime: '2.5',
    deliveryRate: 0.98,
    optOutRate: 0.02,
    qualityMetrics: placeholderData.qualityMetrics,
    responseTypes: placeholderData.responseTypes,
    dailyCosts: placeholderData.dailyCosts
  } : metrics;

  const renderQualityMetrics = () => (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-medium mb-4">Quality Metrics</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={displayData.qualityMetrics}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="sentiment" stroke="#8884d8" name="Sentiment" />
          <Line type="monotone" dataKey="quality" stroke="#82ca9d" name="Quality" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );

  const renderResponseTypes = () => (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-medium mb-4">Response Types</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={displayData.responseTypes}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="type" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="count" fill="#8884d8" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );

  const renderCostMetrics = () => (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-medium mb-4">Daily Costs</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={displayData.dailyCosts}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="ai" stroke="#8884d8" name="AI Cost" />
          <Line type="monotone" dataKey="service" stroke="#82ca9d" name="Service Cost" />
          <Line type="monotone" dataKey="total" stroke="#ffc658" name="Total Cost" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm text-gray-500">Total Messages</h3>
          <p className="mt-1 text-2xl font-semibold">{displayData.totalCount}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm text-gray-500">Response Time</h3>
          <p className="mt-1 text-2xl font-semibold">{displayData.responseTime}s</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm text-gray-500">Delivery Rate</h3>
          <p className="mt-1 text-2xl font-semibold">{(displayData.deliveryRate * 100).toFixed(1)}%</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm text-gray-500">Opt-out Rate</h3>
          <p className="mt-1 text-2xl font-semibold">{(displayData.optOutRate * 100).toFixed(1)}%</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {renderQualityMetrics()}
        {renderResponseTypes()}
      </div>

      {renderCostMetrics()}
      
      {isPlaceholder && (
        <div className="text-center mt-4">
          <p className="text-sm text-gray-500">
            ℹ️ Showing sample data. Select a business to view actual analytics.
          </p>
        </div>
      )}
    </div>
  );
};

export default SMSAnalytics;
