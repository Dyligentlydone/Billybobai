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
        id: `msg-${j}`,
        content: j % 2 === 0 ? 'Customer message' : 'AI response',
        createdAt: new Date(Date.now() - (86400000 - j * 3600000)).toISOString(),
        direction: j % 2 === 0 ? 'inbound' as const : 'outbound' as const,
        status: j % 2 === 0 ? 'delivered' : 'sent',
        phoneNumber: `+1${Math.floor(Math.random() * 9000000000) + 1000000000}`,
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

  const transformConversation = (conversation: Conversation): Conversation => {
    return {
      id: conversation.id,
      startedAt: conversation.startedAt,
      topic: conversation.topic,
      sentiment: conversation.sentiment,
      messageCount: conversation.messageCount,
      avgResponseTime: conversation.avgResponseTime,
      phoneNumber: conversation.phoneNumber,
      messages: conversation.messages.map(msg => ({
        id: msg.id,
        content: msg.content,
        createdAt: msg.createdAt,
        direction: msg.direction,
        status: msg.status || 'delivered',
        phoneNumber: msg.phoneNumber,
        aiConfidence: msg.aiConfidence,
        templateUsed: msg.templateUsed
      }))
    };
  };

  const renderQualityMetrics = () => (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-medium mb-4">Quality Metrics</h3>
      {displayData.qualityMetrics.length > 0 ? (
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
      ) : (
        <div className="h-64 flex items-center justify-center">
          <p className="text-gray-500">No quality metrics available{!businessId && " - Select a business to view data"}</p>
        </div>
      )}
    </div>
  );

  const renderResponseTypes = () => (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-medium mb-4">Response Types</h3>
      {displayData.responseTypes.length > 0 ? (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={displayData.responseTypes}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="type" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="count" fill="#8884d8" />
          </BarChart>
        </ResponsiveContainer>
      ) : (
        <div className="h-64 flex items-center justify-center">
          <p className="text-gray-500">No response type data available{!businessId && " - Select a business to view data"}</p>
        </div>
      )}
    </div>
  );

  const renderCostMetrics = () => (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-medium mb-4">Daily Costs</h3>
      {displayData.dailyCosts.length > 0 ? (
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
      ) : (
        <div className="h-64 flex items-center justify-center">
          <p className="text-gray-500">No cost trend data available{!businessId && " - Select a business to view data"}</p>
        </div>
      )}
    </div>
  );

  const renderHourlyActivity = () => (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-medium mb-4">Hourly Message Volume</h3>
      {displayData.hourlyActivity.length > 0 ? (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={displayData.hourlyActivity}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="hour" tickFormatter={(hour) => `${hour}:00`} />
            <YAxis />
            <Tooltip labelFormatter={(hour) => `${hour}:00`} />
            <Bar dataKey="count" fill="#8884d8" name="Messages" />
          </BarChart>
        </ResponsiveContainer>
      ) : (
        <div className="h-64 flex items-center justify-center">
          <p className="text-gray-500">No activity data available{!businessId && " - Select a business to view data"}</p>
        </div>
      )}
    </div>
  );

  const renderConversations = () => (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="p-4 border-b border-gray-200">
        <h3 className="text-lg font-medium">Recent Conversations</h3>
      </div>
      {displayData.conversations.length > 0 ? (
        <div className="divide-y divide-gray-200">
          {displayData.conversations.map((conv, i) => {
            const lastMessage = 'lastMessage' in conv ? conv.lastMessage : conv.messages[conv.messages.length - 1]?.content || '';
            const timestamp = 'timestamp' in conv ? conv.timestamp : format(new Date(conv.startedAt), 'MMM d, yyyy h:mm a');
            return (
              <div key={i} className="p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="text-sm font-medium text-gray-900">{conv.phoneNumber}</p>
                    <p className="mt-1 text-sm text-gray-500">{lastMessage}</p>
                  </div>
                  <span className="text-sm text-gray-500">{timestamp}</span>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="p-4 text-center">
          <p className="text-gray-500">No conversations available{!businessId && " - Select a business to view data"}</p>
        </div>
      )}
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
                {selectedConversation.startedAt ? (() => { try { return format(new Date(selectedConversation.startedAt), 'MMM d, yyyy h:mm a'); } catch { return 'Unknown'; } })() : 'Unknown'}
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
                    {msg.createdAt ? (() => { try { return format(new Date(msg.createdAt), 'h:mm a'); } catch { return 'Unknown'; } })() : 'Unknown'}
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
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm font-medium text-gray-500">Total Messages</h3>
          <p className="mt-2 text-3xl font-semibold text-gray-900">{displayData.totalCount}</p>
          {!businessId && <p className="mt-1 text-sm text-gray-500">No business selected</p>}
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm font-medium text-gray-500">Response Time</h3>
          <p className="mt-2 text-3xl font-semibold text-gray-900">{displayData.responseTime}</p>
          {!businessId && <p className="mt-1 text-sm text-gray-500">No business selected</p>}
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm font-medium text-gray-500">Delivery Rate</h3>
          <p className="mt-2 text-3xl font-semibold text-gray-900">{(displayData.deliveryRate * 100).toFixed(1)}%</p>
          {!businessId && <p className="mt-1 text-sm text-gray-500">No business selected</p>}
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm font-medium text-gray-500">Opt-out Rate</h3>
          <p className="mt-2 text-3xl font-semibold text-gray-900">{(displayData.optOutRate * 100).toFixed(1)}%</p>
          {!businessId && <p className="mt-1 text-sm text-gray-500">No business selected</p>}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {renderQualityMetrics()}
        {renderResponseTypes()}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
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
