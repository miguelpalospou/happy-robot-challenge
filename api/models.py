from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


class EquipmentType(str, Enum):
    DRY_VAN = "Dry Van"
    REEFER = "Reefer"
    FLATBED = "Flatbed"
    STEP_DECK = "Step Deck"
    LOWBOY = "Lowboy"


class CallOutcome(str, Enum):
    LOAD_BOOKED = "load_booked"
    TRANSFERRED_TO_REP = "transferred_to_rep"
    NO_AGREEMENT = "no_agreement"
    CARRIER_DECLINED = "carrier_declined"
    NO_MATCHING_LOADS = "no_matching_loads"
    VERIFICATION_FAILED = "verification_failed"
    ABANDONED = "abandoned"
    ERROR = "error"


class Sentiment(str, Enum):
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


class NegotiationStatus(str, Enum):
    PENDING = "pending"
    COUNTER_OFFERED = "counter_offered"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


# Load Models
class LoadSearchRequest(BaseModel):
    origin: Optional[str] = None
    destination: Optional[str] = None
    equipment_type: Optional[str] = None
    pickup_date_from: Optional[datetime] = None
    pickup_date_to: Optional[datetime] = None
    min_rate: Optional[float] = None
    max_rate: Optional[float] = None
    max_miles: Optional[float] = None
    min_miles: Optional[float] = None
    max_weight: Optional[float] = None
    commodity_type: Optional[str] = None
    limit: int = Field(default=10, ge=1, le=50)
    markup_percentage: Optional[float] = Field(None, ge=0, le=1, description="Markup to apply over loadboard rate for quoted price (0.15 = 15%)")


class Load(BaseModel):
    id: str
    load_id: str
    origin: str
    destination: str
    pickup_datetime: datetime
    delivery_datetime: datetime
    equipment_type: str
    loadboard_rate: float
    quoted_price: Optional[float] = None
    notes: Optional[str] = None
    weight: Optional[float] = None
    commodity_type: Optional[str] = None
    num_of_pieces: Optional[int] = None
    miles: Optional[float] = None
    dimensions: Optional[str] = None
    status: str
    assigned_mc_number: Optional[str] = None
    assigned_carrier_name: Optional[str] = None
    booked_at: Optional[datetime] = None


class LoadSearchResponse(BaseModel):
    loads: List[Load]
    count: int


# Carrier Models
class CarrierVerifyRequest(BaseModel):
    mc_number: str = Field(..., description="Motor Carrier number (e.g., 'MC-123456' or '123456')")


class CarrierVerifyResponse(BaseModel):
    mc_number: str
    is_verified: bool
    is_eligible: bool
    legal_name: Optional[str] = None
    dba_name: Optional[str] = None
    dot_number: Optional[str] = None
    operating_status: Optional[str] = None
    entity_type: Optional[str] = None
    message: str


# Negotiation Models
class NegotiationEvaluateRequest(BaseModel):
    load_id: str
    carrier_offer: float = Field(..., gt=0, description="Carrier's offered rate")
    round_number: int = Field(..., ge=1, le=3, description="Current negotiation round (1-3)")
    call_id: Optional[str] = None
    # Configurable thresholds (can be set from HappyRobot workflow variables)
    # Accepts both naming conventions: round1_flexibility and round1_discount
    markup_percentage: Optional[float] = Field(None, ge=0, le=1, description="Markup over loadboard rate to quote carrier (0.15 = 15%)")
    round1_flexibility: Optional[float] = Field(None, ge=0, le=1, description="Round 1 max discount off quoted price")
    round2_flexibility: Optional[float] = Field(None, ge=0, le=1, description="Round 2 max discount off quoted price")
    round3_flexibility: Optional[float] = Field(None, ge=0, le=1, description="Round 3 max discount off quoted price")
    round1_discount: Optional[float] = Field(None, ge=0, le=1, description="Alias for round1_flexibility")
    round2_discount: Optional[float] = Field(None, ge=0, le=1, description="Alias for round2_flexibility")
    round3_discount: Optional[float] = Field(None, ge=0, le=1, description="Alias for round3_discount")


class NegotiationEvaluateResponse(BaseModel):
    is_acceptable: bool
    quoted_price: float
    min_acceptable_rate: float
    suggested_counter: Optional[float] = None
    message: str
    round_number: int
    can_continue: bool = Field(description="Whether more negotiation rounds are available")


class NegotiationCreateRequest(BaseModel):
    call_id: str
    load_id: str
    initial_rate: float
    carrier_offer: Optional[float] = None


# Call Models
class CallLogRequest(BaseModel):
    call_id: str
    mc_number: Optional[str] = None
    phone_number: Optional[str] = None
    carrier_name: Optional[str] = None


class AgreementRequest(BaseModel):
    load_id: str
    agreed_rate: Union[str, float, int]  # Accept string, float, or int
    mc_number: Optional[str] = None
    carrier_name: Optional[str] = None
    dot_number: Optional[str] = None
    operating_status: Optional[str] = None


class CallUpdateRequest(BaseModel):
    call_end_time: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    outcome: Optional[CallOutcome] = None
    sentiment: Optional[Sentiment] = None
    sentiment_score: Optional[float] = Field(None, ge=-1.0, le=1.0)
    transcript: Optional[str] = None
    summary: Optional[str] = None
    recording_url: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None


class CallClassifyRequest(BaseModel):
    outcome: CallOutcome
    sentiment: Sentiment
    sentiment_score: Optional[float] = Field(None, ge=-1.0, le=1.0)
    summary: Optional[str] = None
    transcript: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None


class Call(BaseModel):
    id: str
    call_id: str
    carrier_id: Optional[str] = None
    mc_number: Optional[str] = None
    phone_number: Optional[str] = None
    call_start_time: datetime
    call_end_time: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    outcome: Optional[str] = None
    sentiment: Optional[str] = None
    sentiment_score: Optional[float] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None
    # Agreement fields (when deal is made)
    load_id: Optional[str] = None
    agreed_rate: Optional[float] = None
    carrier_name: Optional[str] = None
    transferred_at: Optional[datetime] = None
