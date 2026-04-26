# Happy Robot - Inbound Carrier Sales Automation

AI-powered system for automating inbound carrier calls for freight brokerage load sales.

## Overview

This system handles inbound calls from carriers looking to book loads:
- **Carrier Verification** - Validates carriers via FMCSA SAFER system (live lookup)
- **Load Matching** - Smart search with fuzzy matching and multi-city support
- **Price Negotiation** - Handles up to 3 rounds of negotiation automatically
- **Call Transfer** - Routes agreed deals to sales representatives
- **Call Logging** - Stores all call data and outcomes

## Architecture

```mermaid
flowchart TB
    subgraph HappyRobot["☎️ HappyRobot Platform"]
        A[Inbound Web Call] --> B[Carrier Sales Agent]
    end
    
    subgraph API["⚡ FastAPI Backend"]
        C[Load Search]
        D[FMCSA Verify]
        E[Negotiation Engine]
        F[Call Management]
    end
    
    subgraph DB["🗄️ Supabase"]
        G[(Loads)]
        H[(Calls)]
        I[(Negotiations)]
    end
    
    B --> C & D & E & F
    C & F --> G
    F --> H
    E --> I
```

## HappyRobot Workflow

The AI agent workflow handles the complete call lifecycle:

```mermaid
flowchart TD
    subgraph CALL["📞 During Call"]
        A[Inbound Web Call] --> B[Carrier Sales Agent]
        B --> C{Carrier Sales Conversation}
        
        C --> T1[🔍 verify_carrier]
        C --> T2[📦 search_loads]
        C --> T3[💰 evaluate_offer]
        C --> T4[✅ record_agreement]
        
        T1 --> W1[GET Verify Carrier]
        T2 --> W2[POST Search Loads]
        T3 --> W3[POST Evaluate Offer]
        T4 --> W4[PUT Record Agreement]
        
        T4 --> TRANSFER[📱 Transfer to Sales Rep]
    end
    
    subgraph POSTCALL["📊 After Call Ends"]
        B --> D[Classify Call Outcome]
        D --> E[🏷️ classify_outcome]
        E --> F[Log Call Webhook]
        F --> G[Classify Call Webhook]
    end
    
    style A fill:#e1f5fe
    style TRANSFER fill:#c8e6c9
    style G fill:#fff3e0
```

## Tools Available to AI Agent

| Tool | Webhook | Purpose |
|------|---------|---------|
| `verify_carrier` | GET `/carriers/verify/{mc}` | Check if carrier is FMCSA authorized |
| `search_loads` | POST `/loads/search` | Find loads matching carrier's criteria |
| `evaluate_offer` | POST `/negotiations/evaluate` | Check if carrier's price offer is acceptable |
| `record_agreement` | PUT `/calls/{id}/agreement` | Lock in deal, book load, prepare transfer |
| `classify_outcome` | PUT `/calls/{id}/classify` | Tag call with outcome and sentiment |

## Data Flow

```mermaid
sequenceDiagram
    participant C as 🚛 Carrier
    participant AI as 🤖 AI Agent
    participant API as ⚡ FastAPI
    participant DB as 🗄️ Database
    
    C->>AI: "Hi, MC number 133655"
    AI->>API: GET /carriers/verify/133655
    API-->>AI: ✅ SCHNEIDER NATIONAL - AUTHORIZED
    
    C->>AI: "Looking for loads from Houston"
    AI->>API: POST /loads/search {origin: "Houston"}
    API-->>AI: 📦 5 loads found
    
    AI->>C: "I have Houston to Dallas, $2,500..."
    C->>AI: "I need $3,000"
    
    AI->>API: POST /negotiations/evaluate {offer: 3000}
    API-->>AI: ✅ Acceptable (within 15%)
    
    AI->>API: PUT /calls/{id}/agreement
    API->>DB: Update calls table
    API->>DB: Update loads (status=booked)
    API-->>AI: 🎉 Agreement recorded
    
    AI->>C: "Great! Transferring you to sales..."
    
    Note over AI,DB: After call ends
    AI->>API: POST /calls/log
    AI->>API: PUT /calls/{id}/classify
    API->>DB: Store outcome + sentiment
```

## Database After Successful Deal

