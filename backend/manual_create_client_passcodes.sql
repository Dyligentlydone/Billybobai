-- Run this in your Railway Postgres console if migrations are not working
CREATE TABLE IF NOT EXISTS client_passcodes (
    id SERIAL PRIMARY KEY,
    business_id VARCHAR(255) NOT NULL REFERENCES businesses(id),
    passcode VARCHAR(5) NOT NULL,
    permissions JSON NOT NULL
);
