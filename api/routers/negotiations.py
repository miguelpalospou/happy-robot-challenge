from fastapi import APIRouter, HTTPException
import logging

from database import get_supabase
from models import (
    NegotiationEvaluateRequest, 
    NegotiationEvaluateResponse,
    NegotiationCreateRequest
)

router = APIRouter()
logger = logging.getLogger(__name__)

MAX_NEGOTIATION_ROUNDS = 3

DEFAULT_MARKUP = 0.0  # No markup by default (quoted = loadboard rate)

# Default flexibility values (can be overridden via HappyRobot workflow variables)
DEFAULT_FLEXIBILITY = {
    1: 0.05,  # 5% off quoted price in round 1
    2: 0.10,  # 10% off quoted price in round 2
    3: 0.15,  # 15% off quoted price in round 3 (final offer)
}


def get_flexibility(request, round_num: int) -> float:
    """Get flexibility for a round, using request params if provided, else defaults."""
    overrides = {
        1: request.round1_flexibility,
        2: request.round2_flexibility,
        3: request.round3_flexibility,
    }
    override = overrides.get(round_num)
    if override is not None:
        return override
    return DEFAULT_FLEXIBILITY.get(round_num, 0.15)


@router.post("/evaluate", response_model=NegotiationEvaluateResponse)
async def evaluate_counter_offer(request: NegotiationEvaluateRequest):
    """
    Evaluate a carrier's counter offer and determine if it's acceptable.
    Returns whether to accept, reject, or make a counter-counter offer.
    
    Negotiation logic:
    - Round 1: Accept if within 5% of loadboard rate
    - Round 2: Accept if within 10% of loadboard rate
    - Round 3: Accept if within 15% of loadboard rate (final offer)
    """
    logger.info(f"Negotiation request: load_id={request.load_id}, carrier_offer={request.carrier_offer}, round={request.round_number}")
    try:
        supabase = get_supabase()
        
        # Try to find load by human-readable load_id first, then by UUID
        load_result = supabase.table("loads")\
            .select("*")\
            .eq("load_id", request.load_id)\
            .execute()
        
        if not load_result.data:
            # Try by UUID if not found by load_id
            load_result = supabase.table("loads")\
                .select("*")\
                .eq("id", request.load_id)\
                .execute()
        
        if not load_result.data:
            raise HTTPException(status_code=404, detail="Load not found")
        
        load = load_result.data[0]
        loadboard_rate = float(load["loadboard_rate"])

        # Calculate quoted price (what agent presents to carrier)
        markup = request.markup_percentage if request.markup_percentage is not None else DEFAULT_MARKUP
        quoted_price = round(loadboard_rate * (1 + markup), 2)

        round_num = min(request.round_number, MAX_NEGOTIATION_ROUNDS)
        flexibility = get_flexibility(request, round_num)

        logger.info(f"Round {round_num}: loadboard=${loadboard_rate}, quoted=${quoted_price}, flexibility={flexibility*100}%")

        # Floor is the higher of (quoted * discount) and loadboard_rate — never go below cost
        discount_floor = quoted_price * (1 - flexibility)
        min_acceptable = round(max(discount_floor, loadboard_rate), 2)

        is_acceptable = request.carrier_offer >= min_acceptable

        if is_acceptable:
            message = f"Great! We can accept ${request.carrier_offer:.2f} for this load."
            suggested_counter = None
        else:
            suggested_counter = round((request.carrier_offer + min_acceptable) / 2, 2)

            if round_num < MAX_NEGOTIATION_ROUNDS:
                message = (
                    f"I appreciate the offer of ${request.carrier_offer:.2f}, but our minimum "
                    f"for this lane is ${min_acceptable:.2f}. How about we meet at ${suggested_counter:.2f}?"
                )
            else:
                message = (
                    f"This is our final offer. The best we can do is ${min_acceptable:.2f}. "
                    f"The load is {load['miles']} miles from {load['origin']} to {load['destination']}."
                )
        
        can_continue = round_num < MAX_NEGOTIATION_ROUNDS and not is_acceptable
        
        if request.call_id:
            negotiation_record = {
                "call_id": request.call_id,
                "load_id": load["id"],
                "round_number": round_num,
                "initial_rate": loadboard_rate,
                "carrier_offer": request.carrier_offer,
                "counter_offer": suggested_counter,
                "final_rate": request.carrier_offer if is_acceptable else None,
                "status": "accepted" if is_acceptable else "counter_offered"
            }
            
            supabase.table("negotiations").insert(negotiation_record).execute()
        
        return NegotiationEvaluateResponse(
            is_acceptable=is_acceptable,
            quoted_price=quoted_price,
            min_acceptable_rate=min_acceptable,
            suggested_counter=suggested_counter,
            message=message,
            round_number=round_num,
            can_continue=can_continue
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error evaluating counter offer: {e}")
        raise HTTPException(status_code=500, detail=f"Error evaluating offer: {str(e)}")


@router.post("/create")
async def create_negotiation(request: NegotiationCreateRequest):
    """Create a new negotiation record."""
    try:
        supabase = get_supabase()
        
        negotiation_record = {
            "call_id": request.call_id,
            "load_id": request.load_id,
            "round_number": 1,
            "initial_rate": request.initial_rate,
            "carrier_offer": request.carrier_offer,
            "status": "pending"
        }
        
        result = supabase.table("negotiations").insert(negotiation_record).execute()
        
        return {"message": "Negotiation created", "negotiation": result.data[0]}
        
    except Exception as e:
        logger.error(f"Error creating negotiation: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating negotiation: {str(e)}")


@router.get("/call/{call_id}")
async def get_negotiations_for_call(call_id: str):
    """Get all negotiation rounds for a call."""
    try:
        supabase = get_supabase()
        
        result = supabase.table("negotiations")\
            .select("*")\
            .eq("call_id", call_id)\
            .order("round_number")\
            .execute()
        
        return {"call_id": call_id, "negotiations": result.data, "total_rounds": len(result.data)}
        
    except Exception as e:
        logger.error(f"Error getting negotiations: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting negotiations: {str(e)}")
