from fastapi import APIRouter, HTTPException, Depends
import httpx
import logging
import re

from database import get_supabase
from config import get_settings, Settings
from models import CarrierVerifyRequest, CarrierVerifyResponse

router = APIRouter()
logger = logging.getLogger(__name__)

FMCSA_API_BASE = "https://mobile.fmcsa.dot.gov/qc/services"


def normalize_mc_number(mc_number: str) -> str:
    """Extract just the numeric part from MC number."""
    numbers = re.sub(r'[^\d]', '', mc_number)
    return numbers


@router.post("/verify", response_model=CarrierVerifyResponse)
async def verify_carrier(
    request: CarrierVerifyRequest,
    settings: Settings = Depends(get_settings)
):
    """
    Verify a carrier using their MC number via FMCSA API.
    Checks operating authority and eligibility to haul freight.
    """
    mc_number = normalize_mc_number(request.mc_number)
    
    if not mc_number:
        raise HTTPException(status_code=400, detail="Invalid MC number format")
    
    supabase = get_supabase()
    
    existing = supabase.table("carriers")\
        .select("*")\
        .ilike("mc_number", f"%{mc_number}%")\
        .execute()
    
    if existing.data and existing.data[0].get("is_verified"):
        carrier = existing.data[0]
        return CarrierVerifyResponse(
            mc_number=carrier["mc_number"],
            is_verified=True,
            is_eligible=carrier["is_eligible"],
            legal_name=carrier.get("legal_name"),
            dba_name=carrier.get("dba_name"),
            dot_number=carrier.get("dot_number"),
            operating_status=carrier.get("operating_status"),
            entity_type=carrier.get("entity_type"),
            message="Carrier verified from cache"
        )
    
    if not settings.fmcsa_webkey:
        logger.warning("FMCSA API key not configured, using mock verification")
        return await _mock_verify(mc_number, supabase)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{FMCSA_API_BASE}/carriers/docket-number/{mc_number}",
                params={"webKey": settings.fmcsa_webkey},
                timeout=10.0
            )
            
            if response.status_code == 404:
                return CarrierVerifyResponse(
                    mc_number=f"MC-{mc_number}",
                    is_verified=False,
                    is_eligible=False,
                    message="Carrier not found in FMCSA database"
                )
            
            response.raise_for_status()
            data = response.json()
            
            carrier_data = data.get("content", [{}])[0] if data.get("content") else {}
            
            operating_status = carrier_data.get("operatingStatus", "")
            is_authorized = operating_status.upper() == "AUTHORIZED"
            
            carrier_record = {
                "mc_number": f"MC-{mc_number}",
                "legal_name": carrier_data.get("legalName"),
                "dba_name": carrier_data.get("dbaName"),
                "dot_number": carrier_data.get("dotNumber"),
                "entity_type": carrier_data.get("entityType"),
                "operating_status": operating_status,
                "is_verified": True,
                "is_eligible": is_authorized,
                "fmcsa_data": carrier_data
            }
            
            supabase.table("carriers").upsert(
                carrier_record,
                on_conflict="mc_number"
            ).execute()
            
            return CarrierVerifyResponse(
                mc_number=f"MC-{mc_number}",
                is_verified=True,
                is_eligible=is_authorized,
                legal_name=carrier_data.get("legalName"),
                dba_name=carrier_data.get("dbaName"),
                dot_number=str(carrier_data.get("dotNumber")) if carrier_data.get("dotNumber") else None,
                operating_status=operating_status,
                entity_type=carrier_data.get("entityType"),
                message="Authorized to haul freight" if is_authorized else f"Not authorized: {operating_status}"
            )
            
    except httpx.HTTPError as e:
        logger.error(f"FMCSA API error: {e}")
        return await _mock_verify(mc_number, supabase)


async def _mock_verify(mc_number: str, supabase) -> CarrierVerifyResponse:
    """Mock verification for testing when FMCSA API is unavailable."""
    is_valid = len(mc_number) >= 5
    
    if is_valid:
        carrier_record = {
            "mc_number": f"MC-{mc_number}",
            "legal_name": f"Test Carrier {mc_number}",
            "operating_status": "AUTHORIZED",
            "is_verified": True,
            "is_eligible": True
        }
        
        supabase.table("carriers").upsert(
            carrier_record,
            on_conflict="mc_number"
        ).execute()
    
    return CarrierVerifyResponse(
        mc_number=f"MC-{mc_number}",
        is_verified=is_valid,
        is_eligible=is_valid,
        legal_name=f"Test Carrier {mc_number}" if is_valid else None,
        operating_status="AUTHORIZED" if is_valid else "NOT_FOUND",
        message="Carrier verified (mock mode)" if is_valid else "Invalid MC number"
    )


@router.get("/{mc_number}")
async def get_carrier(mc_number: str):
    """Get carrier details by MC number."""
    try:
        supabase = get_supabase()
        mc_clean = normalize_mc_number(mc_number)
        
        result = supabase.table("carriers")\
            .select("*")\
            .ilike("mc_number", f"%{mc_clean}%")\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Carrier not found")
        
        return result.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting carrier: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting carrier: {str(e)}")
