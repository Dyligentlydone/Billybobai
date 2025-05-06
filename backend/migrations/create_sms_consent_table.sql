-- Create SMS Consent table for opt-in tracking
CREATE TABLE IF NOT EXISTS sms_consents (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) NOT NULL,
    business_id VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_sms_consent_phone_business UNIQUE (phone_number, business_id)
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_sms_consents_phone_business 
ON sms_consents (phone_number, business_id);

-- Create index for status queries
CREATE INDEX IF NOT EXISTS idx_sms_consents_status
ON sms_consents (status);
