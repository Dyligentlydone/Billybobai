import React from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, BarChart, Bar } from 'recharts';

interface Props {
  isPlaceholder?: boolean;
}

const EmailAnalytics: React.FC<Props> = ({ isPlaceholder = false }) => {
  // Sample data for development
  const placeholderData = {
    emailMetrics: {
      totalEmails: 2500,
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
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm text-gray-500">Total Emails</h3>
          <p className="mt-1 text-2xl font-semibold">{placeholderData.emailMetrics.totalEmails}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm text-gray-500">Open Rate</h3>
          <p className="mt-1 text-2xl font-semibold">
            {(placeholderData.emailMetrics.openRate * 100).toFixed(1)}%
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm text-gray-500">Click Rate</h3>
          <p className="mt-1 text-2xl font-semibold">
            {(placeholderData.emailMetrics.clickRate * 100).toFixed(1)}%
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm text-gray-500">Bounce Rate</h3>
          <p className="mt-1 text-2xl font-semibold">
            {(placeholderData.emailMetrics.bounceRate * 100).toFixed(1)}%
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {renderDailyMetrics()}
        {renderTemplatePerformance()}
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

export default EmailAnalytics;
