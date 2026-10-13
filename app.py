import streamlit as st
from supabase import create_client
import pandas as pd

# Page configuration
st.set_page_config(page_title="Soil Moisture Monitor", page_icon="🌱", layout="wide")
st.title("Vermiwash Dashboard")

# Fetch credentials from Streamlit Secrets or hardcode for local testing
SUPABASE_URL = st.secrets.sbURL
SUPABASE_KEY = st.secrets.sbKEY

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# Fetch latest readings
def load_data():
    response = supabase.table("soil_moisture").select("*").order("created_at", desc=True).limit(50).execute()
    data = response.data
    df = pd.DataFrame(data)
    if not df.empty:
        df["created_at"] = pd.to_datetime(df["created_at"])
    return df

df = load_data()

if not df.empty:
    latest = df.iloc[0]
    
    # Display Key Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Latest Moisture Level", value=f"{latest['moisture_percent']}%")
    col2.metric(label="Raw Sensor Value", value=latest['raw_value'])
    col3.metric(label="Last Updated", value=latest['created_at'].strftime("%Y-%m-%d %H:%M:%S"))

    st.divider()

    # Moisture History Line Chart
    st.subheader("Moisture History Trend")
    st.line_chart(df.set_index("created_at")["moisture_percent"])

    # Raw Data Table
    st.subheader("Recent Sensor Logs")
    st.dataframe(df)
else:
    st.info("No sensor readings found in Supabase table yet.")
