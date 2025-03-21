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
