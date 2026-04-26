"""
Happy Robot Metrics Dashboard
Deploy to Streamlit Cloud for free hosting
"""
import streamlit as st
import requests
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

# Configuration
API_URL = "https://happyrobot-production-03c4.up.railway.app"
API_KEY = "hr-carrier-sales-2024"

st.set_page_config(
    page_title="Happy Robot Metrics",
    page_icon="🤖",
    layout="wide"
)

def fetch_metrics():
    """Fetch metrics from API"""
    headers = {"X-API-Key": API_KEY}
    
    try:
        # Try dashboard endpoint first (nested structure)
        response = requests.get(f"{API_URL}/metrics/dashboard", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Check if it's nested format (new) or flat format (old)
            if "calls" in data and isinstance(data["calls"], dict):
                return data
            # Flat format - convert to expected structure
            return {"summary": data}
        
        # Fallback to summary endpoint
        response = requests.get(f"{API_URL}/metrics/summary", headers=headers, timeout=10)
        if response.status_code == 200:
            return {"summary": response.json()}
            
    except Exception as e:
        st.error(f"Error fetching metrics: {e}")
    return None

def fetch_calls():
    """Fetch recent calls for time series"""
    headers = {"X-API-Key": API_KEY}
    try:
        response = requests.get(f"{API_URL}/calls/?limit=100", headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json().get("calls", [])
    except:
        pass
    return []

def fetch_loads():
    """Fetch booked loads for margin analysis"""
    headers = {"X-API-Key": API_KEY}
    try:
        # Try booked endpoint first
        response = requests.get(f"{API_URL}/loads/booked?limit=100", headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json().get("booked_loads", [])
    except:
        pass
    
    # Fallback: get loads with status=booked via search
    try:
        response = requests.post(
            f"{API_URL}/loads/search",
            headers=headers,
            json={"status": "booked", "limit": 100},
            timeout=10
        )
        if response.status_code == 200:
            return response.json().get("loads", [])
    except:
        pass
    
    return []

def fetch_margin_from_calls(calls_list):
    """Calculate margin analysis from calls with load data"""
    headers = {"X-API-Key": API_KEY}
    margin_data = []
    
    for call in calls_list:
        agreed_rate = call.get("agreed_rate")
        load_id = call.get("load_id")
        
        if agreed_rate and load_id:
            # Fetch load to get loadboard_rate
            try:
                response = requests.get(f"{API_URL}/loads/{load_id}", headers=headers, timeout=5)
                if response.status_code == 200:
                    load = response.json()
                    loadboard_rate = load.get("loadboard_rate")
                    if loadboard_rate:
                        margin_data.append({
                            "agreed_rate": float(agreed_rate),
                            "loadboard_rate": float(loadboard_rate)
                        })
            except:
                pass
    
    return margin_data

# Header
st.title("🤖 Happy Robot Metrics Dashboard")
st.markdown("**Inbound Carrier Sales Automation** - Real-time metrics")

# Refresh button
col1, col2 = st.columns([6, 1])
with col2:
    if st.button("🔄 Refresh"):
        st.rerun()

st.divider()

# Fetch data
metrics = fetch_metrics()
calls = fetch_calls()
booked_loads = fetch_loads()

if not metrics:
    st.warning("Unable to fetch metrics. Make sure the API is running.")
    st.stop()

# Handle both nested and flat response formats
if "summary" in metrics:
    # Flat format from /metrics/summary or converted /metrics/dashboard
    summary = metrics.get("summary", {})
    calls_data = {
        "total_calls": summary.get("total_calls", 0),
        "calls_today": summary.get("calls_today", 0),
        "successful_deals": summary.get("successful_transfers", 0) or summary.get("booked_loads", 0),
        "unique_carriers": summary.get("verified_carriers", 0),
        "total_agreed_value": summary.get("total_agreed_value", 0),
        "avg_agreed_rate": (summary.get("total_agreed_value", 0) / max(summary.get("successful_transfers", 1), 1)) if summary.get("total_agreed_value") else 0,
        "outcomes": {},
        "sentiment": {}
    }
    loads_data = {
        "total_loads": summary.get("total_loads", 0),
        "available": summary.get("available_loads", 0),
        "booked": summary.get("total_loads", 0) - summary.get("available_loads", 0)
    }
    pricing_data = {}
    negotiations_data = {"total_negotiations": summary.get("total_negotiations", 0)}
    top_lanes = []
else:
    # Nested format
    calls_data = metrics.get("calls", {})
    loads_data = metrics.get("loads", {})
    pricing_data = metrics.get("pricing", {})
    negotiations_data = metrics.get("negotiations", {})
    top_lanes = metrics.get("top_lanes", [])

# === KPI CARDS ===
st.subheader("📊 Key Metrics")
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

with kpi1:
    st.metric(
        "Total Calls",
        calls_data.get("total_calls", 0),
        delta=f"{calls_data.get('calls_today', 0)} today"
    )

with kpi2:
    successful = calls_data.get("successful_deals", 0)
    total = calls_data.get("total_calls", 1)
    rate = round(successful / max(total, 1) * 100, 1)
    st.metric("Conversion Rate", f"{rate}%", delta=f"{successful} deals")

with kpi3:
    st.metric(
        "Total Revenue",
        f"${calls_data.get('total_agreed_value', 0):,.0f}",
        delta=f"Avg ${calls_data.get('avg_agreed_rate', 0):,.0f}/load"
    )

with kpi4:
    st.metric(
        "Unique Carriers",
        calls_data.get("unique_carriers", 0)
    )

with kpi5:
    booked = loads_data.get("booked", 0)
    available = loads_data.get("available", 0)
    st.metric(
        "Loads Booked",
        booked,
        delta=f"{available} available"
    )

st.divider()

# === MARGIN ANALYSIS ===
st.subheader("💰 Negotiation Margin Analysis")

# Calculate margin from booked loads or calls data
total_agreed = 0
total_loadboard = 0
deals_with_margin = 0

# First try from booked loads
if booked_loads:
    for load in booked_loads:
        agreed = load.get("agreed_rate") or 0
        loadboard = load.get("loadboard_rate") or 0
        if agreed > 0 and loadboard > 0:
            total_agreed += agreed
            total_loadboard += loadboard
            deals_with_margin += 1

# If no margin data from loads, try from calls
if deals_with_margin == 0 and calls:
    margin_data = fetch_margin_from_calls(calls)
    for m in margin_data:
        total_agreed += m["agreed_rate"]
        total_loadboard += m["loadboard_rate"]
        deals_with_margin += 1

avg_discount = round((1 - total_agreed / total_loadboard) * 100, 1) if total_loadboard > 0 else None

margin_col1, margin_col2, margin_col3 = st.columns(3)

with margin_col1:
    if avg_discount is not None:
        color = "🟢" if avg_discount <= 5 else "🟡" if avg_discount <= 10 else "🔴"
        st.metric(
            f"{color} Avg Discount Given",
            f"{avg_discount}%",
            delta="Carriers negotiated this off",
            delta_color="inverse"
        )
    else:
        st.metric("Avg Discount Given", "N/A")

with margin_col2:
    margin_lost = total_loadboard - total_agreed if total_loadboard else 0
    st.metric(
        "Total Margin Impact",
        f"-${margin_lost:,.0f}",
        delta="vs Loadboard Rates",
        delta_color="inverse"
    )

with margin_col3:
    if deals_with_margin > 0:
        avg_savings = margin_lost / deals_with_margin
        st.metric(
            "Avg Carrier Savings",
            f"${avg_savings:,.0f}/deal",
            delta=f"Across {deals_with_margin} deals"
        )
    else:
        st.metric("Avg Carrier Savings", "N/A")

# Margin breakdown note
st.caption("""
**Margin Guide:** 🟢 0-5% discount (great) | 🟡 5-10% discount (acceptable) | 🔴 >10% discount (high)
""")

st.divider()

# === CHARTS ROW ===
chart_col1, chart_col2 = st.columns(2)

# Compute outcomes and sentiment from calls data if not in metrics
outcomes = calls_data.get("outcomes", {})
sentiment = calls_data.get("sentiment", {})

if calls and (not outcomes or not any(outcomes.values())):
    outcomes = {}
    sentiment = {}
    for call in calls:
        o = call.get("outcome")
        s = call.get("sentiment")
        if o:
            outcomes[o] = outcomes.get(o, 0) + 1
        if s:
            sentiment[s] = sentiment.get(s, 0) + 1

# Outcome Distribution
with chart_col1:
    st.subheader("📈 Call Outcomes")
    if outcomes and any(outcomes.values()):
        outcome_df = pd.DataFrame([
            {"Outcome": k.replace("_", " ").title(), "Count": v}
            for k, v in outcomes.items() if v > 0
        ])
        fig = px.pie(
            outcome_df, 
            values="Count", 
            names="Outcome",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No call data yet")

# Sentiment Distribution
with chart_col2:
    st.subheader("😊 Carrier Sentiment")
    if sentiment and any(sentiment.values()):
        sentiment_df = pd.DataFrame([
            {"Sentiment": k.title(), "Count": v}
            for k, v in sentiment.items() if v > 0
        ])
        colors = {"Positive": "#4CAF50", "Neutral": "#FFC107", "Negative": "#F44336"}
        fig = px.bar(
            sentiment_df,
            x="Sentiment",
            y="Count",
            color="Sentiment",
            color_discrete_map=colors
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No sentiment data yet")

st.divider()

# === CALLS OVER TIME ===
st.subheader("📅 Calls Over Time")
if calls:
    # Convert to dataframe
    calls_df = pd.DataFrame(calls)
    # Try different timestamp fields
    time_col = None
    for col in ["call_start_time", "created_at", "timestamp"]:
        if col in calls_df.columns:
            time_col = col
            break
    
    if time_col:
        calls_df["datetime"] = pd.to_datetime(calls_df[time_col])
        calls_df["date"] = calls_df["datetime"].dt.date
        daily_calls = calls_df.groupby("date").size().reset_index(name="calls")
        
        fig = px.line(
            daily_calls,
            x="date",
            y="calls",
            markers=True,
            title=""
        )
        fig.update_layout(xaxis_title="Date", yaxis_title="Number of Calls")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No timestamp data available")
else:
    st.info("No calls recorded yet")

st.divider()

# === TOP LANES ===
lanes_col, equipment_col = st.columns(2)

with lanes_col:
    st.subheader("🛣️ Top Lanes")
    if top_lanes:
        for i, lane in enumerate(top_lanes[:5], 1):
            origin = lane.get("origin", "Unknown")
            dest = lane.get("destination", "Unknown")
            count = lane.get("count", 0)
            avg_rate = lane.get("avg_rate", 0)
            st.markdown(f"**{i}. {origin} → {dest}**")
            st.caption(f"{count} bookings | Avg rate: ${avg_rate:,.0f}")
    else:
        st.info("No booked lanes yet")

with equipment_col:
    st.subheader("🚛 Equipment Breakdown")
    equipment = loads_data.get("equipment_breakdown", {})
    if equipment:
        eq_df = pd.DataFrame([
            {"Equipment": k, "Booked": v}
            for k, v in equipment.items()
        ])
        fig = px.bar(
            eq_df,
            x="Equipment",
            y="Booked",
            color="Equipment",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No equipment data yet")

st.divider()

# === NEGOTIATION STATS ===
st.subheader("🤝 Negotiation Statistics")
neg_col1, neg_col2, neg_col3 = st.columns(3)

with neg_col1:
    st.metric(
        "Total Negotiations",
        negotiations_data.get("total_negotiations", 0)
    )

with neg_col2:
    avg_rounds = negotiations_data.get("avg_rounds")
    st.metric(
        "Avg Rounds/Deal",
        f"{avg_rounds}" if avg_rounds else "N/A"
    )

with neg_col3:
    acceptance = negotiations_data.get("acceptance_rate_pct")
    st.metric(
        "Acceptance Rate",
        f"{acceptance}%" if acceptance else "N/A"
    )

# Footer
st.divider()
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Data from Happy Robot API")
