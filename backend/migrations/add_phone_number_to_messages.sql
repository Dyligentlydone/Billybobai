-- Add phone_number column to messages table
ALTER TABLE messages ADD COLUMN phone_number TEXT;

-- Create index on phone_number for faster lookups
CREATE INDEX idx_messages_phone_number ON messages (phone_number);
