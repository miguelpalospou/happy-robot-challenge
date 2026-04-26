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


def get_flexibility(request, round_num: int) -> float:
    """Get flexibility for a round. Accepts both round1_flexibility and round1_discount naming.
    Values must be provided via HappyRobot workflow variables — no defaults."""
    def first_set(*vals):
        for v in vals:
            if v is not None:
                return v
        return None

    flexibility_vals = {
        1: first_set(request.round1_flexibility, request.round1_discount),
        2: first_set(request.round2_flexibility, request.round2_discount),
        3: first_set(request.round3_flexibility, request.round3_discount),
    }
    override = flexibility_vals.get(round_num)
    if override is None:
        raise HTTPException(status_code=400, detail=f"round{round_num}_flexibility is required")
    return override


@router.post("/evaluate", response_model=NegotiationEvaluateResponse)
async def evaluate_counter_offer(request: NegotiationEvaluateRequest):
    """
    Evaluate a carrier's counter offer and determine if it's acceptable.
    Returns whether to accept, reject, or make a counter-counter offer.

    Negotiation logic:
    - Broker quotes loadboard_rate to carrier as initial offer
    - Carrier counters HIGHER (wants more money)
    - Broker has a ceiling per round (goes up each round as broker gets more flexible)
    - Round 1: accept if carrier asks <= loadboard * 1.05
    - Round 2: accept if carrier asks <= loadboard * 1.07
    - Round 3: accept if carrier asks <= loadboard * 1.08 (final ceiling)
    """
    logger.info(f"Negotiation request: load_id={request.load_id}, carrier_offer={request.carrier_offer}, round={request.round_number}")
    try:
        supabase = get_supabase()

        load_result = supabase.table("loads")\
            .select("*")\
            .eq("load_id", request.load_id)\
            .execute()

        if not load_result.data:
            load_result = supabase.table("loads")\
                .select("*")\
                .eq("id", request.load_id)\
                .execute()

        if not load_result.data:
            raise HTTPException(status_code=404, detail="Load not found")

        load = load_result.data[0]
        loadboard_rate = float(load["loadboard_rate"])

        # quoted_price = opening offer to carrier (below loadboard by markup_percentage)
        # markup_percentage comes from HappyRobot workflow variable
        markup = request.markup_percentage if request.markup_percentage is not None else 0.0
        quoted_price = round(loadboard_rate * (1 - markup), 2)

        round_num = min(request.round_number, MAX_NEGOTIATION_ROUNDS)
        flexibility = get_flexibility(request, round_num)

        # Ceiling per round = loadboard * (1 - flexibility), goes UP each round
        # Round 1: strictest (highest discount off loadboard)
        # Round 3: loadboard rate itself = absolute ceiling
        max_acceptable = round(loadboard_rate * (1 - flexibility), 2)

        logger.info(f"Round {round_num}: loadboard=${loadboard_rate}, quoted=${quoted_price}, max_acceptable=${max_acceptable}, carrier_offer=${request.carrier_offer}")

        # If no carrier_offer, just return thresholds (used for upfront memory loading)
        if request.carrier_offer is None:
            is_acceptable = False
            suggested_counter = None
            can_continue = True
            message = f"Thresholds loaded. Opening offer: ${quoted_price:.2f}."
        else:
            # Accept if carrier's ask is at or below the ceiling for this round
            is_acceptable = request.carrier_offer <= max_acceptable

            if is_acceptable:
                message = f"Great! We can do ${request.carrier_offer:.2f} for this load."
                suggested_counter = None
            else:
                suggested_counter = max_acceptable

                if round_num < MAX_NEGOTIATION_ROUNDS:
                    message = (
                        f"${request.carrier_offer:.2f} is a bit high for this lane. "
                        f"Best we can do right now is ${max_acceptable:.2f}. Does that work?"
                    )
                else:
                    message = (
                        f"That's our final offer — the most we can pay is ${max_acceptable:.2f} "
                        f"for the {load['miles']} miles from {load['origin']} to {load['destination']}."
                    )

            can_continue = round_num < MAX_NEGOTIATION_ROUNDS and not is_acceptable

        # Pre-calculate all round ceilings so HappyRobot can store them on round 1
        def calc_max(r):
            f = get_flexibility(request, r)
            return round(loadboard_rate * (1 - f), 2)

        all_round_maxes = {
            "round1_max": calc_max(1),
            "round2_max": calc_max(2),
            "round3_max": calc_max(3),
        }

        if request.call_id and request.carrier_offer is not None:
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
            min_acceptable_rate=max_acceptable,
            suggested_counter=suggested_counter,
            message=message,
            round_number=round_num,
            can_continue=can_continue,
            **all_round_maxes
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
