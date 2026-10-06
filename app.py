import streamlit as st
import pandas as pd
import requests

# 1. Configuration (Paste your Supabase credentials here)
SUPABASE_URL = "https://supabase.co*"
SUPABASE_KEY = "YOUR_SUPABASE_ANON_KEY"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}

st.set_page_config(page_title="Smart Vermiwash System", layout="wide")
st.title("🪱 Smart Vermiwash Telemetry Hub")

# Fetch Logs from Database
response = requests.get(SUPABASE_URL, headers=HEADERS)

if response.status_code == 200 and len(response.json()) > 0:
    data = response.json()
    df = pd.DataFrame(data)
    
    # Process timestamps for charting
    df['created_at'] = pd.to_datetime(df['created_at'])
    df = df.sort_values(by='created_at', ascending=False)
    
    # Extract latest readings
    latest_reading = df.iloc[0]
    
    # Metric Layout
    col1, col2 = st.columns(2)
    col1.metric(label="Compost Moisture Level", value=f"{latest_reading['moisture']}%")
    col2.metric(label="Liquid Vermiwash pH", value=f"{latest_reading['ph']}")
    
    st.divider()
    
    # Dynamic Charts
    st.subheader("📊 Historical Trends")
    chart_df = df.set_index('created_at')
    
    tab1, tab2 = st.tabs(["Moisture History", "pH Stability"])
    with tab1:
        st.line_chart(chart_df['moisture'])
    with tab2:
        st.line_chart(chart_df['ph'])
else:
    st.warning("🔄 Database table is live, but waiting for initial sensor logs from the ESP32.")