```mermaid
erDiagram
    LOADS {
        uuid id PK
        string load_id "LD-2026-0318"
        string origin "Houston, TX"
        string destination "Dallas, TX"
        decimal loadboard_rate "2500.00"
        string status "booked"
        string assigned_mc_number "133655"
        string assigned_carrier_name "SCHNEIDER"
        timestamp booked_at
    }
    
    CALLS {
        uuid id PK
        string call_id "abc-123"
        string mc_number "133655"
        string carrier_name "SCHNEIDER"
        uuid load_id FK
        decimal agreed_rate "3000.00"
        string outcome "load_booked"
        string sentiment "positive"
    }
    
    NEGOTIATIONS {
        uuid id PK
        uuid call_id FK
        int round_number "1"
        decimal carrier_offer "3000.00"
        string status "accepted"
    }
    
    CALLS ||--o{ NEGOTIATIONS : has
    CALLS ||--o| LOADS : books
```

## API Endpoints

### Base URL
**Production:** `https://happyrobot-production-03c4.up.railway.app`

**Dashboard:** `https://happyrobot-production-03c4.up.railway.app/` (same URL, serves dashboard)

### Authentication
All endpoints require header: `X-API-Key: hr-carrier-sales-2024`

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/carriers/verify/{mc}` | GET | Verify carrier by MC number (live FMCSA lookup) |
| `/loads/search` | POST | Search loads with flexible filters |
| `/loads/{id}` | GET | Get specific load details |
| `/loads/booked` | GET | List all booked loads with carriers |
| `/negotiations/evaluate` | POST | Evaluate carrier counter-offer |
| `/calls/log` | POST | Log/update call record |
| `/calls/{id}/classify` | PUT | Classify call outcome/sentiment |
| `/calls/{id}/agreement` | PUT | Record agreed price + book load |

## Search Features

### Available Filters

```mermaid
mindmap
  root((search_loads))
    Location
      origin
      destination
      multi-city support
    Equipment
      equipment_type
      Dry Van
      Reefer
      Flatbed
    Distance
      max_miles
      min_miles
    Load Details
      max_weight
      commodity_type
    Pricing
      min_rate
      max_rate
    Dates
      pickup_date_from
      pickup_date_to
```

| Parameter | Type | Example | Description |
|-----------|------|---------|-------------|
| `origin` | string | `"Houston"` or `"SF,LA,Phoenix"` | Origin city (supports multiple, comma-separated) |
| `destination` | string | `"Dallas"` or `"NYC,Boston"` | Destination (supports multiple) |
| `equipment_type` | string | `"Dry Van"` | Equipment type |
| `max_miles` | number | `500` | Maximum trip distance |
| `min_miles` | number | `100` | Minimum trip distance |
| `max_weight` | number | `40000` | Maximum load weight |
| `commodity_type` | string | `"produce"` | Commodity type (partial match) |
| `min_rate` | number | `1000` | Minimum rate |
| `max_rate` | number | `5000` | Maximum rate |
| `limit` | number | `10` | Max results (default 10, max 50) |

### Fuzzy City Matching

The search API implements flexible city matching to handle natural conversation:

```mermaid
flowchart TD
    A[User says: 'SF'] --> B{Check CITY_ALIASES}
    B -->|Match found| C[Expand to 'San Francisco']
    B -->|No match| D[Use as-is]
    C --> E[SQL: origin ILIKE '%San Francisco%']
    D --> E
    
    F[User says: 'Houston,Dallas'] --> G[Split by comma]
    G --> H[origin ILIKE '%Houston%' OR origin ILIKE '%Dallas%']
```

#### Alias Dictionary

| Input | Expands To | Reason |
|-------|------------|--------|
| `SF` | San Francisco | Common abbreviation |
| `LA` | Los Angeles | Common abbreviation |
| `NYC` | New York | Airport code style |
| `DFW` | Dallas | Airport code |
| `ATL` | Atlanta | Airport code |
| `CHI` | Chicago | Common abbreviation |
| `HTX` / `HOU` | Houston | Airport codes |
| `NOLA` | New Orleans | Common nickname |
| `VEGAS` | Las Vegas | Colloquial |
| `PHILLY` | Philadelphia | Nickname |
| `INDY` | Indianapolis | Nickname |
| `BMORE` | Baltimore | Nickname |
| `CALI` | California | State abbreviation |

#### Implementation

```python
CITY_ALIASES = {
    "sf": "San Francisco", "la": "Los Angeles", 
    "nyc": "New York", "dfw": "Dallas", ...
}

def expand_city_alias(city: str) -> str:
    return CITY_ALIASES.get(city.lower().strip(), city)

# In search_loads:
if origin:
    cities = [expand_city_alias(c.strip()) for c in origin.split(",")]
    # Build OR query for each city
