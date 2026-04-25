# Happy Robot - Inbound Carrier Sales Automation

An AI-powered system for automating inbound carrier calls for freight brokerage load sales.

## Overview

This system handles inbound calls from carriers looking to book loads:
- **Carrier Verification** - Validates carriers via FMCSA API using MC numbers
- **Load Matching** - Searches and pitches available loads to carriers
- **Price Negotiation** - Handles up to 3 rounds of negotiation automatically
- **Call Transfer** - Routes agreed deals to sales representatives
- **Analytics** - Dashboard with call metrics, sentiment analysis, and conversion rates

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    HappyRobot Platform                          │
│                    (Inbound AI Agent)                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ Load Search  │  │   FMCSA      │  │    Negotiation       │   │
│  │   Endpoint   │  │ Verification │  │      Engine          │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ Call Logger  │  │  Sentiment   │  │    Metrics           │   │
│  │              │  │  Classifier  │  │    Aggregator        │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Supabase                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐    │
│  │  Loads   │  │ Carriers │  │  Calls   │  │ Negotiations │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘    │
│  ┌──────────┐  ┌──────────────────────────────────────────┐    │
│  │  Offers  │  │          Daily Metrics                   │    │
│  └──────────┘  └──────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Set Up Supabase

1. Create a new project at [supabase.com](https://supabase.com)
2. Go to **SQL Editor** and run the migration files in order:
   - `supabase/migrations/001_initial_schema.sql` - Creates tables
   - `supabase/migrations/002_seed_data.sql` - Adds sample loads
   - `supabase/migrations/003_functions.sql` - Creates search functions and views

3. Get your credentials from **Settings > API**:
   - `SUPABASE_URL` - Your project URL
   - `SUPABASE_SERVICE_KEY` - Service role key (for backend API)

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key
FMCSA_WEBKEY=your-fmcsa-key
API_KEY=your-api-key-for-authentication
```

### 3. Run with Docker

```bash
docker-compose up --build
```

Or run locally:

```bash
cd api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 4. Access the System

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Dashboard**: http://localhost:3000

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/loads/search` | POST | Search available loads |
| `/carriers/verify` | POST | Verify carrier via FMCSA |
| `/negotiations/evaluate` | POST | Evaluate counter offer |
| `/calls/log` | POST | Log call details |
| `/calls/{id}/classify` | PUT | Classify call outcome/sentiment |
| `/metrics/dashboard` | GET | Get dashboard metrics |
| `/metrics/daily` | GET | Get daily metrics |

## Database Schema

### Tables

- **loads** - Available freight loads with all details
- **carriers** - Verified carrier information
- **calls** - Call records with classification
- **negotiations** - Negotiation history (up to 3 rounds)
- **offers** - Agreed deals ready for booking
- **daily_metrics** - Aggregated daily metrics

### Key Functions

- `search_loads()` - Flexible load search with filters
- `evaluate_counter_offer()` - Business logic for negotiations
- `update_daily_metrics()` - Aggregate metrics for reporting

## Negotiation Logic

The system uses a graduated flexibility model:

| Round | Max Discount | Strategy |
|-------|--------------|----------|
| 1 | 5% | Hold firm, emphasize load value |
| 2 | 10% | Show flexibility, find middle ground |
| 3 | 15% | Final offer, maximum flexibility |

If agreement is reached → Transfer to sales rep  
If no agreement after 3 rounds → Log and classify call

## Deployment

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed cloud deployment instructions.

## License

MIT
