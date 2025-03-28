import { Conversation, Message, ConversationsResponse } from '../types/conversations';
import { subDays, subHours, subMinutes } from 'date-fns';

const now = new Date();

const mockMessages: Record<string, Message[]> = {
  "conv1": [
    {
      id: "msg1",
      content: "Hi, I'm having trouble with my order #12345",
      timestamp: subHours(now, 2).toISOString(),
      from: "+1234567890",
      to: "+1987654321",
      direction: "inbound",
      source: "twilio",
      status: "delivered"
    },
    {
      id: "msg2",
      content: "I'm sorry to hear that. Let me look up your order. Can you tell me what specific issue you're experiencing?",
      timestamp: subHours(now, 2).toISOString(),
      from: "+1987654321",
      to: "+1234567890",
      direction: "outbound",
      source: "twilio",
      status: "delivered"
    },
    {
      id: "msg3",
      content: "The package says it was delivered but I haven't received it",
      timestamp: subHours(now, 1).toISOString(),
      from: "+1234567890",
      to: "+1987654321",
      direction: "inbound",
      source: "twilio",
      status: "delivered"
    }
  ],
  "conv2": [
    {
      id: "msg4",
      content: "When will my subscription renew?",
      timestamp: subDays(now, 1).toISOString(),
      from: "+1555555555",
      to: "+1987654321",
      direction: "inbound",
      source: "twilio",
      status: "delivered"
    },
    {
      id: "msg5",
      content: "Your subscription is set to renew on the 15th of next month. Would you like me to send you a reminder?",
      timestamp: subDays(now, 1).toISOString(),
      from: "+1987654321",
      to: "+1555555555",
      direction: "outbound",
      source: "zendesk",
      status: "sent",
      zendeskTicketId: "ticket123"
    }
  ],
  "conv3": [
    {
      id: "msg6",
      content: "Do you offer international shipping?",
      timestamp: subMinutes(now, 30).toISOString(),
      from: "+1777777777",
      to: "+1987654321",
      direction: "inbound",
      source: "twilio",
      status: "delivered"
    }
  ]
};

const mockConversations: Conversation[] = [
  {
    id: "conv1",
    customerNumber: "+1234567890",
    customerName: "John Smith",
    lastMessage: mockMessages["conv1"][mockMessages["conv1"].length - 1],
    unreadCount: 2,
    status: "active",
    tags: ["support", "shipping"],
    updatedAt: subHours(now, 1).toISOString()
  },
  {
    id: "conv2",
    customerNumber: "+1555555555",
    customerName: "Alice Johnson",
    lastMessage: mockMessages["conv2"][mockMessages["conv2"].length - 1],
    unreadCount: 0,
    status: "resolved",
    zendeskTicketUrl: "https://support.zendesk.com/tickets/ticket123",
    tags: ["billing", "subscription"],
    updatedAt: subDays(now, 1).toISOString()
  },
  {
    id: "conv3",
    customerNumber: "+1777777777",
    lastMessage: mockMessages["conv3"][mockMessages["conv3"].length - 1],
    unreadCount: 1,
    status: "pending",
    tags: ["sales"],
    updatedAt: subMinutes(now, 30).toISOString()
  }
];

export const getMockConversations = (): ConversationsResponse => ({
  conversations: mockConversations,
  totalCount: mockConversations.length,
  hasMore: false
});

export const getMockMessages = (conversationId: string): Message[] => 
  mockMessages[conversationId] || [];
