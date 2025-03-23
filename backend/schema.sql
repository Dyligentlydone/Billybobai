DROP TABLE IF EXISTS clients;
CREATE TABLE clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    twilio_account_sid TEXT,
    twilio_auth_token TEXT,
    twilio_phone_number TEXT,
    sendgrid_api_key TEXT,
    sendgrid_sender_email TEXT,
    zendesk_subdomain TEXT,
    zendesk_email TEXT,
    zendesk_api_token TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS business_configs;
CREATE TABLE business_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_id TEXT NOT NULL,
    workflow_id TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    tone TEXT NOT NULL DEFAULT 'professional',
    context TEXT NOT NULL DEFAULT '{}',  -- JSON string for AI context
    brand_voice TEXT,                    -- Additional brand voice settings
    ai_model TEXT DEFAULT 'gpt-4',       -- AI model to use
    max_response_tokens INTEGER DEFAULT 300,
    temperature FLOAT DEFAULT 0.7,
    fallback_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(business_id, workflow_id),
    FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE CASCADE
);

-- Index for quick lookups
CREATE INDEX idx_business_configs_lookup ON business_configs(phone_number, workflow_id);

-- Trigger to update the updated_at timestamp
CREATE TRIGGER update_business_configs_timestamp 
AFTER UPDATE ON business_configs
BEGIN
    UPDATE business_configs SET updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;
