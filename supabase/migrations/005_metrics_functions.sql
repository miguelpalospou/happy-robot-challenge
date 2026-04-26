-- Metrics Functions for Scalable Dashboard
-- These run in the database, not in memory

-- Function: Get call metrics
CREATE OR REPLACE FUNCTION get_call_metrics()
RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    SELECT json_build_object(
        'total_calls', COUNT(*),
        'calls_today', COUNT(*) FILTER (WHERE call_start_time::date = CURRENT_DATE),
        'calls_this_week', COUNT(*) FILTER (WHERE call_start_time >= date_trunc('week', CURRENT_DATE)),
        'outcomes', json_build_object(
            'load_booked', COUNT(*) FILTER (WHERE outcome = 'load_booked'),
            'transferred_to_rep', COUNT(*) FILTER (WHERE outcome = 'transferred_to_rep'),
            'no_agreement', COUNT(*) FILTER (WHERE outcome = 'no_agreement'),
            'carrier_declined', COUNT(*) FILTER (WHERE outcome = 'carrier_declined'),
            'no_matching_loads', COUNT(*) FILTER (WHERE outcome = 'no_matching_loads'),
            'verification_failed', COUNT(*) FILTER (WHERE outcome = 'verification_failed')
        ),
        'sentiment', json_build_object(
            'positive', COUNT(*) FILTER (WHERE sentiment IN ('positive', 'very_positive')),
            'neutral', COUNT(*) FILTER (WHERE sentiment = 'neutral'),
            'negative', COUNT(*) FILTER (WHERE sentiment IN ('negative', 'very_negative'))
        ),
        'unique_carriers', COUNT(DISTINCT mc_number),
        'total_agreed_value', COALESCE(SUM(agreed_rate), 0),
        'avg_agreed_rate', ROUND(AVG(agreed_rate)::numeric, 2),
        'successful_deals', COUNT(*) FILTER (WHERE outcome IN ('load_booked', 'transferred_to_rep'))
    ) INTO result
    FROM calls;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Function: Get load metrics
CREATE OR REPLACE FUNCTION get_load_metrics()
RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    SELECT json_build_object(
        'total_loads', COUNT(*),
        'available', COUNT(*) FILTER (WHERE status = 'available'),
        'booked', COUNT(*) FILTER (WHERE status = 'booked'),
        'pending', COUNT(*) FILTER (WHERE status = 'pending'),
        'booking_rate_pct', ROUND(
            COUNT(*) FILTER (WHERE status = 'booked')::numeric / NULLIF(COUNT(*), 0) * 100, 2
        ),
        'equipment_breakdown', (
            SELECT json_object_agg(equipment_type, cnt)
            FROM (
                SELECT equipment_type, COUNT(*) as cnt
                FROM loads
                WHERE status = 'booked'
                GROUP BY equipment_type
            ) eq
        ),
        'avg_loadboard_rate', ROUND(AVG(loadboard_rate)::numeric, 2),
        'rate_range', json_build_object(
            'min', MIN(loadboard_rate),
            'max', MAX(loadboard_rate)
        )
    ) INTO result
    FROM loads;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Function: Get top lanes
CREATE OR REPLACE FUNCTION get_top_lanes(limit_count INT DEFAULT 5)
RETURNS JSON AS $$
BEGIN
    RETURN (
        SELECT json_agg(lane_data)
        FROM (
            SELECT 
                json_build_object(
                    'origin', origin,
                    'destination', destination,
                    'count', COUNT(*),
                    'avg_rate', ROUND(AVG(loadboard_rate)::numeric, 2)
                ) as lane_data
            FROM loads
            WHERE status = 'booked'
            GROUP BY origin, destination
            ORDER BY COUNT(*) DESC
            LIMIT limit_count
        ) lanes
    );
END;
$$ LANGUAGE plpgsql;

-- Function: Get negotiation metrics
CREATE OR REPLACE FUNCTION get_negotiation_metrics()
RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    SELECT json_build_object(
        'total_negotiations', COUNT(*),
        'avg_rounds', ROUND(AVG(round_number)::numeric, 1),
        'accepted', COUNT(*) FILTER (WHERE status = 'accepted'),
        'rejected', COUNT(*) FILTER (WHERE status = 'rejected'),
        'acceptance_rate_pct', ROUND(
            COUNT(*) FILTER (WHERE status = 'accepted')::numeric / NULLIF(COUNT(*), 0) * 100, 2
        )
    ) INTO result
    FROM negotiations;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Function: Get pricing analysis (compares agreed_rate vs loadboard_rate)
CREATE OR REPLACE FUNCTION get_pricing_analysis()
RETURNS JSON AS $$
BEGIN
    RETURN (
        SELECT json_build_object(
            'deals_count', COUNT(*),
            'total_agreed_value', COALESCE(SUM(c.agreed_rate), 0),
            'total_loadboard_value', COALESCE(SUM(l.loadboard_rate), 0),
            'avg_discount_pct', ROUND(
                AVG((1 - c.agreed_rate / NULLIF(l.loadboard_rate, 0)) * 100)::numeric, 2
            ),
            'avg_agreed_rate', ROUND(AVG(c.agreed_rate)::numeric, 2),
            'avg_loadboard_rate', ROUND(AVG(l.loadboard_rate)::numeric, 2)
        )
        FROM calls c
        JOIN loads l ON c.load_id = l.id
        WHERE c.agreed_rate IS NOT NULL
    );
END;
$$ LANGUAGE plpgsql;

-- Master function: Get all dashboard metrics in one call
CREATE OR REPLACE FUNCTION get_dashboard_metrics()
RETURNS JSON AS $$
BEGIN
    RETURN json_build_object(
        'calls', get_call_metrics(),
        'loads', get_load_metrics(),
        'top_lanes', get_top_lanes(5),
        'negotiations', get_negotiation_metrics(),
        'pricing', get_pricing_analysis(),
        'generated_at', NOW()
    );
END;
$$ LANGUAGE plpgsql;
