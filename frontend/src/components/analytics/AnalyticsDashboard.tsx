import { useState } from 'react';
import { useQuery } from 'react-query';
import axios from 'axios';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { format, subDays } from 'date-fns';

interface AnalyticsDashboardProps {
  clientId: string;
}

export default function AnalyticsDashboard({ clientId }: AnalyticsDashboardProps) {
  const [dateRange, setDateRange] = useState<number>(7); // days

  const { data: analytics, isLoading } = useQuery(
    ['analytics', clientId, dateRange],
    async () => {
      const startDate = format(subDays(new Date(), dateRange), 'yyyy-MM-dd');
      const endDate = format(new Date(), 'yyyy-MM-dd');
      
      const { data } = await axios.get(`/api/analytics`, {
        params: {
          clientId,
          startDate,
          endDate
        }
      });
      return data;
    },
    {
      refetchInterval: 300000 // Refresh every 5 minutes
    }
  );

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8 p-6">
      {/* Date range selector */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h2>
        <select
          value={dateRange}
          onChange={(e) => setDateRange(Number(e.target.value))}
          className="rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        >
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
        </select>
      </div>

      {/* SMS Automation Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <MetricCard
          title="Total Messages"
          value={analytics?.sms.totalMessages || 0}
          change={analytics?.sms.messageChange || 0}
          icon="💬"
        />
        <MetricCard
          title="Response Time"
          value={analytics?.sms.avgResponseTime || 0}
          change={analytics?.sms.responseTimeChange || 0}
          icon="⚡"
          unit="sec"
        />
        <MetricCard
          title="AI Cost"
          value={analytics?.sms.aiCost || 0}
          change={analytics?.sms.aiCostChange || 0}
          icon="🤖"
          unit="$"
        />
        <MetricCard
          title="SMS Cost"
          value={analytics?.sms.smsCost || 0}
          change={analytics?.sms.smsCostChange || 0}
          icon="📱"
          unit="$"
        />
      </div>

      {/* Message Quality Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Message Quality</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={analytics?.sms.qualityMetrics || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="sentiment"
                  stroke="#3B82F6"
                  name="Sentiment"
                />
                <Line
                  type="monotone"
                  dataKey="quality"
                  stroke="#10B981"
                  name="Quality"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Response Distribution</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={analytics?.sms.responseTypes || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="type" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" fill="#3B82F6" name="Count" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Cost Analysis */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Daily Cost Breakdown</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={analytics?.sms.dailyCosts || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="ai"
                stroke="#3B82F6"
                name="AI Cost"
              />
              <Line
                type="monotone"
                dataKey="sms"
                stroke="#10B981"
                name="SMS Cost"
              />
              <Line
                type="monotone"
                dataKey="total"
                stroke="#6366F1"
                name="Total Cost"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

interface MetricCardProps {
  title: string;
  value: number;
  change: number;
  icon: string;
  unit?: string;
}

function MetricCard({ title, value, change, icon, unit }: MetricCardProps) {
  const formatValue = (val: number) => {
    if (unit === 'sec') return `${val.toFixed(2)}s`;
    if (unit === '$') return `$${val.toFixed(2)}`;
    return val.toLocaleString();
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <div className="flex items-center">
        <span className="text-2xl mr-2">{icon}</span>
        <h3 className="text-lg font-semibold">{title}</h3>
      </div>
      <p className="text-3xl font-bold mt-2">{formatValue(value)}</p>
      <div className={`flex items-center mt-2 ${change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
        <span>{change >= 0 ? '↑' : '↓'}</span>
        <span className="ml-1">{Math.abs(change)}% vs previous period</span>
      </div>
    </div>
  );
}
