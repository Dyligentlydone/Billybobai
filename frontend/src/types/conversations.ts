export interface Message {
  id: string;
  content: string;
  timestamp: string;
  from: string;
  to: string;
  direction: 'inbound' | 'outbound';
  source: 'twilio' | 'zendesk';
  status: 'sent' | 'delivered' | 'failed';
  mediaUrls?: string[];
  zendeskTicketId?: string;
}

export interface Conversation {
  id: string;
  customerNumber: string;
  customerName?: string;
  lastMessage: Message;
  unreadCount: number;
  status: 'active' | 'resolved' | 'pending';
  zendeskTicketUrl?: string;
  tags: string[];
  updatedAt: string;
}

export interface ConversationsResponse {
  conversations: Conversation[];
  totalCount: number;
  hasMore: boolean;
}

export interface ConversationMessagesResponse {
  messages: Message[];
  hasMore: boolean;
  nextCursor?: string;
}
