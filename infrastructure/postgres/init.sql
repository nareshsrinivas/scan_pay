-- Initialize smart_checkout database
CREATE DATABASE IF NOT EXISTS smart_checkout;

-- Create n8n database
CREATE DATABASE IF NOT EXISTS n8n;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE smart_checkout TO postgres;
GRANT ALL PRIVILEGES ON DATABASE n8n TO postgres;
