-- SQL migration to add conversation tracking fields to messages table

-- Add conversation_id column
ALTER TABLE messages ADD COLUMN IF NOT EXISTS conversation_id VARCHAR(36);

-- Add index on conversation_id for faster lookups
CREATE INDEX IF NOT EXISTS ix_messages_conversation_id ON messages (conversation_id);

-- Add is_first_in_conversation column
ALTER TABLE messages ADD COLUMN IF NOT EXISTS is_first_in_conversation BOOLEAN NOT NULL DEFAULT FALSE;

-- Add response_to_message_id column
ALTER TABLE messages ADD COLUMN IF NOT EXISTS response_to_message_id INTEGER;

-- Add foreign key constraint for response_to_message_id
ALTER TABLE messages 
ADD CONSTRAINT IF NOT EXISTS fk_response_to_message 
FOREIGN KEY (response_to_message_id) REFERENCES messages(id);
