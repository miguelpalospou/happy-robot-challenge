from fastapi import APIRouter, HTTPException
import logging

from database import get_supabase
from models import (
    NegotiationEvaluateRequest, 
    NegotiationEvaluateResponse
)

router = APIRouter()
logger = logging.getLogger(__name__)

MAX_NEGOTIATION_ROUNDS = 3


def round50(value: float) -> float:
    """Round to nearest $50."""
    return round(round(value / 50) * 50, 2)


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
        quoted_price = round50(loadboard_rate * (1 - markup))

        round_num = min(request.round_number, MAX_NEGOTIATION_ROUNDS)
        flexibility = get_flexibility(request, round_num)

        # Ceiling per round = loadboard * (1 - flexibility), goes UP each round
        # Round 1: strictest (highest discount off loadboard)
        # Round 3: loadboard rate itself = absolute ceiling
        max_acceptable = round50(loadboard_rate * (1 - flexibility))

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
            return round50(loadboard_rate * (1 - f))

        all_round_maxes = {
            "round1_max": calc_max(1),
            "round2_max": calc_max(2),
            "round3_max": calc_max(3),
        }

        # Update calls table with negotiation tracking (if call_id provided)
        if request.call_id and request.carrier_offer is not None:
            update_data = {
                "negotiation_rounds": round_num,
                "opening_quote": quoted_price,
            }
            # Track first offer from carrier
            if round_num == 1:
                update_data["carrier_first_offer"] = request.carrier_offer
            # Track which round closed the deal
            if is_acceptable:
                update_data["round_closed"] = round_num
            
            supabase.table("calls").update(update_data).eq("call_id", request.call_id).execute()

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


