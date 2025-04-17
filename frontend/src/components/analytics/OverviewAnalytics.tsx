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
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28'];

  const getChannelDistribution = () => {
    const total = Number(metrics.sms.totalCount) + Number(metrics.voice.totalCount) + Number(metrics.email.totalCount);
    if (total === 0) return [];
    
    return [
      { name: 'SMS', value: Number(metrics.sms.totalCount) },
      { name: 'Voice', value: Number(metrics.voice.totalCount) },
      { name: 'Email', value: Number(metrics.email.totalCount) }
    ];
  };

  const renderChannelDistribution = () => (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-medium mb-4">Channel Distribution</h3>
      {getChannelDistribution().length > 0 ? (
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={getChannelDistribution()}
              cx="50%"
              cy="50%"
              labelLine={false}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
            >
              {getChannelDistribution().map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      ) : (
        <div className="h-64 flex items-center justify-center">
          <p className="text-gray-500">No distribution data available{!businessId && " - Select a business to view data"}</p>
        </div>
      )}
    </div>
  );

  const renderWeeklyTrends = () => (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-medium mb-4">Channel Activity</h3>
      {metrics.sms.hourlyActivity.length > 0 ? (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="hour" />
            <YAxis />
            <Tooltip />
            <Line 
              data={metrics.sms.hourlyActivity} 
              type="monotone" 
              dataKey="count" 
              stroke="#0088FE" 
              name="SMS" 
            />
            <Line 
              data={metrics.voice.hourlyActivity} 
              type="monotone" 
              dataKey="count" 
              stroke="#00C49F" 
              name="Voice" 
            />
            <Line 
              data={metrics.email.hourlyActivity} 
              type="monotone" 
              dataKey="count" 
              stroke="#FFBB28" 
              name="Email" 
            />
          </LineChart>
        </ResponsiveContainer>
      ) : (
        <div className="h-64 flex items-center justify-center">
          <p className="text-gray-500">No activity data available{!businessId && " - Select a business to view data"}</p>
        </div>
      )}
    </div>
  );

  const getActiveChannels = () => {
    let count = 0;
    if (Number(metrics.sms.totalCount) > 0) count++;
    if (Number(metrics.voice.totalCount) > 0) count++;
    if (Number(metrics.email.totalCount) > 0) count++;
    return count;
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm text-gray-500">Total Interactions</h3>
          <p className="mt-1 text-2xl font-semibold">{metrics.overview.totalInteractions}</p>
          {!businessId && <p className="mt-1 text-sm text-gray-500">No business selected</p>}
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm text-gray-500">Active Channels</h3>
          <p className="mt-1 text-2xl font-semibold">{getActiveChannels()}</p>
          {!businessId && <p className="mt-1 text-sm text-gray-500">No business selected</p>}
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm text-gray-500">Avg Response Time</h3>
          <p className="mt-1 text-2xl font-semibold">{metrics.overview.averageResponseTime}</p>
          {!businessId && <p className="mt-1 text-sm text-gray-500">No business selected</p>}
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm text-gray-500">Total Cost</h3>
          <p className="mt-1 text-2xl font-semibold">${metrics.overview.totalCost.toFixed(2)}</p>
          {!businessId && <p className="mt-1 text-sm text-gray-500">No business selected</p>}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {renderChannelDistribution()}
        {renderWeeklyTrends()}
      </div>
    </div>
  );
};

export default OverviewAnalytics;
