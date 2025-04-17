import React from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, PieChart, Pie, Cell } from 'recharts';
import { AnalyticsData } from '../../types/analytics';

interface Props {
  metrics: AnalyticsData;
  businessId: string;
  clientId: string;
  isPlaceholder?: boolean;
}

const OverviewAnalytics: React.FC<Props> = ({ metrics, businessId, clientId, isPlaceholder = false }) => {
  // Sample data for development
  const placeholderData = {
    totalMetrics: {
      totalInteractions: 5000,
      activeChannels: 3,
      avgResponseTime: '2.5s',
      totalCost: '$1,250.00'
    },
    channelDistribution: [
      { name: 'SMS', value: 60 },
      { name: 'Voice', value: 25 },
      { name: 'Email', value: 15 }
    ],
    weeklyTrends: Array.from({ length: 7 }, (_, i) => ({
      date: `Day ${i + 1}`,
      sms: Math.floor(Math.random() * 100),
      voice: Math.floor(Math.random() * 50),
      email: Math.floor(Math.random() * 75)
    }))
  };

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28'];

  const renderChannelDistribution = () => (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-medium mb-4">Channel Distribution</h3>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={placeholderData.channelDistribution}
            cx="50%"
            cy="50%"
            labelLine={false}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
          >
            {placeholderData.channelDistribution.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );

  const renderWeeklyTrends = () => (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-medium mb-4">Weekly Channel Activity</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={placeholderData.weeklyTrends}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="sms" stroke="#0088FE" name="SMS" />
          <Line type="monotone" dataKey="voice" stroke="#00C49F" name="Voice" />
          <Line type="monotone" dataKey="email" stroke="#FFBB28" name="Email" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm text-gray-500">Total Interactions</h3>
          <p className="mt-1 text-2xl font-semibold">{placeholderData.totalMetrics.totalInteractions}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm text-gray-500">Active Channels</h3>
          <p className="mt-1 text-2xl font-semibold">{placeholderData.totalMetrics.activeChannels}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm text-gray-500">Avg Response Time</h3>
          <p className="mt-1 text-2xl font-semibold">{placeholderData.totalMetrics.avgResponseTime}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm text-gray-500">Total Cost</h3>
          <p className="mt-1 text-2xl font-semibold">{placeholderData.totalMetrics.totalCost}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {renderChannelDistribution()}
        {renderWeeklyTrends()}
      </div>

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

export default OverviewAnalytics;
