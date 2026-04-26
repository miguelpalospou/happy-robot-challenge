from fastapi import APIRouter, HTTPException
import httpx
import logging
import re

from models import CarrierVerifyRequest, CarrierVerifyResponse

router = APIRouter()
logger = logging.getLogger(__name__)

# SAFER website (HTML) - more reliable than API
SAFER_URL = "https://safer.fmcsa.dot.gov/query.asp"


def normalize_mc_number(mc_number: str) -> str:
    """Extract just the numeric part from MC number."""
    numbers = re.sub(r'[^\d]', '', mc_number)
    return numbers


def parse_safer_html(html: str) -> dict:
    """Parse carrier data from SAFER HTML response."""
    data = {}
    
    # Check for inactive/not found
    if 'Record Inactive' in html or 'No records matching' in html:
        data['inactive'] = True
        return data
    
    # Extract Legal Name (format: <A>Legal Name:</A></TH><TD>NAME</TD>)
    match = re.search(r'Legal Name:</[Aa]></TH>\s*<TD[^>]*>([^<&]+)', html, re.IGNORECASE)
    if match:
        data['legal_name'] = match.group(1).strip()
    
    # Extract DBA Name
    match = re.search(r'DBA Name:</[Aa]></TH>\s*<TD[^>]*>([^<&]+)', html, re.IGNORECASE)
    if match:
        dba = match.group(1).strip()
        if dba and dba != '&nbsp;':
            data['dba_name'] = dba
    
    # Extract USDOT Number
    match = re.search(r'USDOT Number:\s*(\d+)', html, re.IGNORECASE)
    if match:
        data['dot_number'] = match.group(1).strip()
    
    # Extract Entity Type
    match = re.search(r'Entity Type:</[Aa]></TH>\s*<TD[^>]*>([^<&]+)', html, re.IGNORECASE)
    if match:
        data['entity_type'] = match.group(1).strip()
    
    # Check for AUTHORIZED in Operating Authority section
    if re.search(r'AUTHORIZED FOR', html, re.IGNORECASE):
        data['operating_status'] = 'AUTHORIZED'
        data['is_authorized'] = True
    elif re.search(r'OUT-OF-SERVICE', html, re.IGNORECASE):
        data['operating_status'] = 'OUT-OF-SERVICE'
        data['is_authorized'] = False
    elif re.search(r'NOT AUTHORIZED', html, re.IGNORECASE):
        data['operating_status'] = 'NOT AUTHORIZED'
        data['is_authorized'] = False
    else:
        data['operating_status'] = 'UNKNOWN'
        data['is_authorized'] = False
    
    return data


async def _verify_carrier_logic(mc_number: str) -> CarrierVerifyResponse:
    """
    Core verification logic - verifies carrier directly via FMCSA SAFER.
    No caching - always queries live data.
    """
    mc_number = normalize_mc_number(mc_number)
    
    if not mc_number:
        raise HTTPException(status_code=400, detail="Invalid MC number format")
    
    # Query SAFER website directly (it's publicly accessible)
    try:
        safer_query = f"{SAFER_URL}?searchtype=ANY&query_type=queryCarrierSnapshot&query_param=MC_MX&query_string={mc_number}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(safer_query, timeout=15.0)
            
            if response.status_code == 200:
                html = response.text
                
                # Parse the HTML
                data = parse_safer_html(html)
                
                # Check for inactive/not found
                if data.get('inactive'):
                    return CarrierVerifyResponse(
                        mc_number=f"MC-{mc_number}",
                        is_verified=False,
                        is_eligible=False,
                        message="Carrier is INACTIVE in FMCSA SAFER database"
                    )
                
                if data.get('legal_name') or data.get('dot_number'):
                    is_authorized = data.get('is_authorized', False)
                    
                    return CarrierVerifyResponse(
                        mc_number=f"MC-{mc_number}",
                        is_verified=True,
                        is_eligible=is_authorized,
                        legal_name=data.get('legal_name'),
                        dba_name=data.get('dba_name'),
                        dot_number=data.get('dot_number'),
                        operating_status=data.get('operating_status', 'UNKNOWN'),
                        entity_type=data.get('entity_type'),
                        message="Carrier verified via FMCSA SAFER" if is_authorized else f"Carrier found but status: {data.get('operating_status', 'UNKNOWN')}"
                    )
            
            logger.warning(f"SAFER query returned status {response.status_code}")
            
    except Exception as e:
        logger.error(f"SAFER error: {e}")
        return CarrierVerifyResponse(
            mc_number=f"MC-{mc_number}",
            is_verified=False,
            is_eligible=False,
            message=f"FMCSA verification failed: {str(e)}"
        )
    
    # If we get here, SAFER didn't return valid data
    return CarrierVerifyResponse(
        mc_number=f"MC-{mc_number}",
        is_verified=False,
        is_eligible=False,
        message="Carrier not found in FMCSA SAFER database"
    )


@router.post("/verify", response_model=CarrierVerifyResponse)
async def verify_carrier_post(request: CarrierVerifyRequest):
    """
    Verify a carrier using their MC number via FMCSA SAFER system.
    POST method - accepts JSON body with mc_number.
    """
    return await _verify_carrier_logic(request.mc_number)


@router.get("/verify/{mc_number}", response_model=CarrierVerifyResponse)
async def verify_carrier_get(mc_number: str):
    """
    Verify a carrier using their MC number via FMCSA SAFER system.
    GET method - accepts mc_number as path parameter.
    """
    return await _verify_carrier_logic(mc_number)