```

#### Multi-City Search

Carriers often say "I'm near Houston, Dallas, or Austin" - the API handles this:

```json
{"origin": "Houston,Dallas,Austin", "equipment_type": "Dry Van"}
```

Generates SQL:
```sql
WHERE (origin ILIKE '%Houston%' OR origin ILIKE '%Dallas%' OR origin ILIKE '%Austin%')
  AND equipment_type = 'Dry Van'
  AND status = 'available'
```

### Example Searches

```bash
# Multiple origins (carrier near Houston)
{"origin": "Houston,Dallas,Austin,San Antonio", "equipment_type": "Dry Van"}

# Short haul only
{"origin": "SF", "max_miles": 300}

# Specific commodity
{"commodity_type": "produce", "equipment_type": "Reefer"}

# Rate range
{"min_rate": 2000, "max_rate": 4000, "origin": "CA"}
```

## FMCSA Carrier Verification

### How It Works

```mermaid
flowchart LR
    A[MC Number] --> B{SAFER Website}
    B --> C[Parse HTML]
    C --> D{Status?}
    D -->|AUTHORIZED| E[✅ is_eligible: true]
    D -->|NOT AUTHORIZED| F[❌ is_eligible: false]
    D -->|INACTIVE| G[❌ is_eligible: false]
```

### Test MC Numbers

| MC Number | Status | Carrier |
|-----------|--------|---------|
| `133655` | ✅ AUTHORIZED | SCHNEIDER NATIONAL |
| `999999` | ✅ AUTHORIZED | TLA TRUCKING LLC |
| `12345` | ❌ INACTIVE | - |
| `11111` | ❌ INACTIVE | - |

## Negotiation Logic

```mermaid
flowchart TD
    A[Carrier Offer] --> B{Round 1}
    B -->|≥95% of rate| C[✅ Accept]
    B -->|<95%| D{Round 2}
    D -->|≥90% of rate| C
    D -->|<90%| E{Round 3}
    E -->|≥85% of rate| C
    E -->|<85%| F[❌ No Deal]
    
    C --> G[Record Agreement]
    G --> H[Transfer to Sales]
    
    style C fill:#c8e6c9
    style F fill:#ffcdd2
