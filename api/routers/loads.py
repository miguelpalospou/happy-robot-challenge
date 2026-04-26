from fastapi import APIRouter, HTTPException
from typing import List
import logging

from database import get_supabase
from models import LoadSearchRequest, LoadSearchResponse, Load

router = APIRouter()
logger = logging.getLogger(__name__)

# City aliases for fuzzy matching
CITY_ALIASES = {
    # California
    "SF": "San Francisco", "SAN FRAN": "San Francisco", "FRISCO": "San Francisco",
    "LA": "Los Angeles", "L.A.": "Los Angeles",
    "SD": "San Diego", "DIEGO": "San Diego",
    "SAC": "Sacramento", "SACTO": "Sacramento",
    "OAK": "Oakland",
    "SJ": "San Jose", "SAN JO": "San Jose",
    # Texas
    "DFW": "Dallas", "BIG D": "Dallas",
    "HTX": "Houston", "H-TOWN": "Houston",
    "SA": "San Antonio", "SATX": "San Antonio",
    "ATX": "Austin",
    # Other major cities
    "NYC": "New York", "NY": "New York",
    "CHI": "Chicago", "CHITOWN": "Chicago",
    "ATL": "Atlanta",
    "MIA": "Miami",
    "PHX": "Phoenix",
    "DEN": "Denver",
    "SEA": "Seattle",
    "PDX": "Portland",
    "MSP": "Minneapolis",
    "DTW": "Detroit", "DETROIT": "Detroit",
    "BOS": "Boston",
    "PHL": "Philadelphia", "PHILLY": "Philadelphia",
    "CLT": "Charlotte",
    "NASH": "Nashville",
    "MEM": "Memphis",
    "NOLA": "New Orleans", "NO": "New Orleans",
    "OKC": "Oklahoma City",
    "KC": "Kansas City",
    "STL": "St. Louis", "STLOUIS": "St. Louis",
    "INDY": "Indianapolis",
    "CBUS": "Columbus",
    "CLE": "Cleveland",
    "CINCY": "Cincinnati",
    "VEGAS": "Las Vegas", "LV": "Las Vegas",
    "SLC": "Salt Lake City",
    "ABQ": "Albuquerque",
    "JAX": "Jacksonville",
    "TAMPA": "Tampa", "TPA": "Tampa",
    "ORL": "Orlando", "MCO": "Orlando",
}

def expand_city_alias(city: str) -> str:
    """Expand city abbreviations to full names."""
    upper = city.upper().strip()
    return CITY_ALIASES.get(upper, city)


@router.post("/search", response_model=LoadSearchResponse)
async def search_loads(request: LoadSearchRequest):
    """
    Search for available loads based on criteria.
    All parameters are optional - supports partial matching.
    
    Examples:
    - {"origin": "Houston"} - loads from Houston
    - {"origin": "Los Angeles,Sacramento,San Jose"} - loads from multiple cities
    - {"equipment_type": "Reefer"} - refrigerated loads
    - {"origin": "TX", "equipment_type": "Dry Van"} - combine filters
    """
    try:
        supabase = get_supabase()
        
        query = supabase.table("loads").select("*").eq("status", "available")
        
        if request.origin:
            # Support comma-separated origins: "Los Angeles,Sacramento,San Jose"
            # Also expand aliases: "SF" -> "San Francisco", "LA" -> "Los Angeles"
            origins = [expand_city_alias(o.strip()) for o in request.origin.split(",")]
            if len(origins) == 1:
                query = query.ilike("origin", f"%{origins[0]}%")
            else:
                # Build OR filter for multiple origins
                or_filter = ",".join([f"origin.ilike.%{o}%" for o in origins])
                query = query.or_(or_filter)
        
        if request.destination:
            # Support comma-separated destinations + aliases
            destinations = [expand_city_alias(d.strip()) for d in request.destination.split(",")]
            if len(destinations) == 1:
                query = query.ilike("destination", f"%{destinations[0]}%")
            else:
                or_filter = ",".join([f"destination.ilike.%{d}%" for d in destinations])
                query = query.or_(or_filter)
        
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
        
        if request.max_miles is not None:
            query = query.lte("miles", request.max_miles)
        
        if request.min_miles is not None:
            query = query.gte("miles", request.min_miles)
        
        if request.max_weight is not None:
            query = query.lte("weight", request.max_weight)
        
        if request.commodity_type:
            query = query.ilike("commodity_type", f"%{request.commodity_type}%")
        
        query = query.order("pickup_datetime").limit(request.limit)
        
        result = query.execute()

        markup = request.markup_percentage or 0.0
        loads = []
        for load_data in result.data:
            load = Load(**load_data)
            load.quoted_price = round(load.loadboard_rate * (1 + markup), 2)
            loads.append(load)

        return LoadSearchResponse(loads=loads, count=len(loads))
        
    except Exception as e:
        logger.error(f"Error searching loads: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching loads: {str(e)}")



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


# Dynamic routes MUST come AFTER specific routes
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


@router.get("/booked")
async def get_booked_loads(limit: int = 50):
    """Get all booked loads with their assigned carriers."""
    try:
        supabase = get_supabase()
        
        result = supabase.table("loads")\
            .select("*")\
            .eq("status", "booked")\
            .order("booked_at", desc=True)\
            .limit(limit)\
            .execute()
        
        return {
            "booked_loads": result.data,
            "count": len(result.data)
        }
        
    except Exception as e:
        logger.error(f"Error getting booked loads: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting booked loads: {str(e)}")


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
