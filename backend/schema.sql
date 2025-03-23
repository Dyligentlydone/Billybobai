-- Clients table
CREATE TABLE IF NOT EXISTS clients (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    twilio_account_sid TEXT,
    twilio_auth_token TEXT,
    twilio_messaging_service TEXT,
    zendesk_subdomain TEXT,
    zendesk_email TEXT,
    zendesk_api_token TEXT,
    openai_api_key TEXT,
    settings JSON,
    UNIQUE(name)
);

-- Business configurations table
CREATE TABLE IF NOT EXISTS business_configs (
    business_id TEXT NOT NULL,
    workflow_id TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    tone TEXT DEFAULT 'professional',
    context JSON,
    brand_voice TEXT,
    ai_model TEXT DEFAULT 'gpt-4',
    max_response_tokens INTEGER DEFAULT 300,
    temperature REAL DEFAULT 0.7,
    fallback_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (business_id, workflow_id),
    FOREIGN KEY (business_id) REFERENCES clients(id) ON DELETE CASCADE,
    FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE CASCADE
);

-- Workflows table
CREATE TABLE IF NOT EXISTS workflows (
    id TEXT PRIMARY KEY,
    client_id TEXT NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    actions JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
);

-- Message metrics table
CREATE TABLE IF NOT EXISTS message_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_id TEXT NOT NULL,
    workflow_id TEXT NOT NULL,
    workflow_name TEXT NOT NULL,
    message_sid TEXT,
    ticket_id INTEGER,
    response_time INTEGER,
    ai_time INTEGER,
    tokens INTEGER,
    confidence REAL,
    sentiment REAL,
    relevance REAL,
    quality_score REAL,
    is_follow_up BOOLEAN,
    sms_cost REAL,
    ai_cost REAL,
    total_cost REAL,
    error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (business_id) REFERENCES clients(id) ON DELETE CASCADE,
    FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE CASCADE
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_business_configs_phone ON business_configs(phone_number);
CREATE INDEX IF NOT EXISTS idx_business_configs_workflow ON business_configs(workflow_id);
CREATE INDEX IF NOT EXISTS idx_message_metrics_business ON message_metrics(business_id);
CREATE INDEX IF NOT EXISTS idx_message_metrics_workflow ON message_metrics(workflow_id);
CREATE INDEX IF NOT EXISTS idx_message_metrics_created ON message_metrics(created_at);
CREATE INDEX IF NOT EXISTS idx_workflows_client ON workflows(client_id);

-- Create triggers for updated_at
CREATE TRIGGER IF NOT EXISTS clients_updated_at 
    AFTER UPDATE ON clients
BEGIN
    UPDATE clients SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS business_configs_updated_at 
    AFTER UPDATE ON business_configs
BEGIN
    UPDATE business_configs SET updated_at = CURRENT_TIMESTAMP 
    WHERE business_id = NEW.business_id AND workflow_id = NEW.workflow_id;
END;

CREATE TRIGGER IF NOT EXISTS workflows_updated_at 
    AFTER UPDATE ON workflows
BEGIN
    UPDATE workflows SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
