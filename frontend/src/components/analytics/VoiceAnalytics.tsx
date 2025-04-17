import React from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, BarChart, Bar } from 'recharts';
import { VoiceMetrics } from '../../types/analytics';

interface Props {
  metrics: VoiceMetrics;
  businessId: string;
  clientId: string;
  isPlaceholder?: boolean;
}

const VoiceAnalytics: React.FC<Props> = ({ metrics, businessId, clientId, isPlaceholder = false }) => {
  // Sample data for development
  const placeholderData = {
    callMetrics: {
      totalCalls: 1250,
      averageDuration: '3:45',
      answerRate: 0.85,
      failureRate: 0.03
    },
    hourlyVolume: Array.from({ length: 24 }, (_, i) => ({
      hour: i,
      calls: Math.floor(Math.random() * 50)
    })),
    qualityMetrics: Array.from({ length: 7 }, (_, i) => ({
      date: `Day ${i + 1}`,
      transcriptionAccuracy: 0.85 + Math.random() * 0.1,
      satisfactionScore: 0.75 + Math.random() * 0.15
    }))
  };

  const renderCallVolume = () => (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-medium mb-4">Hourly Call Volume</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={placeholderData.hourlyVolume}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="hour" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="calls" fill="#8884d8" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );

  const renderQualityMetrics = () => (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-medium mb-4">Voice Quality Metrics</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={placeholderData.qualityMetrics}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="transcriptionAccuracy" stroke="#8884d8" name="Transcription Accuracy" />
          <Line type="monotone" dataKey="satisfactionScore" stroke="#82ca9d" name="Satisfaction Score" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm font-medium text-gray-500">Total Calls</h3>
          <p className="mt-2 text-3xl font-semibold text-gray-900">{metrics.totalCount}</p>
          {!businessId && <p className="mt-1 text-sm text-gray-500">No business selected</p>}
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm font-medium text-gray-500">Average Duration</h3>
          <p className="mt-2 text-3xl font-semibold text-gray-900">{Math.round(metrics.averageDuration / 60)}m</p>
          {!businessId && <p className="mt-1 text-sm text-gray-500">No business selected</p>}
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm font-medium text-gray-500">Success Rate</h3>
          <p className="mt-2 text-3xl font-semibold text-gray-900">{(metrics.successRate * 100).toFixed(1)}%</p>
          {!businessId && <p className="mt-1 text-sm text-gray-500">No business selected</p>}
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm font-medium text-gray-500">Inbound/Outbound</h3>
          <p className="mt-2 text-3xl font-semibold text-gray-900">
            {metrics.inboundCalls}/{metrics.outboundCalls}
          </p>
          {!businessId && <p className="mt-1 text-sm text-gray-500">No business selected</p>}
        </div>
      </div>

      {/* Call Volume */}
      <div className="bg-white rounded-lg shadow p-4">
        <h3 className="text-lg font-medium mb-4">Call Volume</h3>
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
            <p className="text-gray-500">No call volume data available{!businessId && " - Select a business to view data"}</p>
          </div>
        )}
      </div>

      {/* Success Rate Trend */}
      <div className="bg-white rounded-lg shadow p-4">
        <h3 className="text-lg font-medium mb-4">Success Rate Trend</h3>
        {metrics.hourlyActivity.length > 0 ? (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={metrics.hourlyActivity}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="hour" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="successRate" stroke="#3B82F6" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="h-64 flex items-center justify-center">
            <p className="text-gray-500">No success rate data available{!businessId && " - Select a business to view data"}</p>
          </div>
        )}
      </div>

      {/* Call Duration Distribution */}
      <div className="bg-white rounded-lg shadow p-4">
        <h3 className="text-lg font-medium mb-4">Call Duration Distribution</h3>
        {metrics.hourlyActivity.length > 0 ? (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={metrics.hourlyActivity}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="duration" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#3B82F6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="h-64 flex items-center justify-center">
            <p className="text-gray-500">No duration data available{!businessId && " - Select a business to view data"}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default VoiceAnalytics;
