from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import logging

from database import get_supabase

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/dashboard")
async def get_dashboard_metrics():
    """
    Comprehensive dashboard metrics using SQL aggregation.
    Scalable - all computation happens in the database, not in memory.
    """
    try:
        supabase = get_supabase()
        
        # Single database call - all metrics computed in PostgreSQL
        result = supabase.rpc("get_dashboard_metrics").execute()
        
        if result.data:
            return result.data
        
        return {"error": "No data returned from metrics function"}
        
    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting metrics: {str(e)}")


@router.get("/calls")
async def get_call_metrics():
    """Get call metrics only (SQL aggregated)."""
    try:
        supabase = get_supabase()
        result = supabase.rpc("get_call_metrics").execute()
        return result.data if result.data else {}
    except Exception as e:
        logger.error(f"Error getting call metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/loads")  
async def get_load_metrics():
    """Get load metrics only (SQL aggregated)."""
    try:
        supabase = get_supabase()
        result = supabase.rpc("get_load_metrics").execute()
        return result.data if result.data else {}
    except Exception as e:
        logger.error(f"Error getting load metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pricing")
async def get_pricing_analysis():
    """Get pricing analysis - agreed vs loadboard rates (SQL aggregated)."""
    try:
        supabase = get_supabase()
        result = supabase.rpc("get_pricing_analysis").execute()
        return result.data if result.data else {}
    except Exception as e:
        logger.error(f"Error getting pricing analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lanes")
async def get_top_lanes(limit: int = 10):
    """Get top lanes by booking volume (SQL aggregated)."""
    try:
        supabase = get_supabase()
        result = supabase.rpc("get_top_lanes", {"limit_count": limit}).execute()
        return result.data if result.data else []
    except Exception as e:
        logger.error(f"Error getting top lanes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_metrics_summary():
    """Get a high-level summary using SQL functions for efficiency."""
    try:
        supabase = get_supabase()
        
        # Use SQL functions (already deployed in Supabase)
        calls = supabase.rpc("get_call_metrics").execute().data or {}
        loads = supabase.rpc("get_load_metrics").execute().data or {}
        
        booked_loads = loads.get("booked", 0)
        total_calls = calls.get("total_calls", 0)
        
        return {
            "total_calls": total_calls,
            "successful_deals": booked_loads,
            "unique_carriers": calls.get("unique_carriers", 0),
            "total_agreed_value": calls.get("total_agreed_value", 0),
            "total_loads": loads.get("total_loads", 0),
            "available_loads": loads.get("available", 0),
            "booked_loads": booked_loads,
            "conversion_rate_pct": round((booked_loads / max(total_calls, 1)) * 100, 1)
        }
        
    except Exception as e:
        logger.error(f"Error getting summary: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting summary: {str(e)}")


@router.get("/negotiations")
async def get_negotiation_stats():
    """Get negotiation statistics (SQL aggregated)."""
    try:
        supabase = get_supabase()
        result = supabase.rpc("get_negotiation_metrics").execute()
        return result.data if result.data else {
            "total_negotiations": 0,
            "avg_rounds": None,
            "acceptance_rate_pct": None
        }
        
    except Exception as e:
        logger.error(f"Error getting negotiation stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")
