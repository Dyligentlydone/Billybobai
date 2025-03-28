import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { getMockConversations, getMockMessages } from '../../data/mockConversations';
import { Message } from '../../types/conversations';

interface Props {
  businessId: string;
}

export const SMSConversations: React.FC<Props> = ({ businessId }) => {
  const [selectedConversation, setSelectedConversation] = useState<string | null>(null);
  const [messageInput, setMessageInput] = useState('');

  // Fetch conversations
  const { data: conversationsData } = useQuery(
    ['conversations', businessId],
    () => getMockConversations(),
    {
      refetchInterval: 5000 // Refresh every 5 seconds
    }
  );

  // Fetch messages for selected conversation
  const { data: messagesData } = useQuery(
    ['messages', selectedConversation],
    () => selectedConversation ? getMockMessages(selectedConversation) : [],
    {
      enabled: !!selectedConversation,
      refetchInterval: 5000
    }
  );

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!messageInput.trim() || !selectedConversation) return;

    // In real implementation, this would call the API
    console.log('Sending message:', messageInput);
    setMessageInput('');
  };

  return (
    <div className="flex h-[calc(100vh-200px)] bg-gray-50 rounded-lg overflow-hidden">
      {/* Conversations List */}
      <div className="w-1/3 border-r border-gray-200 bg-white">
        <div className="p-4 border-b border-gray-200">
          <input
            type="text"
            placeholder="Search conversations..."
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div className="overflow-y-auto h-[calc(100%-64px)]">
          {conversationsData?.conversations.map((conversation) => (
            <div
              key={conversation.id}
              onClick={() => setSelectedConversation(conversation.id)}
              className={`p-4 border-b border-gray-200 cursor-pointer hover:bg-gray-50 ${
                selectedConversation === conversation.id ? 'bg-blue-50' : ''
              }`}
            >
              <div className="flex justify-between items-start mb-1">
                <span className="font-medium">
                  {conversation.customerName || conversation.customerNumber}
                </span>
                {conversation.unreadCount > 0 && (
                  <span className="bg-red-500 text-white text-xs px-2 py-1 rounded-full">
                    {conversation.unreadCount}
                  </span>
                )}
              </div>
              <div className="text-sm text-gray-500 truncate">
                {conversation.lastMessage.content}
              </div>
              <div className="flex justify-between items-center mt-2 text-xs text-gray-400">
                <span>{new Date(conversation.updatedAt).toLocaleString()}</span>
                <span className={`px-2 py-1 rounded ${
                  conversation.status === 'active' ? 'bg-green-100 text-green-800' :
                  conversation.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {conversation.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Messages View */}
      <div className="flex-1 flex flex-col bg-gray-50">
        {selectedConversation ? (
          <>
            {/* Messages */}
            <div className="flex-1 p-4 overflow-y-auto">
              {messagesData?.map((message: Message) => (
                <div
                  key={message.id}
                  className={`max-w-[70%] mb-4 ${
                    message.direction === 'outbound' ? 'ml-auto' : ''
                  }`}
                >
                  <div
                    className={`p-3 rounded-lg ${
                      message.direction === 'outbound'
                        ? 'bg-blue-500 text-white'
                        : 'bg-white'
                    }`}
                  >
                    {message.content}
                  </div>
                  <div className="text-xs text-gray-400 mt-1">
                    {new Date(message.timestamp).toLocaleString()}
                    {message.source === 'zendesk' && (
                      <span className="ml-2 text-blue-500">Zendesk</span>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Message Input */}
            <form onSubmit={handleSendMessage} className="p-4 bg-white border-t">
              <div className="flex space-x-4">
                <input
                  type="text"
                  value={messageInput}
                  onChange={(e) => setMessageInput(e.target.value)}
                  placeholder="Type a message..."
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  type="submit"
                  disabled={!messageInput.trim()}
                  className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
                >
                  Send
                </button>
              </div>
            </form>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-500">
            Select a conversation to view messages
          </div>
        )}
      </div>
    </div>
  );
};
