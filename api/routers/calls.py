from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Optional
import logging

from database import get_supabase
from models import (
    CallLogRequest, 
    CallUpdateRequest, 
    CallClassifyRequest,
    AgreementRequest,
    Call
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/log")
async def log_call(request: CallLogRequest):
    """
    Log a call from a carrier.
    Uses UPSERT - creates new or updates existing call record.
    Called after call ends by HappyRobot.
    """
    try:
        supabase = get_supabase()
        
        call_record = {
            "call_id": request.call_id,
            "mc_number": request.mc_number,
            "phone_number": request.phone_number,
            "carrier_name": request.carrier_name,
        }
        
        # Remove None values
        call_record = {k: v for k, v in call_record.items() if v is not None}
        
        # Try to update existing call first
        result = supabase.table("calls")\
            .update(call_record)\
            .eq("call_id", request.call_id)\
            .execute()
        
        # If no existing call, create new one
        if not result.data:
            call_record["call_start_time"] = datetime.utcnow().isoformat()
            result = supabase.table("calls").insert(call_record).execute()
        
        return {"message": "Call logged", "call_id": request.call_id}
        
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
    Will create call record if it doesn't exist.
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
        
        if request.transcript:
            update_data["transcript"] = request.transcript
        
        # Try to update existing call
        result = supabase.table("calls")\
            .update(update_data)\
            .eq("call_id", call_id)\
            .execute()
        
        # If no call found, create one with classification data
        if not result.data:
            logger.info(f"Call {call_id} not found for classification, creating new record")
            insert_data = {
                "call_id": call_id,
                "call_start_time": datetime.utcnow().isoformat(),
                **update_data
            }
            result = supabase.table("calls").insert(insert_data).execute()
        
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
    request: AgreementRequest
):
    """
    Record an agreed price and mark call for transfer to sales rep.
    Called when negotiation succeeds.
    Accepts JSON body: {"load_id": "...", "agreed_rate": 3500, "carrier_name": "..."}
    load_id can be either UUID or human-readable (e.g., "LD-2024-001")
    Will auto-create a call record if one doesn't exist.
    """
    try:
        supabase = get_supabase()
        
        # Handle agreed_rate as string or number
        agreed_rate = request.agreed_rate
        if isinstance(agreed_rate, str):
            agreed_rate = float(agreed_rate.replace('$', '').replace(',', ''))
        
        # Resolve load_id to UUID if it's human-readable
        load_uuid = request.load_id
        if request.load_id and not request.load_id.startswith(('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f')):
            # Looks like human-readable ID (e.g., "LD-2024-001"), look up UUID
            load_lookup = supabase.table("loads").select("id").eq("load_id", request.load_id).execute()
            if load_lookup.data:
                load_uuid = load_lookup.data[0]["id"]
        
        update_data = {
            "load_id": load_uuid,
            "agreed_rate": agreed_rate,
            "carrier_name": request.carrier_name,
            "mc_number": request.mc_number,
            "transferred_at": datetime.utcnow().isoformat(),
            "outcome": "transferred_to_rep"
        }
        
        # Try to update existing call by call_id (string identifier)
        result = supabase.table("calls")\
            .update(update_data)\
            .eq("call_id", call_id)\
            .execute()
        
        # If no call found, create one
        if not result.data:
            logger.info(f"Call {call_id} not found, creating new record")
            insert_data = {
                "call_id": call_id,
                "load_id": load_uuid,
                "agreed_rate": agreed_rate,
                "carrier_name": request.carrier_name,
                "mc_number": request.mc_number,
                "transferred_at": datetime.utcnow().isoformat(),
                "outcome": "transferred_to_rep",
                "call_start_time": datetime.utcnow().isoformat()
            }
            result = supabase.table("calls").insert(insert_data).execute()
        
        # Update load with carrier assignment
        if load_uuid:
            load_update = {
                "status": "booked",
                "assigned_mc_number": request.mc_number,
                "assigned_carrier_name": request.carrier_name,
                "booked_at": datetime.utcnow().isoformat()
            }
            supabase.table("loads")\
                .update(load_update)\
                .eq("id", load_uuid)\
                .execute()
        
        return {
            "message": "Agreement recorded, load booked",
            "call_id": call_id,
            "load_id": request.load_id,
            "agreed_rate": agreed_rate,
            "carrier_name": request.carrier_name,
            "mc_number": request.mc_number
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
