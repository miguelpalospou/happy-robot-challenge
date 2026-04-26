-- Add carrier assignment fields to loads table
ALTER TABLE loads ADD COLUMN IF NOT EXISTS assigned_mc_number VARCHAR(20);
ALTER TABLE loads ADD COLUMN IF NOT EXISTS assigned_carrier_name VARCHAR(255);
ALTER TABLE loads ADD COLUMN IF NOT EXISTS booked_at TIMESTAMP WITH TIME ZONE;

-- Index for finding booked loads by carrier
CREATE INDEX IF NOT EXISTS idx_loads_assigned_mc ON loads(assigned_mc_number);
