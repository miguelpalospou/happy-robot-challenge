# Happy Robot Metrics Dashboard

Visual dashboard for the inbound carrier sales automation system.

## Features

- **KPI Cards**: Total calls, conversion rate, revenue, carriers, loads
- **Margin Analysis**: Shows discount % given during negotiations
- **Outcome Distribution**: Pie chart of call outcomes
- **Sentiment Analysis**: Bar chart of carrier sentiment
- **Calls Over Time**: Time series of daily call volume
- **Top Lanes**: Most popular origin → destination routes
- **Equipment Breakdown**: Booked loads by equipment type
- **Negotiation Stats**: Rounds and acceptance rates

## Run Locally

```bash
cd dashboard
pip install -r requirements.txt
streamlit run app.py
```

Opens at: http://localhost:8501

## Deploy to Streamlit Cloud (Free, Always Up)

1. Push your code to GitHub

2. Go to [share.streamlit.io](https://share.streamlit.io)

3. Click "New app"

4. Select:
   - Repository: `your-username/happy-robot-challenge`
   - Branch: `main`
   - Main file path: `dashboard/app.py`

5. Click "Deploy"

Your dashboard will be live at: `https://your-app-name.streamlit.app`

## Configuration

The dashboard connects to the Railway API. To change the API URL, edit `app.py`:

```python
API_URL = "https://happyrobot-production-03c4.up.railway.app"
API_KEY = "hr-carrier-sales-2024"
```

For Streamlit Cloud, you can use secrets instead:
1. Go to app settings → Secrets
2. Add:
```toml
API_URL = "https://your-api-url.railway.app"
API_KEY = "your-api-key"
```

Then update app.py to use:
```python
API_URL = st.secrets.get("API_URL", "default-url")
API_KEY = st.secrets.get("API_KEY", "default-key")
```
