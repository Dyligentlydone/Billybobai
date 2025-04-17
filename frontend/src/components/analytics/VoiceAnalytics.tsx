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
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm text-gray-500">Total Calls</h3>
          <p className="mt-1 text-2xl font-semibold">{placeholderData.callMetrics.totalCalls}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm text-gray-500">Average Duration</h3>
          <p className="mt-1 text-2xl font-semibold">{placeholderData.callMetrics.averageDuration}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm text-gray-500">Answer Rate</h3>
          <p className="mt-1 text-2xl font-semibold">
            {(placeholderData.callMetrics.answerRate * 100).toFixed(1)}%
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm text-gray-500">Failure Rate</h3>
          <p className="mt-1 text-2xl font-semibold">
            {(placeholderData.callMetrics.failureRate * 100).toFixed(1)}%
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {renderCallVolume()}
        {renderQualityMetrics()}
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

export default VoiceAnalytics;
