from fastapi import APIRouter, HTTPException
from typing import List
import logging

from database import get_supabase
from models import LoadSearchRequest, LoadSearchResponse, Load

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/search", response_model=LoadSearchResponse)
async def search_loads(request: LoadSearchRequest):
    """
    Search for available loads based on criteria.
    Used by HappyRobot agent to find matching loads for carriers.
    """
    try:
        supabase = get_supabase()
        
        query = supabase.table("loads").select("*").eq("status", "available")
        
        if request.origin:
            query = query.ilike("origin", f"%{request.origin}%")
        
        if request.destination:
            query = query.ilike("destination", f"%{request.destination}%")
        
        if request.equipment_type:
            query = query.ilike("equipment_type", f"%{request.equipment_type}%")
        
        if request.pickup_date_from:
            query = query.gte("pickup_datetime", request.pickup_date_from.isoformat())
        
        if request.pickup_date_to:
            query = query.lte("pickup_datetime", request.pickup_date_to.isoformat())
        
        if request.min_rate is not None:
            query = query.gte("loadboard_rate", request.min_rate)
        
        if request.max_rate is not None:
            query = query.lte("loadboard_rate", request.max_rate)
        
        query = query.order("pickup_datetime").limit(request.limit)
        
        result = query.execute()
        
        loads = [Load(**load) for load in result.data]
        
        return LoadSearchResponse(loads=loads, count=len(loads))
        
    except Exception as e:
        logger.error(f"Error searching loads: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching loads: {str(e)}")


@router.get("/{load_id}", response_model=Load)
async def get_load(load_id: str):
    """Get a specific load by ID."""
    try:
        supabase = get_supabase()
        
        result = supabase.table("loads").select("*").eq("load_id", load_id).execute()
        
        if not result.data:
            result = supabase.table("loads").select("*").eq("id", load_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Load not found")
        
        return Load(**result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting load: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting load: {str(e)}")


@router.patch("/{load_id}/status")
async def update_load_status(load_id: str, status: str):
    """Update load status (e.g., when booked)."""
    valid_statuses = ["available", "pending", "booked", "in_transit", "delivered", "cancelled"]
    
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    try:
        supabase = get_supabase()
        
        result = supabase.table("loads").update({"status": status}).eq("load_id", load_id).execute()
        
        if not result.data:
            result = supabase.table("loads").update({"status": status}).eq("id", load_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Load not found")
        
        return {"message": f"Load status updated to {status}", "load_id": load_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating load status: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating load status: {str(e)}")


@router.get("/", response_model=LoadSearchResponse)
async def list_available_loads(limit: int = 20):
    """List all available loads."""
    try:
        supabase = get_supabase()
        
        result = supabase.table("loads")\
            .select("*")\
            .eq("status", "available")\
            .order("pickup_datetime")\
            .limit(limit)\
            .execute()
        
        loads = [Load(**load) for load in result.data]
        
        return LoadSearchResponse(loads=loads, count=len(loads))
        
    except Exception as e:
        logger.error(f"Error listing loads: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing loads: {str(e)}")
