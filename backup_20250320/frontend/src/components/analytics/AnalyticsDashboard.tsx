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

      {/* Usage metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MetricCard
          title="Total Messages"
          value={analytics?.twilio.totalMessages || 0}
          change={analytics?.twilio.messageChange || 0}
          icon="📱"
        />
        <MetricCard
          title="Total Emails"
          value={analytics?.sendgrid.totalEmails || 0}
          change={analytics?.sendgrid.emailChange || 0}
          icon="✉️"
        />
        <MetricCard
          title="Total Tickets"
          value={analytics?.zendesk.totalTickets || 0}
          change={analytics?.zendesk.ticketChange || 0}
          icon="🎫"
        />
      </div>

      {/* Usage trends */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Message Volume</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={analytics?.twilio.dailyMessages || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="sms"
                  stroke="#3B82F6"
                  name="SMS"
                />
                <Line
                  type="monotone"
                  dataKey="voice"
                  stroke="#10B981"
                  name="Voice"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Email Performance</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={analytics?.sendgrid.emailMetrics || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="delivered" fill="#3B82F6" name="Delivered" />
                <Bar dataKey="opened" fill="#10B981" name="Opened" />
                <Bar dataKey="clicked" fill="#6366F1" name="Clicked" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Cost analysis */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Cost Analysis</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <CostCard
            service="Twilio"
            costs={analytics?.costs.twilio || {}}
            icon="📱"
          />
          <CostCard
            service="SendGrid"
            costs={analytics?.costs.sendgrid || {}}
            icon="✉️"
          />
          <CostCard
            service="Zendesk"
            costs={analytics?.costs.zendesk || {}}
            icon="🎫"
          />
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
}

function MetricCard({ title, value, change, icon }: MetricCardProps) {
  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <div className="flex items-center">
        <span className="text-2xl mr-2">{icon}</span>
        <h3 className="text-lg font-semibold">{title}</h3>
      </div>
      <p className="text-3xl font-bold mt-2">{value.toLocaleString()}</p>
      <div className={`flex items-center mt-2 ${change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
        <span>{change >= 0 ? '↑' : '↓'}</span>
        <span className="ml-1">{Math.abs(change)}% vs previous period</span>
      </div>
    </div>
  );
}

interface CostCardProps {
  service: string;
  costs: {
    current: number;
    previous: number;
    breakdown: {
      [key: string]: number;
    };
  };
  icon: string;
}

function CostCard({ service, costs, icon }: CostCardProps) {
  const change = ((costs.current - costs.previous) / costs.previous) * 100;

  return (
    <div className="bg-gray-50 p-4 rounded-lg">
      <div className="flex items-center">
        <span className="text-2xl mr-2">{icon}</span>
        <h4 className="text-lg font-semibold">{service}</h4>
      </div>
      <p className="text-2xl font-bold mt-2">${costs.current.toFixed(2)}</p>
      <div className={`flex items-center mt-2 ${change >= 0 ? 'text-red-500' : 'text-green-500'}`}>
        <span>{change >= 0 ? '↑' : '↓'}</span>
        <span className="ml-1">{Math.abs(change).toFixed(1)}% vs previous period</span>
      </div>
      <div className="mt-4">
        <h5 className="text-sm font-semibold mb-2">Cost Breakdown</h5>
        {Object.entries(costs.breakdown || {}).map(([key, value]) => (
          <div key={key} className="flex justify-between text-sm">
            <span className="text-gray-600">{key}</span>
            <span className="font-medium">${value.toFixed(2)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
