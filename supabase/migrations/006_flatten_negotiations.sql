-- Migration: Flatten negotiations into calls table
-- Removes the negotiations table and adds negotiation tracking fields directly to calls

ALTER TABLE calls
    ADD COLUMN IF NOT EXISTS opening_quote       DECIMAL(10, 2),
    ADD COLUMN IF NOT EXISTS carrier_first_offer DECIMAL(10, 2),
    ADD COLUMN IF NOT EXISTS negotiation_rounds  INTEGER,
    ADD COLUMN IF NOT EXISTS round_closed        INTEGER;

-- Drop negotiations table (no longer needed)
DROP TABLE IF EXISTS negotiations;

-- Update get_negotiation_metrics to read from calls
CREATE OR REPLACE FUNCTION get_negotiation_metrics()
RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    SELECT json_build_object(
        'total_negotiations',   COUNT(*) FILTER (WHERE negotiation_rounds IS NOT NULL),
        'avg_rounds',           ROUND(AVG(negotiation_rounds)::numeric, 1),
        'accepted',             COUNT(*) FILTER (WHERE round_closed IS NOT NULL),
        'round1_closes',        COUNT(*) FILTER (WHERE round_closed = 1),
        'round2_closes',        COUNT(*) FILTER (WHERE round_closed = 2),
        'round3_closes',        COUNT(*) FILTER (WHERE round_closed = 3),
        'acceptance_rate_pct',  ROUND(
            COUNT(*) FILTER (WHERE round_closed IS NOT NULL)::numeric
            / NULLIF(COUNT(*) FILTER (WHERE negotiation_rounds IS NOT NULL), 0) * 100, 2
        ),
        'avg_first_offer',      ROUND(AVG(carrier_first_offer)::numeric, 2),
        'avg_opening_quote',    ROUND(AVG(opening_quote)::numeric, 2)
    ) INTO result
    FROM calls;

    RETURN result;
END;
$$ LANGUAGE plpgsql;
