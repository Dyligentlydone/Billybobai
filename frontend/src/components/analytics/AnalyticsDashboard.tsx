import { useState } from 'react';
import { useQuery } from 'react-query';
import axios from 'axios';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { format, subDays } from 'date-fns';
import { Tab } from '@headlessui/react';
import { AnalyticsData } from '../../types/analytics';

const COLORS = ['#3B82F6', '#10B981', '#6366F1', '#F59E0B'];

interface AnalyticsDashboardProps {
  clientId: string;
  mockData?: AnalyticsData;
}

export default function AnalyticsDashboard({ clientId, mockData }: AnalyticsDashboardProps) {
  const [dateRange, setDateRange] = useState<number>(7); // days
  const [selectedTab, setSelectedTab] = useState(0);

  const { data: analytics, isLoading } = useQuery<AnalyticsData>(
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
      refetchInterval: 300000, // Refresh every 5 minutes
      enabled: !mockData && !!clientId // Only fetch if we don't have mock data and have a clientId
    }
  );

  const data = mockData || analytics;

  if (isLoading || (!data && !mockData)) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="text-center py-12 bg-gray-50 rounded-lg">
        <p className="text-gray-500">No data available</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 p-6">
      {/* Overview Section */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <MetricCard
          title="Total Interactions"
          value={data.overview.totalInteractions}
          change={0}
          icon="🔄"
        />
        <MetricCard
          title="Total Cost"
          value={data.overview.totalCost}
          change={0}
          icon="💰"
          unit="$"
        />
        <MetricCard
          title="Avg Response Time"
          value={data.overview.averageResponseTime}
          change={0}
          icon="⚡"
          unit="sec"
        />
        <MetricCard
          title="Success Rate"
          value={data.overview.successRate}
          change={0}
          icon="✅"
          unit="%"
        />
      </div>

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

      {/* Automation Type Tabs */}
      <Tab.Group selectedIndex={selectedTab} onChange={setSelectedTab}>
        <Tab.List className="flex space-x-1 rounded-xl bg-blue-900/20 p-1">
          <Tab className={({ selected }) =>
            `w-full rounded-lg py-2.5 text-sm font-medium leading-5
             ${selected 
               ? 'bg-white shadow text-blue-700'
               : 'text-blue-100 hover:bg-white/[0.12] hover:text-white'
             }`
          }>
            SMS
          </Tab>
          <Tab className={({ selected }) =>
            `w-full rounded-lg py-2.5 text-sm font-medium leading-5
             ${selected 
               ? 'bg-white shadow text-blue-700'
               : 'text-blue-100 hover:bg-white/[0.12] hover:text-white'
             }`
          }>
            Email
          </Tab>
          <Tab className={({ selected }) =>
            `w-full rounded-lg py-2.5 text-sm font-medium leading-5
             ${selected 
               ? 'bg-white shadow text-blue-700'
               : 'text-blue-100 hover:bg-white/[0.12] hover:text-white'
             }`
          }>
            Voice
          </Tab>
        </Tab.List>

        <Tab.Panels>
          {/* SMS Panel */}
          <Tab.Panel>
            <AutomationMetrics
              metrics={data.sms}
              type="SMS"
              specificMetrics={[
                { label: 'Delivery Rate', value: data.sms.deliveryRate, unit: '%' },
                { label: 'Opt-out Rate', value: data.sms.optOutRate, unit: '%' }
              ]}
            />
          </Tab.Panel>

          {/* Email Panel */}
          <Tab.Panel>
            <AutomationMetrics
              metrics={data.email}
              type="Email"
              specificMetrics={[
                { label: 'Open Rate', value: data.email.openRate, unit: '%' },
                { label: 'Click Rate', value: data.email.clickRate, unit: '%' },
                { label: 'Bounce Rate', value: data.email.bounceRate, unit: '%' },
                { label: 'Unsubscribe Rate', value: data.email.unsubscribeRate, unit: '%' }
              ]}
            />
          </Tab.Panel>

          {/* Voice Panel */}
          <Tab.Panel>
            <AutomationMetrics
              metrics={data.voice}
              type="Voice"
              specificMetrics={[
                { label: 'Avg Call Duration', value: data.voice.callDuration, unit: 'sec' },
                { label: 'Completion Rate', value: data.voice.completionRate, unit: '%' },
                { label: 'Transfer Rate', value: data.voice.transferRate, unit: '%' },
                { label: 'Voicemail Rate', value: data.voice.voicemailRate, unit: '%' }
              ]}
            />
          </Tab.Panel>
        </Tab.Panels>
      </Tab.Group>
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
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center">
        <div className="text-2xl mr-2">{icon}</div>
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-semibold text-gray-900">
            {value.toLocaleString()}{unit ? ` ${unit}` : ''}
          </p>
        </div>
      </div>
      <div className={`mt-2 flex items-center text-sm ${
        change >= 0 ? 'text-green-600' : 'text-red-600'
      }`}>
        {change >= 0 ? '↑' : '↓'} {Math.abs(change)}%
      </div>
    </div>
  );
}

interface AutomationMetricsProps {
  metrics: any;
  type: 'SMS' | 'Email' | 'Voice';
  specificMetrics: Array<{
    label: string;
    value: number;
    unit: string;
  }>;
}

function AutomationMetrics({ metrics, type, specificMetrics }: AutomationMetricsProps) {
  return (
    <div className="space-y-6 mt-6">
      {/* Type-specific metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        {specificMetrics.map((metric, index) => (
          <div key={index} className="bg-white rounded-lg shadow p-4">
            <h3 className="text-sm font-medium text-gray-600">{metric.label}</h3>
            <p className="text-xl font-semibold text-gray-900">
              {metric.value.toLocaleString()}{metric.unit}
            </p>
          </div>
        ))}
      </div>

      {/* Quality Metrics Chart */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Quality Metrics</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={metrics.qualityMetrics}>
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

      {/* Response Types */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Response Distribution</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={metrics.responseTypes}
                  dataKey="count"
                  nameKey="type"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label
                >
                  {metrics.responseTypes.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Cost Analysis */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Cost Breakdown</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={metrics.dailyCosts}>
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
                  dataKey="service"
                  stroke="#10B981"
                  name={`${type} Cost`}
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
    </div>
  );
}
