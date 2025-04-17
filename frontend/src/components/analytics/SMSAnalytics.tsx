import React, { useState } from 'react';
import { SMSMetrics, Conversation } from '../../types/analytics';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { format } from 'date-fns';

interface Props {
  metrics: SMSMetrics;
  businessId: string;
  clientId: string;
  isPlaceholder?: boolean;
}

const SMSAnalytics: React.FC<Props> = ({ metrics, businessId, clientId, isPlaceholder }) => {
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null);
  const [conversationsPage, setConversationsPage] = useState(1);

  // Sample data for placeholder state
  const placeholderData = {
    qualityMetrics: Array.from({ length: 7 }, (_, i) => ({
      date: `Day ${i + 1}`,
      sentiment: 0.7 + Math.random() * 0.2,
      quality: 0.8 + Math.random() * 0.15
    })),
    responseTypes: [
      { type: 'Quick Reply', count: 45 },
      { type: 'Custom', count: 30 },
      { type: 'Automated', count: 25 }
    ],
    dailyCosts: Array.from({ length: 7 }, (_, i) => ({
      date: `Day ${i + 1}`,
      ai: Math.random() * 50,
      service: Math.random() * 30,
      total: Math.random() * 80
    })),
    hourlyActivity: Array.from({ length: 24 }, (_, i) => ({
      hour: i,
      count: Math.floor(Math.random() * 100)
    })),
    conversations: Array.from({ length: 5 }, (_, i) => ({
      id: `conv-${i}`,
      startedAt: new Date(Date.now() - Math.random() * 86400000).toISOString(),
      topic: ['Booking', 'Support', 'Inquiry', 'Feedback', 'Other'][Math.floor(Math.random() * 5)],
      sentiment: ['positive', 'neutral', 'negative'][Math.floor(Math.random() * 3)] as 'positive' | 'neutral' | 'negative',
      messageCount: Math.floor(Math.random() * 10) + 2,
      avgResponseTime: Math.random() * 60 + 30,
      phoneNumber: `+1${Math.floor(Math.random() * 9000000000) + 1000000000}`,
      messages: Array.from({ length: Math.floor(Math.random() * 5) + 2 }, (_, j) => ({
        direction: j % 2 === 0 ? 'inbound' as const : 'outbound' as const,
        content: j % 2 === 0 ? 'Customer message' : 'AI response',
        createdAt: new Date(Date.now() - (86400000 - j * 3600000)).toISOString(),
        aiConfidence: Math.random(),
        templateUsed: j % 2 === 0 ? undefined : 'Template A'
      }))
    }))
  };

  const displayData = isPlaceholder ? {
    totalCount: '1,234',
    responseTime: '2.5',
    deliveryRate: 0.98,
    optOutRate: 0.02,
    qualityMetrics: placeholderData.qualityMetrics,
    responseTypes: placeholderData.responseTypes,
    dailyCosts: placeholderData.dailyCosts,
    hourlyActivity: placeholderData.hourlyActivity,
    conversations: placeholderData.conversations
  } : metrics;

  const renderQualityMetrics = () => (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-medium mb-4">Quality Metrics</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={displayData.qualityMetrics}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="sentiment" stroke="#8884d8" name="Sentiment" />
          <Line type="monotone" dataKey="quality" stroke="#82ca9d" name="Quality" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );

  const renderResponseTypes = () => (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-medium mb-4">Response Types</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={displayData.responseTypes}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="type" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="count" fill="#8884d8" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );

  const renderCostMetrics = () => (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-medium mb-4">Daily Costs</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={displayData.dailyCosts}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="ai" stroke="#8884d8" name="AI Cost" />
          <Line type="monotone" dataKey="service" stroke="#82ca9d" name="Service Cost" />
          <Line type="monotone" dataKey="total" stroke="#ffc658" name="Total Cost" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );

  const renderHourlyActivity = () => (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-medium mb-4">Hourly Message Volume</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={displayData.hourlyActivity}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="hour" tickFormatter={(hour) => `${hour}:00`} />
          <YAxis />
          <Tooltip labelFormatter={(hour) => `${hour}:00`} />
          <Bar dataKey="count" fill="#8884d8" name="Messages" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );

  const renderConversations = () => (
    <div className="bg-white rounded-lg shadow p-4 mt-6">
      <h3 className="text-lg font-medium mb-4">Recent Conversations</h3>
      <div className="space-y-4">
        {displayData.conversations.map((conv) => (
          <div 
            key={conv.id} 
            className="border rounded p-4 cursor-pointer hover:bg-gray-50"
            onClick={() => setSelectedConversation(conv)}
          >
            <div className="flex justify-between items-start">
              <div>
                <p className="font-medium">{format(new Date(conv.startedAt), 'MMM d, yyyy h:mm a')}</p>
                <p className="text-sm text-gray-600">Topic: {conv.topic}</p>
                <p className="text-sm text-gray-600">Contact: {conv.phoneNumber}</p>
              </div>
              <div className="text-right">
                <p className="text-sm">{conv.messageCount} messages</p>
                <p className="text-sm text-gray-600">
                  Avg Response: {Math.round(conv.avgResponseTime)}s
                </p>
              </div>
            </div>
            <div className="mt-2">
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                ${conv.sentiment === 'positive' ? 'bg-green-100 text-green-800' :
                  conv.sentiment === 'negative' ? 'bg-red-100 text-red-800' :
                  'bg-gray-100 text-gray-800'}`}>
                {conv.sentiment}
              </span>
            </div>
          </div>
        ))}
      </div>
      
      {/* Pagination */}
      <div className="mt-4 flex justify-center space-x-2">
        <button
          className="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50"
          disabled={conversationsPage === 1}
          onClick={() => setConversationsPage(p => p - 1)}
        >
          Previous
        </button>
        <span className="px-3 py-1">Page {conversationsPage}</span>
        <button
          className="px-3 py-1 border rounded hover:bg-gray-50"
          onClick={() => setConversationsPage(p => p + 1)}
        >
          Next
        </button>
      </div>
    </div>
  );

  const renderConversationDetail = () => {
    if (!selectedConversation) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-hidden">
          <div className="p-4 border-b flex justify-between items-center">
            <div>
              <h3 className="text-lg font-medium">Conversation Detail</h3>
              <p className="text-sm text-gray-600">
                {format(new Date(selectedConversation.startedAt), 'MMM d, yyyy h:mm a')}
              </p>
              <p className="text-sm text-gray-600">Contact: {selectedConversation.phoneNumber}</p>
            </div>
            <button
              className="text-gray-400 hover:text-gray-500"
              onClick={() => setSelectedConversation(null)}
            >
              ✕
            </button>
          </div>
          <div className="p-4 space-y-4 overflow-y-auto max-h-[calc(90vh-8rem)]">
            {selectedConversation.messages.map((msg, i) => (
              <div
                key={i}
                className={`flex ${msg.direction === 'inbound' ? 'justify-start' : 'justify-end'}`}
              >
                <div
                  className={`rounded-lg px-4 py-2 max-w-[80%] ${
                    msg.direction === 'inbound'
                      ? 'bg-gray-100'
                      : 'bg-blue-500 text-white'
                  }`}
                >
                  <p>{msg.content}</p>
                  <p className="text-xs mt-1 opacity-75">
                    {format(new Date(msg.createdAt), 'h:mm a')}
                    {msg.direction === 'outbound' && msg.aiConfidence && (
                      <span className="ml-2">
                        AI Confidence: {(msg.aiConfidence * 100).toFixed(0)}%
                      </span>
                    )}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm text-gray-500">Total Messages</h3>
          <p className="mt-1 text-2xl font-semibold">{displayData.totalCount}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm text-gray-500">Response Time</h3>
          <p className="mt-1 text-2xl font-semibold">{displayData.responseTime}s</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm text-gray-500">Delivery Rate</h3>
          <p className="mt-1 text-2xl font-semibold">{(displayData.deliveryRate * 100).toFixed(1)}%</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm text-gray-500">Opt-out Rate</h3>
          <p className="mt-1 text-2xl font-semibold">{(displayData.optOutRate * 100).toFixed(1)}%</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {renderQualityMetrics()}
        {renderResponseTypes()}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {renderCostMetrics()}
        {renderHourlyActivity()}
      </div>

      {renderConversations()}
      {renderConversationDetail()}
      
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

export default SMSAnalytics;
