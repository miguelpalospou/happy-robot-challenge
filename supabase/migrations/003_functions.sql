-- Happy Robot - Database Functions & Views
-- Functions for load search, metrics aggregation, and business logic

-- ============================================
-- LOAD SEARCH FUNCTION
-- Search loads by origin, destination, equipment type, and date range
-- ============================================
CREATE OR REPLACE FUNCTION search_loads(
    p_origin TEXT DEFAULT NULL,
    p_destination TEXT DEFAULT NULL,
    p_equipment_type TEXT DEFAULT NULL,
    p_pickup_date_from TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    p_pickup_date_to TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    p_min_rate DECIMAL DEFAULT NULL,
    p_max_rate DECIMAL DEFAULT NULL,
    p_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    load_id VARCHAR,
    origin VARCHAR,
    destination VARCHAR,
    pickup_datetime TIMESTAMP WITH TIME ZONE,
    delivery_datetime TIMESTAMP WITH TIME ZONE,
    equipment_type VARCHAR,
    loadboard_rate DECIMAL,
    notes TEXT,
    weight DECIMAL,
    commodity_type VARCHAR,
    num_of_pieces INTEGER,
    miles DECIMAL,
    dimensions VARCHAR,
    status VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        l.id,
        l.load_id,
        l.origin,
        l.destination,
        l.pickup_datetime,
        l.delivery_datetime,
        l.equipment_type,
        l.loadboard_rate,
        l.notes,
        l.weight,
        l.commodity_type,
        l.num_of_pieces,
        l.miles,
        l.dimensions,
        l.status
    FROM loads l
    WHERE l.status = 'available'
        AND (p_origin IS NULL OR l.origin ILIKE '%' || p_origin || '%')
        AND (p_destination IS NULL OR l.destination ILIKE '%' || p_destination || '%')
        AND (p_equipment_type IS NULL OR l.equipment_type ILIKE '%' || p_equipment_type || '%')
        AND (p_pickup_date_from IS NULL OR l.pickup_datetime >= p_pickup_date_from)
        AND (p_pickup_date_to IS NULL OR l.pickup_datetime <= p_pickup_date_to)
        AND (p_min_rate IS NULL OR l.loadboard_rate >= p_min_rate)
        AND (p_max_rate IS NULL OR l.loadboard_rate <= p_max_rate)
    ORDER BY l.pickup_datetime ASC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- NEGOTIATION EVALUATION FUNCTION
-- Evaluate a carrier's counter offer against business rules
-- ============================================
CREATE OR REPLACE FUNCTION evaluate_counter_offer(
    p_load_id UUID,
    p_carrier_offer DECIMAL,
    p_round_number INTEGER
)
RETURNS TABLE (
    is_acceptable BOOLEAN,
    min_acceptable_rate DECIMAL,
    suggested_counter DECIMAL,
    message TEXT
) AS $$
DECLARE
    v_loadboard_rate DECIMAL;
    v_min_rate DECIMAL;
    v_flex_percentage DECIMAL;
BEGIN
    -- Get the loadboard rate
    SELECT loadboard_rate INTO v_loadboard_rate
    FROM loads WHERE id = p_load_id;
    
    IF v_loadboard_rate IS NULL THEN
        RETURN QUERY SELECT FALSE, NULL::DECIMAL, NULL::DECIMAL, 'Load not found'::TEXT;
        RETURN;
    END IF;
    
    -- Flexibility increases with each round (more willing to negotiate)
    v_flex_percentage := CASE p_round_number
        WHEN 1 THEN 0.05  -- 5% flexibility in round 1
        WHEN 2 THEN 0.10  -- 10% flexibility in round 2
        WHEN 3 THEN 0.15  -- 15% flexibility in round 3
        ELSE 0.15
    END;
    
    v_min_rate := v_loadboard_rate * (1 - v_flex_percentage);
    
    IF p_carrier_offer >= v_min_rate THEN
        -- Accept the offer
        RETURN QUERY SELECT 
            TRUE,
            v_min_rate,
            p_carrier_offer,
            'Offer accepted! Rate of $' || p_carrier_offer || ' is within acceptable range.';
    ELSE
        -- Counter offer - meet halfway between their offer and our minimum
        RETURN QUERY SELECT 
            FALSE,
            v_min_rate,
            ROUND((p_carrier_offer + v_min_rate) / 2, 2),
            'Counter offer: We can do $' || ROUND((p_carrier_offer + v_min_rate) / 2, 2) || 
            '. The listed rate is $' || v_loadboard_rate || '.';
    END IF;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- UPDATE DAILY METRICS FUNCTION
-- Aggregate metrics for a given date
-- ============================================
CREATE OR REPLACE FUNCTION update_daily_metrics(p_date DATE DEFAULT CURRENT_DATE)
RETURNS VOID AS $$
BEGIN
    INSERT INTO daily_metrics (
        date,
        total_calls,
        successful_bookings,
        transferred_calls,
        failed_calls,
        carriers_verified,
        verification_failures,
        total_negotiations,
        avg_negotiation_rounds,
        total_load_value,
        total_agreed_value,
        avg_discount_percentage,
        avg_sentiment_score,
        positive_sentiment_count,
        negative_sentiment_count,
        avg_call_duration_seconds
    )
    SELECT
        p_date,
        COUNT(c.id),
        COUNT(c.id) FILTER (WHERE c.outcome = 'load_booked'),
        COUNT(c.id) FILTER (WHERE c.outcome = 'transferred_to_rep'),
        COUNT(c.id) FILTER (WHERE c.outcome IN ('no_agreement', 'carrier_declined', 'error')),
        COUNT(DISTINCT car.id) FILTER (WHERE car.is_verified = true),
        COUNT(DISTINCT car.id) FILTER (WHERE car.is_verified = false),
        COUNT(n.id),
        AVG(n.round_number),
        COALESCE(SUM(l.loadboard_rate), 0),
        COALESCE(SUM(o.agreed_rate), 0),
        AVG(CASE WHEN o.original_rate > 0 THEN ((o.original_rate - o.agreed_rate) / o.original_rate * 100) END),
        AVG(c.sentiment_score),
        COUNT(c.id) FILTER (WHERE c.sentiment IN ('positive', 'very_positive')),
        COUNT(c.id) FILTER (WHERE c.sentiment IN ('negative', 'very_negative')),
        AVG(c.duration_seconds)
    FROM calls c
    LEFT JOIN carriers car ON c.carrier_id = car.id
    LEFT JOIN negotiations n ON c.id = n.call_id
    LEFT JOIN offers o ON c.id = o.call_id
    LEFT JOIN loads l ON o.load_id = l.id
    WHERE DATE(c.call_start_time) = p_date
    GROUP BY p_date
    ON CONFLICT (date) DO UPDATE SET
        total_calls = EXCLUDED.total_calls,
        successful_bookings = EXCLUDED.successful_bookings,
        transferred_calls = EXCLUDED.transferred_calls,
        failed_calls = EXCLUDED.failed_calls,
        carriers_verified = EXCLUDED.carriers_verified,
        verification_failures = EXCLUDED.verification_failures,
        total_negotiations = EXCLUDED.total_negotiations,
        avg_negotiation_rounds = EXCLUDED.avg_negotiation_rounds,
        total_load_value = EXCLUDED.total_load_value,
        total_agreed_value = EXCLUDED.total_agreed_value,
        avg_discount_percentage = EXCLUDED.avg_discount_percentage,
        avg_sentiment_score = EXCLUDED.avg_sentiment_score,
        positive_sentiment_count = EXCLUDED.positive_sentiment_count,
        negative_sentiment_count = EXCLUDED.negative_sentiment_count,
        avg_call_duration_seconds = EXCLUDED.avg_call_duration_seconds,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- DASHBOARD METRICS VIEW
-- Real-time metrics view for the dashboard
-- ============================================
CREATE OR REPLACE VIEW v_dashboard_metrics AS
SELECT
    -- Today's metrics
    COUNT(c.id) FILTER (WHERE DATE(c.call_start_time) = CURRENT_DATE) AS calls_today,
    COUNT(c.id) FILTER (WHERE DATE(c.call_start_time) = CURRENT_DATE AND c.outcome = 'load_booked') AS bookings_today,
    COUNT(c.id) FILTER (WHERE DATE(c.call_start_time) = CURRENT_DATE AND c.outcome = 'transferred_to_rep') AS transfers_today,
    
    -- This week's metrics
    COUNT(c.id) FILTER (WHERE c.call_start_time >= DATE_TRUNC('week', CURRENT_DATE)) AS calls_this_week,
    COUNT(c.id) FILTER (WHERE c.call_start_time >= DATE_TRUNC('week', CURRENT_DATE) AND c.outcome = 'load_booked') AS bookings_this_week,
    
    -- Overall metrics
    COUNT(c.id) AS total_calls,
    COUNT(c.id) FILTER (WHERE c.outcome = 'load_booked') AS total_bookings,
    COUNT(c.id) FILTER (WHERE c.outcome = 'transferred_to_rep') AS total_transfers,
    
    -- Conversion rates
    ROUND(
        COUNT(c.id) FILTER (WHERE c.outcome IN ('load_booked', 'transferred_to_rep'))::DECIMAL / 
        NULLIF(COUNT(c.id), 0) * 100, 2
    ) AS conversion_rate,
    
    -- Sentiment breakdown
    COUNT(c.id) FILTER (WHERE c.sentiment IN ('positive', 'very_positive')) AS positive_calls,
    COUNT(c.id) FILTER (WHERE c.sentiment = 'neutral') AS neutral_calls,
    COUNT(c.id) FILTER (WHERE c.sentiment IN ('negative', 'very_negative')) AS negative_calls,
    
    -- Average call duration
    ROUND(AVG(c.duration_seconds) / 60.0, 1) AS avg_call_duration_minutes
FROM calls c;

-- ============================================
-- LOAD AVAILABILITY VIEW
-- View of available loads with summary stats
-- ============================================
CREATE OR REPLACE VIEW v_available_loads AS
SELECT
    l.*,
    ROUND(l.loadboard_rate / NULLIF(l.miles, 0), 2) AS rate_per_mile
FROM loads l
WHERE l.status = 'available'
ORDER BY l.pickup_datetime ASC;

-- ============================================
-- CARRIER PERFORMANCE VIEW
-- Track carrier interactions and success rates
-- ============================================
CREATE OR REPLACE VIEW v_carrier_performance AS
SELECT
    car.id,
    car.mc_number,
    car.legal_name,
    COUNT(c.id) AS total_calls,
    COUNT(c.id) FILTER (WHERE c.outcome = 'load_booked') AS successful_bookings,
    AVG(c.sentiment_score) AS avg_sentiment,
    COUNT(o.id) AS total_offers,
    AVG(o.agreed_rate) AS avg_agreed_rate,
    AVG(o.discount_percentage) AS avg_discount_given
FROM carriers car
LEFT JOIN calls c ON car.id = c.carrier_id
LEFT JOIN offers o ON car.id = o.carrier_id
GROUP BY car.id, car.mc_number, car.legal_name;
