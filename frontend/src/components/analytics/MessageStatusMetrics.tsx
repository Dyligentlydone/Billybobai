import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line
} from 'recharts';

interface MessageMetrics {
  total_messages: number;
  delivered_count: number;
  failed_count: number;
  retried_count: number;
  avg_retries: number;
  opt_out_count: number;
  avg_delivery_time: number;
}

interface HourlyStats {
  [hour: string]: {
    [status: string]: number;
  };
}

interface OptOutTrend {
  date: string;
  count: number;
}

interface ErrorDistribution {
  error_code: string;
  count: number;
}

interface Props {
  metrics?: MessageMetrics;
  hourlyStats?: HourlyStats;
  optOutTrends?: OptOutTrend[];
  errorDistribution?: ErrorDistribution[];
  isPlaceholder?: boolean;
}

// Generate placeholder data
const generatePlaceholderData = () => {
  // Generate 24 hours of empty data
  const hourlyData = Array.from({ length: 24 }, (_, i) => ({
    hour: `${String(i).padStart(2, '0')}:00`,
    delivered: 0,
    failed: 0,
    retried: 0
  }));

  // Generate 30 days of empty opt-out data
  const optOutData = Array.from({ length: 30 }, (_, i) => {
    const date = new Date();
    date.setDate(date.getDate() - i);
    return {
      date: date.toISOString().split('T')[0],
      count: 0
    };
  }).reverse();

  // Generate empty error distribution
  const errorData = [
    { error_code: 'No Data', count: 0 },
    { error_code: 'Select Business', count: 0 },
  ];

  return { hourlyData, optOutData, errorData };
};

export default function MessageStatusMetrics({
  metrics,
  hourlyStats,
  optOutTrends,
  errorDistribution,
  isPlaceholder = false
}: Props) {
  const placeholder = generatePlaceholderData();
  
  // Use real data or placeholder data
  const hourlyData = isPlaceholder ? placeholder.hourlyData : 
    Object.entries(hourlyStats || {}).map(([hour, stats]) => ({
      hour: `${hour}:00`,
      delivered: stats.delivered || 0,
      failed: stats.failed || 0,
      retried: stats.retried || 0
    }));

  // Calculate rates using real or placeholder metrics
  const defaultMetrics = {
    total_messages: 0,
    delivered_count: 0,
    failed_count: 0,
    retried_count: 0,
    avg_retries: 0,
    opt_out_count: 0,
    avg_delivery_time: 0
  };
  
  const currentMetrics = metrics || defaultMetrics;
  const deliveryRate = (currentMetrics.delivered_count / (currentMetrics.total_messages || 1)) * 100;
  const retryRate = (currentMetrics.retried_count / (currentMetrics.total_messages || 1)) * 100;
  const optOutRate = (currentMetrics.opt_out_count / (currentMetrics.total_messages || 1)) * 100;

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <dt className="text-sm font-medium text-gray-500 truncate">Delivery Rate</dt>
            <dd className="mt-1 text-3xl font-semibold text-gray-900">
              {isPlaceholder ? '0.0%' : `${deliveryRate.toFixed(1)}%`}
            </dd>
          </div>
        </div>
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <dt className="text-sm font-medium text-gray-500 truncate">Retry Rate</dt>
            <dd className="mt-1 text-3xl font-semibold text-gray-900">
              {isPlaceholder ? '0.0%' : `${retryRate.toFixed(1)}%`}
            </dd>
          </div>
        </div>
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <dt className="text-sm font-medium text-gray-500 truncate">Opt-out Rate</dt>
            <dd className="mt-1 text-3xl font-semibold text-gray-900">
              {isPlaceholder ? '0.0%' : `${optOutRate.toFixed(1)}%`}
            </dd>
          </div>
        </div>
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <dt className="text-sm font-medium text-gray-500 truncate">Avg. Delivery Time</dt>
            <dd className="mt-1 text-3xl font-semibold text-gray-900">
              {isPlaceholder ? '0.0s' : `${currentMetrics.avg_delivery_time.toFixed(1)}s`}
            </dd>
          </div>
        </div>
      </div>

      {/* Hourly Message Volume */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900">Message Volume by Hour</h3>
        <div className="mt-5 h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={hourlyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hour" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="delivered" fill="#10B981" name="Delivered" />
              <Bar dataKey="failed" fill="#EF4444" name="Failed" />
              <Bar dataKey="retried" fill="#F59E0B" name="Retried" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Opt-out Trends */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900">Opt-out Trends</h3>
        <div className="mt-5 h-72">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={isPlaceholder ? placeholder.optOutData : optOutTrends}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="count" stroke="#6366F1" name="Opt-outs" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Error Distribution */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900">Top Error Codes</h3>
        <div className="mt-5 h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart 
              data={isPlaceholder ? placeholder.errorData : errorDistribution} 
              layout="vertical"
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="error_code" type="category" />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" fill="#EF4444" name="Occurrences" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