```

| Round | Max Discount | Strategy |
|-------|--------------|----------|
| 1 | 5% | Hold firm, emphasize load value |
| 2 | 10% | Show flexibility, find middle ground |
| 3 | 15% | Final offer, maximum flexibility |

**Example:** Load rate is $3,500
- Round 1: Accept if offer ≥ $3,325 (5% off)
- Round 2: Accept if offer ≥ $3,150 (10% off)
- Round 3: Accept if offer ≥ $2,975 (15% off)

## Database Schema

### Entity Relationship Diagram

```mermaid
erDiagram
    LOADS {
        uuid id PK
        string load_id UK "LD-2026-XXXX"
        string origin "Houston, TX"
        string destination "Dallas, TX"
        timestamp pickup_datetime
        timestamp delivery_datetime
        string equipment_type "Dry Van|Reefer|Flatbed"
        decimal loadboard_rate "2500.00"
        string notes
        decimal weight
        string commodity_type
        int num_of_pieces
        decimal miles
        string dimensions
        string status "available|booked"
        string assigned_mc_number "FK to carrier"
        string assigned_carrier_name
        timestamp booked_at
    }
    
    CALLS {
        uuid id PK
        string call_id UK "HappyRobot run_id"
        string mc_number "Carrier MC"
        string carrier_name
        string phone_number
        timestamp call_start_time
        timestamp call_end_time
        int duration_seconds
        string outcome "load_booked|transferred_to_rep|..."
        string sentiment "positive|neutral|negative"
        decimal sentiment_score
        text transcript
        text summary
        string recording_url
        jsonb extracted_data
        decimal agreed_rate
        uuid load_id FK
        timestamp transferred_at
        timestamp created_at
        timestamp updated_at
    }
    
    NEGOTIATIONS {
        uuid id PK
        uuid call_id FK
        uuid load_id FK
        int round_number "1-3"
        decimal initial_rate
        decimal carrier_offer
        decimal counter_offer
        decimal final_rate
        string status "pending|accepted|rejected"
        timestamp created_at
        timestamp updated_at
    }
    
    CALLS ||--o{ NEGOTIATIONS : "has rounds"
    CALLS ||--o| LOADS : "books"
    NEGOTIATIONS ||--o| LOADS : "for"
```

### Tables Summary

| Table | Purpose | Records |
|-------|---------|---------|
| `loads` | Freight loads inventory | 1000+ diverse routes |
| `calls` | Call records with carrier info, outcomes, sentiment | Per call |
| `negotiations` | Negotiation rounds (max 3 per call) | Per round |

### Database Indexes

Indexes optimize the most frequent queries from HappyRobot tools and dashboard:

```mermaid
flowchart LR
    subgraph "HappyRobot Tool Queries"
        A[search_loads] --> I1[idx_loads_origin]
        A --> I2[idx_loads_destination]
        A --> I3[idx_loads_status]
        A --> I4[idx_loads_pickup]
    end
    
    subgraph "Dashboard Metrics"
        B[get_call_metrics] --> I5[idx_calls_outcome]
        B --> I6[idx_calls_start_time]
        C[get_load_metrics] --> I3
    end
    
    subgraph "Booking Flow"
        D[record_agreement] --> I7[idx_loads_assigned_mc]
    end
```

| Index | Table | Column | Used By |
|-------|-------|--------|---------|
| `idx_loads_status` | loads | status | `search_loads`, dashboard metrics |
| `idx_loads_origin` | loads | origin | `search_loads` (WHERE origin ILIKE) |
| `idx_loads_destination` | loads | destination | `search_loads` |
| `idx_loads_pickup` | loads | pickup_datetime | Date range filters |
| `idx_loads_assigned_mc` | loads | assigned_mc_number | Find carrier's booked loads |
| `idx_calls_outcome` | calls | outcome | Outcome distribution metrics |
| `idx_calls_start_time` | calls | call_start_time | "Calls today", time series |

**Note:** With 1000 loads and few calls, indexes have minimal performance impact. They become critical at 100K+ records.

### Call Outcomes
- `load_booked` - Deal closed
- `transferred_to_rep` - Agreed price, transferred to sales
- `no_agreement` - Negotiation failed
- `carrier_declined` - Carrier not interested
- `no_matching_loads` - No loads for carrier's criteria
- `verification_failed` - MC number invalid

### Sentiment Classification
- `very_positive`, `positive`, `neutral`, `negative`, `very_negative`

## Dashboard & Metrics

The dashboard fetches real-time metrics from PostgreSQL functions for scalability:

```mermaid
flowchart LR
    subgraph Dashboard["📊 Dashboard (Static HTML)"]
        A[KPI Cards]
        B[Charts]
        C[Tables]
    end
    
    subgraph API["⚡ FastAPI"]
        D[/metrics/summary]
        E[/metrics/calls]
        F[/metrics/loads]
        G[/metrics/lanes]
    end
    
    subgraph SQL["🐘 PostgreSQL Functions"]
        H[get_call_metrics]
        I[get_load_metrics]
        J[get_top_lanes]
        K[get_pricing_analysis]
    end
    
    A --> D
    B --> E & F
    C --> G
    
    D --> H & I
    E --> H
    F --> I
    G --> J
```

### SQL Aggregation Functions

All metrics computed in PostgreSQL (not in-memory) for scalability:

| Function | Returns | Used For |
|----------|---------|----------|
| `get_call_metrics()` | total_calls, calls_today, outcomes, sentiment | KPI cards, pie charts |
| `get_load_metrics()` | available, booked, equipment_breakdown | Load stats |
| `get_top_lanes(n)` | Top N origin→destination by bookings | Top lanes table |
| `get_pricing_analysis()` | avg_discount_pct, total_agreed_value | Margin analysis |
| `get_negotiation_metrics()` | total_negotiations, avg_rounds | Negotiation stats |

### Margin Analysis

Tracks negotiation effectiveness:

```
Premium Earned = (agreed_rate / loadboard_rate - 1) × 100%

Example:
  Loadboard rate: $2,000
  Agreed rate:    $3,000
  Premium:        +50% (carriers paying MORE than listed)
```

- **Green (+%)**: Carriers paid above loadboard rate (good!)
- **Red (-%)**: Discount given to carriers

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SUPABASE_URL` | Supabase project URL | Yes |
| `SUPABASE_SERVICE_KEY` | Supabase service role key | Yes |
| `API_KEY` | API authentication key | Yes |

## Deployment

### Railway (Current)

```bash
railway login
railway up
railway domain  # Get public URL
```

### Docker

```bash
docker build -t happy-robot-api .
docker run -p 8000:8000 --env-file .env happy-robot-api
```

## Local Development

```bash
cd api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

## Tech Stack

- **Backend:** FastAPI (Python)
- **Database:** Supabase (PostgreSQL)
- **Deployment:** Railway (Docker)
- **Carrier Verification:** FMCSA SAFER (live lookup)
- **AI Platform:** HappyRobot

## License

MIT
