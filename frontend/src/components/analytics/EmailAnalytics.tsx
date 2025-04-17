import React from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, BarChart, Bar, PieChart, Pie, Legend, Cell } from 'recharts';
import { EmailMetrics } from '../../types/analytics';

interface Props {
  metrics: EmailMetrics;
  businessId: string;
  clientId: string;
  isPlaceholder?: boolean;
}

const EmailAnalytics: React.FC<Props> = ({ metrics, businessId, clientId, isPlaceholder = false }) => {
  // Sample data for development
  const displayData = isPlaceholder ? {
    totalCount: 1234,
    openRate: 0.65,
    clickRate: 0.32,
    bounceRate: 0.02
  } : metrics;

  const placeholderData = {
    emailMetrics: {
      totalCount: 2500,
      openRate: 0.68,
      clickRate: 0.15,
      bounceRate: 0.02
    },
    dailyMetrics: Array.from({ length: 7 }, (_, i) => ({
      date: `Day ${i + 1}`,
      sent: Math.floor(Math.random() * 500),
      opened: Math.floor(Math.random() * 300),
      clicked: Math.floor(Math.random() * 100)
    })),
    templatePerformance: Array.from({ length: 5 }, (_, i) => ({
      template: `Template ${i + 1}`,
      openRate: 0.5 + Math.random() * 0.3,
      clickRate: 0.1 + Math.random() * 0.2
    }))
  };

  const renderDailyMetrics = () => (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-medium mb-4">Daily Email Performance</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={placeholderData.dailyMetrics}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="sent" stroke="#8884d8" name="Sent" />
          <Line type="monotone" dataKey="opened" stroke="#82ca9d" name="Opened" />
          <Line type="monotone" dataKey="clicked" stroke="#ffc658" name="Clicked" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );

  const renderTemplatePerformance = () => (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-medium mb-4">Template Performance</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={placeholderData.templatePerformance}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="template" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="openRate" fill="#8884d8" name="Open Rate" />
          <Bar dataKey="clickRate" fill="#82ca9d" name="Click Rate" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm font-medium text-gray-500">Total Emails</h3>
          <p className="mt-2 text-3xl font-semibold text-gray-900">{displayData.totalCount}</p>
          {!businessId && <p className="mt-1 text-sm text-gray-500">No business selected</p>}
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm font-medium text-gray-500">Open Rate</h3>
          <p className="mt-2 text-3xl font-semibold text-gray-900">{(displayData.openRate * 100).toFixed(1)}%</p>
          {!businessId && <p className="mt-1 text-sm text-gray-500">No business selected</p>}
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm font-medium text-gray-500">Click Rate</h3>
          <p className="mt-2 text-3xl font-semibold text-gray-900">{(displayData.clickRate * 100).toFixed(1)}%</p>
          {!businessId && <p className="mt-1 text-sm text-gray-500">No business selected</p>}
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm font-medium text-gray-500">Bounce Rate</h3>
          <p className="mt-2 text-3xl font-semibold text-gray-900">{(displayData.bounceRate * 100).toFixed(1)}%</p>
          {!businessId && <p className="mt-1 text-sm text-gray-500">No business selected</p>}
        </div>
      </div>

      {/* Email Volume */}
      <div className="bg-white rounded-lg shadow p-4">
        <h3 className="text-lg font-medium mb-4">Email Volume</h3>
        {metrics.hourlyActivity.length > 0 ? (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={metrics.hourlyActivity}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="hour" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="count" stroke="#3B82F6" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="h-64 flex items-center justify-center">
            <p className="text-gray-500">No email volume data available{!businessId && " - Select a business to view data"}</p>
          </div>
        )}
      </div>

      {/* Engagement Metrics */}
      <div className="bg-white rounded-lg shadow p-4">
        <h3 className="text-lg font-medium mb-4">Engagement Metrics</h3>
        {metrics.hourlyActivity.length > 0 ? (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={metrics.hourlyActivity}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="hour" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="opens" stroke="#3B82F6" name="Opens" />
                <Line type="monotone" dataKey="clicks" stroke="#10B981" name="Clicks" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="h-64 flex items-center justify-center">
            <p className="text-gray-500">No engagement data available{!businessId && " - Select a business to view data"}</p>
          </div>
        )}
      </div>

      {/* Delivery Status */}
      <div className="bg-white rounded-lg shadow p-4">
        <h3 className="text-lg font-medium mb-4">Delivery Status</h3>
        {metrics.hourlyActivity.length > 0 ? (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={[
                    { name: 'Delivered', value: Number(metrics.totalCount) * (1 - metrics.bounceRate) },
                    { name: 'Bounced', value: Number(metrics.totalCount) * metrics.bounceRate }
                  ]}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  fill="#3B82F6"
                  dataKey="value"
                  label
                >
                  <Cell fill="#3B82F6" />
                  <Cell fill="#EF4444" />
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="h-64 flex items-center justify-center">
            <p className="text-gray-500">No delivery status data available{!businessId && " - Select a business to view data"}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default EmailAnalytics;
