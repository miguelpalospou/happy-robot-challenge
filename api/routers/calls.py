from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Optional
import logging

from database import get_supabase
from models import (
    CallLogRequest, 
    CallUpdateRequest, 
    CallClassifyRequest,
    Call
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/log", response_model=Call)
async def log_call(request: CallLogRequest):
    """
    Log a new inbound call from a carrier.
    Called at the start of each call.
    """
    try:
        supabase = get_supabase()
        
        carrier_id = request.carrier_id
        if request.mc_number and not carrier_id:
            carrier_result = supabase.table("carriers")\
                .select("id")\
                .ilike("mc_number", f"%{request.mc_number}%")\
                .execute()
            if carrier_result.data:
                carrier_id = carrier_result.data[0]["id"]
        
        call_record = {
            "call_id": request.call_id,
            "mc_number": request.mc_number,
            "phone_number": request.phone_number,
            "carrier_id": carrier_id,
            "call_start_time": datetime.utcnow().isoformat()
        }
        
        result = supabase.table("calls").insert(call_record).execute()
        
        return Call(**result.data[0])
        
    except Exception as e:
        logger.error(f"Error logging call: {e}")
        raise HTTPException(status_code=500, detail=f"Error logging call: {str(e)}")


@router.put("/{call_id}", response_model=Call)
async def update_call(call_id: str, request: CallUpdateRequest):
    """Update call details during or after the call."""
    try:
        supabase = get_supabase()
        
        update_data = request.model_dump(exclude_unset=True, exclude_none=True)
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No update data provided")
        
        result = supabase.table("calls")\
            .update(update_data)\
            .eq("call_id", call_id)\
            .execute()
        
        if not result.data:
            result = supabase.table("calls")\
                .update(update_data)\
                .eq("id", call_id)\
                .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Call not found")
        
        return Call(**result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating call: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating call: {str(e)}")


@router.put("/{call_id}/classify")
async def classify_call(call_id: str, request: CallClassifyRequest):
    """
    Classify the call outcome and carrier sentiment.
    Called at the end of each call.
    """
    try:
        supabase = get_supabase()
        
        update_data = {
            "outcome": request.outcome.value,
            "sentiment": request.sentiment.value,
            "call_end_time": datetime.utcnow().isoformat()
        }
        
        if request.sentiment_score is not None:
            update_data["sentiment_score"] = request.sentiment_score
        
        if request.summary:
            update_data["summary"] = request.summary
        
        if request.extracted_data:
            update_data["extracted_data"] = request.extracted_data
        
        result = supabase.table("calls")\
            .update(update_data)\
            .eq("call_id", call_id)\
            .execute()
        
        if not result.data:
            result = supabase.table("calls")\
                .update(update_data)\
                .eq("id", call_id)\
                .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Call not found")
        
        return {
            "message": "Call classified successfully",
            "call_id": call_id,
            "outcome": request.outcome.value,
            "sentiment": request.sentiment.value
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error classifying call: {e}")
        raise HTTPException(status_code=500, detail=f"Error classifying call: {str(e)}")


@router.put("/{call_id}/agreement")
async def record_agreement(
    call_id: str,
    load_id: str,
    agreed_rate: float,
    carrier_name: Optional[str] = None
):
    """
    Record an agreed price and mark call for transfer to sales rep.
    Called when negotiation succeeds.
    """
    try:
        supabase = get_supabase()
        
        update_data = {
            "load_id": load_id,
            "agreed_rate": agreed_rate,
            "carrier_name": carrier_name,
            "transferred_at": datetime.utcnow().isoformat(),
            "outcome": "transferred_to_rep"
        }
        
        result = supabase.table("calls")\
            .update(update_data)\
            .eq("call_id", call_id)\
            .execute()
        
        if not result.data:
            result = supabase.table("calls")\
                .update(update_data)\
                .eq("id", call_id)\
                .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Call not found")
        
        supabase.table("loads")\
            .update({"status": "pending"})\
            .eq("id", load_id)\
            .execute()
        
        return {
            "message": "Agreement recorded, ready for transfer",
            "call_id": call_id,
            "load_id": load_id,
            "agreed_rate": agreed_rate
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recording agreement: {e}")
        raise HTTPException(status_code=500, detail=f"Error recording agreement: {str(e)}")


@router.get("/{call_id}", response_model=Call)
async def get_call(call_id: str):
    """Get call details by ID."""
    try:
        supabase = get_supabase()
        
        result = supabase.table("calls")\
            .select("*")\
            .eq("call_id", call_id)\
            .execute()
        
        if not result.data:
            result = supabase.table("calls")\
                .select("*")\
                .eq("id", call_id)\
                .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Call not found")
        
        return Call(**result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting call: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting call: {str(e)}")


@router.get("/")
async def list_calls(limit: int = 50, outcome: str = None):
    """List recent calls with optional filtering."""
    try:
        supabase = get_supabase()
        
        query = supabase.table("calls").select("*")
        
        if outcome:
            query = query.eq("outcome", outcome)
        
        result = query.order("call_start_time", desc=True).limit(limit).execute()
        
        return {"calls": result.data, "count": len(result.data)}
        
    except Exception as e:
        logger.error(f"Error listing calls: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing calls: {str(e)}")


@router.get("/pending/transfers")
async def list_pending_transfers():
    """List calls that have been transferred and are awaiting sales rep action."""
    try:
        supabase = get_supabase()
        
        result = supabase.table("calls")\
            .select("*, loads(*)")\
            .eq("outcome", "transferred_to_rep")\
            .not_.is_("agreed_rate", "null")\
            .order("transferred_at", desc=True)\
            .execute()
        
        return {"transfers": result.data, "count": len(result.data)}
        
    except Exception as e:
        logger.error(f"Error listing transfers: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing transfers: {str(e)}")
