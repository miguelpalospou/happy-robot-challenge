-- Happy Robot Inbound Carrier Sales - Database Schema (Simplified)
-- 4 Tables: loads, carriers, calls, negotiations

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- LOADS TABLE
-- ============================================
CREATE TABLE loads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    load_id VARCHAR(50) UNIQUE NOT NULL,
    origin VARCHAR(255) NOT NULL,
    destination VARCHAR(255) NOT NULL,
    pickup_datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    delivery_datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    equipment_type VARCHAR(100) NOT NULL,
    loadboard_rate DECIMAL(10, 2) NOT NULL,
    notes TEXT,
    weight DECIMAL(10, 2),
    commodity_type VARCHAR(100),
    num_of_pieces INTEGER,
    miles DECIMAL(10, 2),
    dimensions VARCHAR(100),
    status VARCHAR(50) DEFAULT 'available' CHECK (status IN ('available', 'pending', 'booked', 'in_transit', 'delivered', 'cancelled')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- CARRIERS TABLE
-- Caches verified carrier info from FMCSA
-- ============================================
CREATE TABLE carriers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    mc_number VARCHAR(20) UNIQUE NOT NULL,
    legal_name VARCHAR(255),
    dba_name VARCHAR(255),
    phone VARCHAR(50),
    email VARCHAR(255),
    dot_number VARCHAR(20),
    entity_type VARCHAR(50),
    operating_status VARCHAR(50),
    safety_rating VARCHAR(50),
    is_verified BOOLEAN DEFAULT FALSE,
    is_eligible BOOLEAN DEFAULT FALSE,
    fmcsa_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- CALLS TABLE
-- One row per call, includes agreement data
-- ============================================
CREATE TABLE calls (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    call_id VARCHAR(100) UNIQUE NOT NULL,
    carrier_id UUID REFERENCES carriers(id),
    mc_number VARCHAR(20),
    phone_number VARCHAR(50),
    call_start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    call_end_time TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    -- Outcome & sentiment
    outcome VARCHAR(50) CHECK (outcome IN (
        'load_booked', 'transferred_to_rep', 'no_agreement',
        'carrier_declined', 'no_matching_loads', 'verification_failed',
        'abandoned', 'error'
    )),
    sentiment VARCHAR(50) CHECK (sentiment IN (
        'very_positive', 'positive', 'neutral', 'negative', 'very_negative'
    )),
    sentiment_score DECIMAL(3, 2),
    -- Call content
    transcript TEXT,
    summary TEXT,
    recording_url VARCHAR(500),
    extracted_data JSONB,
    -- Agreement data (when deal is made)
    load_id UUID REFERENCES loads(id),
    agreed_rate DECIMAL(10, 2),
    carrier_name VARCHAR(255),
    transferred_at TIMESTAMP WITH TIME ZONE,
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- NEGOTIATIONS TABLE
-- One row per negotiation round (max 3 per call)
-- ============================================
CREATE TABLE negotiations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    call_id UUID REFERENCES calls(id) ON DELETE CASCADE,
    load_id UUID REFERENCES loads(id),
    round_number INTEGER NOT NULL CHECK (round_number >= 1 AND round_number <= 3),
    initial_rate DECIMAL(10, 2) NOT NULL,
    carrier_offer DECIMAL(10, 2),
    counter_offer DECIMAL(10, 2),
    final_rate DECIMAL(10, 2),
    status VARCHAR(50) CHECK (status IN (
        'pending', 'counter_offered', 'accepted', 'rejected', 'expired'
    )),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- INDEXES
-- ============================================
CREATE INDEX idx_loads_status ON loads(status);
CREATE INDEX idx_loads_origin ON loads(origin);
CREATE INDEX idx_loads_destination ON loads(destination);
CREATE INDEX idx_loads_pickup ON loads(pickup_datetime);

CREATE INDEX idx_carriers_mc ON carriers(mc_number);

CREATE INDEX idx_calls_carrier ON calls(carrier_id);
CREATE INDEX idx_calls_outcome ON calls(outcome);
CREATE INDEX idx_calls_start_time ON calls(call_start_time);

CREATE INDEX idx_negotiations_call ON negotiations(call_id);

-- ============================================
-- AUTO-UPDATE TIMESTAMPS
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_loads_updated_at BEFORE UPDATE ON loads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_carriers_updated_at BEFORE UPDATE ON carriers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_calls_updated_at BEFORE UPDATE ON calls
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_negotiations_updated_at BEFORE UPDATE ON negotiations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- ROW LEVEL SECURITY
-- ============================================
ALTER TABLE loads ENABLE ROW LEVEL SECURITY;
ALTER TABLE carriers ENABLE ROW LEVEL SECURITY;
ALTER TABLE calls ENABLE ROW LEVEL SECURITY;
ALTER TABLE negotiations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role full access on loads" ON loads
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access on carriers" ON carriers
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access on calls" ON calls
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access on negotiations" ON negotiations
    FOR ALL USING (auth.role() = 'service_role');
