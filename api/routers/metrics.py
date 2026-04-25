from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import logging

from database import get_supabase

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/dashboard")
async def get_dashboard_metrics():
    """
    Get real-time dashboard metrics computed on-the-fly.
    """
    try:
        supabase = get_supabase()
        
        today = datetime.utcnow().date()
        week_start = today - timedelta(days=today.weekday())
        
        # Get all calls
        all_calls = supabase.table("calls").select("*").execute()
        calls = all_calls.data
        
        # Filter by date
        today_calls = [c for c in calls if c.get("call_start_time", "")[:10] == str(today)]
        week_calls = [c for c in calls if c.get("call_start_time", "")[:10] >= str(week_start)]
        
        def count_outcome(call_list, outcome):
            return len([c for c in call_list if c.get("outcome") == outcome])
        
        def count_sentiment(call_list, sentiments):
            return len([c for c in call_list if c.get("sentiment") in sentiments])
        
        # Calculate averages
        durations = [c.get("duration_seconds") for c in calls if c.get("duration_seconds")]
        avg_duration = sum(durations) / len(durations) / 60 if durations else None
        
        # Calculate conversion rate
        total_booked = count_outcome(calls, "load_booked")
        total_transferred = count_outcome(calls, "transferred_to_rep")
        total_calls = len(calls)
        
        conversion_rate = None
        if total_calls > 0:
            conversion_rate = round((total_booked + total_transferred) / total_calls * 100, 2)
        
        # Calculate total revenue from agreed rates
        agreed_rates = [c.get("agreed_rate") for c in calls if c.get("agreed_rate")]
        total_agreed_value = sum(agreed_rates) if agreed_rates else 0
        
        return {
            "calls_today": len(today_calls),
            "bookings_today": count_outcome(today_calls, "load_booked"),
            "transfers_today": count_outcome(today_calls, "transferred_to_rep"),
            "calls_this_week": len(week_calls),
            "bookings_this_week": count_outcome(week_calls, "load_booked"),
            "total_calls": total_calls,
            "total_bookings": total_booked,
            "total_transfers": total_transferred,
            "conversion_rate": conversion_rate,
            "positive_calls": count_sentiment(calls, ["positive", "very_positive"]),
            "neutral_calls": count_sentiment(calls, ["neutral"]),
            "negative_calls": count_sentiment(calls, ["negative", "very_negative"]),
            "avg_call_duration_minutes": round(avg_duration, 1) if avg_duration else None,
            "total_agreed_value": total_agreed_value
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting metrics: {str(e)}")


@router.get("/summary")
async def get_metrics_summary():
    """Get a high-level summary of all data."""
    try:
        supabase = get_supabase()
        
        calls = supabase.table("calls").select("*").execute().data
        loads = supabase.table("loads").select("*").execute().data
        carriers = supabase.table("carriers").select("*").execute().data
        negotiations = supabase.table("negotiations").select("*").execute().data
        
        # Calculate stats
        total_agreed = sum(c.get("agreed_rate", 0) for c in calls if c.get("agreed_rate"))
        
        return {
            "total_calls": len(calls),
            "total_loads": len(loads),
            "available_loads": len([l for l in loads if l.get("status") == "available"]),
            "verified_carriers": len([c for c in carriers if c.get("is_verified")]),
            "total_negotiations": len(negotiations),
            "successful_transfers": len([c for c in calls if c.get("outcome") == "transferred_to_rep"]),
            "total_agreed_value": total_agreed
        }
        
    except Exception as e:
        logger.error(f"Error getting summary: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting summary: {str(e)}")


@router.get("/negotiations")
async def get_negotiation_stats():
    """Get negotiation statistics."""
    try:
        supabase = get_supabase()
        
        negotiations = supabase.table("negotiations").select("*").execute().data
        
        if not negotiations:
            return {
                "total_negotiations": 0,
                "avg_rounds": None,
                "acceptance_rate": None
            }
        
        # Group by call_id to get rounds per call
        calls_rounds = {}
        for n in negotiations:
            call_id = n.get("call_id")
            if call_id not in calls_rounds:
                calls_rounds[call_id] = []
            calls_rounds[call_id].append(n)
        
        # Calculate stats
        total_rounds = [max(n.get("round_number", 1) for n in rounds) for rounds in calls_rounds.values()]
        avg_rounds = sum(total_rounds) / len(total_rounds) if total_rounds else None
        
        accepted = len([n for n in negotiations if n.get("status") == "accepted"])
        acceptance_rate = round(accepted / len(negotiations) * 100, 2) if negotiations else None
        
        return {
            "total_negotiations": len(negotiations),
            "unique_calls_with_negotiations": len(calls_rounds),
            "avg_rounds_per_call": round(avg_rounds, 1) if avg_rounds else None,
            "acceptance_rate": acceptance_rate,
            "accepted_count": accepted,
            "rejected_count": len([n for n in negotiations if n.get("status") == "rejected"])
        }
        
    except Exception as e:
        logger.error(f"Error getting negotiation stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")
