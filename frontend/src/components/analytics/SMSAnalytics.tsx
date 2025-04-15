import React from 'react';
import { SMSMetrics } from '../../types/analytics';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';

interface Props {
  metrics: SMSMetrics;
  businessId: string;
  clientId: string;
}

const SMSAnalytics: React.FC<Props> = ({ metrics, businessId, clientId }) => {
  const renderQualityMetrics = () => (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-medium mb-4">Quality Metrics</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={metrics.qualityMetrics}>
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
        <BarChart data={metrics.responseTypes}>
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
        <LineChart data={metrics.dailyCosts}>
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
          <p className="mt-1 text-2xl font-semibold">{metrics.totalCount}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm text-gray-500">Response Time</h3>
          <p className="mt-1 text-2xl font-semibold">{metrics.responseTime}s</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm text-gray-500">Delivery Rate</h3>
          <p className="mt-1 text-2xl font-semibold">{(metrics.deliveryRate * 100).toFixed(1)}%</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm text-gray-500">Opt-out Rate</h3>
          <p className="mt-1 text-2xl font-semibold">{(metrics.optOutRate * 100).toFixed(1)}%</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {renderQualityMetrics()}
        {renderResponseTypes()}
      </div>

      {renderCostMetrics()}
    </div>
  );
};

export default SMSAnalytics;
