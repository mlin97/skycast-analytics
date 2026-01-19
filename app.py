import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime, timedelta
from requests.exceptions import Timeout

# --- Page Config ---
st.set_page_config(
    page_title="SkyCast Analytics",
    page_icon="🌤️",
    layout="wide",
)

# --- Design & Styling ---
# Using custom CSS to ensure a "Light Mode" friendly and premium vibe
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
        color: #212529;
    }
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 1px solid #ced4da;
    }
    .stDateInput > div > div > input {
        border-radius: 10px;
    }
    h1, h2, h3 {
        color: #0d6efd;
        font-family: 'Inter', sans-serif;
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Helper Functions ---

@st.cache_data(ttl=3600)
def get_lat_lon(city_name):
    """
    Fetches latitude and longitude for a given city name using Open-Meteo Geocoding API.
    """
    if not city_name:
        return None, None
    try:
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {"name": city_name, "count": 1, "language": "en", "format": "json"}
        # Added timeout to prevent hanging
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "results" in data and data["results"]:
            return data["results"][0]["latitude"], data["results"][0]["longitude"]
        return None, None
    except Exception as e:
        st.error(f"Error finding city '{city_name}': {e}")
        return None, None

@st.cache_data(ttl=3600)
def get_weather_data(lat, lon, start_date, end_date):
    """
    Fetches historical weather data (max temp) for a specific location and date range.
    """
    try:
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "daily": "temperature_2m_max",
            "timezone": "auto"
        }
        # Added timeout to prevent hanging
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        daily_data = data.get("daily", {})
        df = pd.DataFrame({
            "Date": daily_data.get("time", []),
            "Max Temp (°C)": daily_data.get("temperature_2m_max", [])
        })
        return df
    except Timeout:
        st.error(f"⏳ Timeout while fetching data for {lat}, {lon}. The server might be busy.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching weather data: {e}")
        return pd.DataFrame()

# --- Main App Board ---

st.title("🌤️ SkyCast Analytics")
st.markdown("### Compare historical temperature trends between cities")

# --- Inputs Section ---
with st.container():
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        city_a = st.text_input("City A", value="New York")
    
    with col2:
        city_b = st.text_input("City B", value="London")
        
    with col3:
        # Default to last 30 days
        end_date_default = datetime.now().date()
        start_date_default = end_date_default - timedelta(days=30)
        date_range = st.date_input(
            "Select Date Range",
            value=(start_date_default, end_date_default),
            max_value=end_date_default
        )

st.divider()

# --- Data Processing & Display ---

if city_a and city_b and len(date_range) == 2:
    start_date, end_date = date_range

    # Initialize dataframes
    df_a = pd.DataFrame()
    df_b = pd.DataFrame()
    fetch_error = False

    # Using st.status to show explicit progress
    with st.status("Fetching weather data...", expanded=True) as status:
        try:
            # 1. Get Coordinates
            st.write(f"📍 Finding location for {city_a}...")
            lat_a, lon_a = get_lat_lon(city_a)
            
            st.write(f"📍 Finding location for {city_b}...")
            lat_b, lon_b = get_lat_lon(city_b)
            
            if lat_a is None:
                status.update(label="Error Finding Location", state="error")
                st.error(f"Could not find location for City A: {city_a}")
                fetch_error = True
            elif lat_b is None:
                status.update(label="Error Finding Location", state="error")
                st.error(f"Could not find location for City B: {city_b}")
                fetch_error = True
            else:
                # 2. Get Weather Data
                st.write(f"🌤️ Fetching weather history for {city_a}...")
                df_a = get_weather_data(lat_a, lon_a, start_date, end_date)
                
                st.write(f"🌤️ Fetching weather history for {city_b}...")
                df_b = get_weather_data(lat_b, lon_b, start_date, end_date)
                
                if df_a.empty or df_b.empty:
                    status.update(label="No Data Found", state="error")
                    st.warning("Could not retrieve weather data. Please check the city names or try a shorter date range.")
                    fetch_error = True
                else:
                    status.update(label="Data Loaded Successfully!", state="complete", expanded=False)
                    
        except Timeout:
            status.update(label="Connection Timed Out", state="error")
            st.error("The request to the Weather API timed out. Please try again later or assume the server is busy.")
            fetch_error = True
        except Exception as e:
            status.update(label="An Error Occurred", state="error")
            st.error(f"An unexpected error occurred: {e}")
            fetch_error = True

    # --- Visualizations ---
    if not fetch_error and not df_a.empty and not df_b.empty:
        # Merge Data for Charting
        df_a["City"] = city_a
        df_b["City"] = city_b
        
        # Calculate Metrics
        avg_temp_a = df_a["Max Temp (°C)"].mean()
        avg_temp_b = df_b["Max Temp (°C)"].mean()
        
        # Display Metrics
        st.markdown("### 📊 Dataset Overview")
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.metric(label=f"Avg Max Temp ({city_a})", value=f"{avg_temp_a:.1f}°C")
        with m_col2:
            st.metric(label=f"Avg Max Temp ({city_b})", value=f"{avg_temp_b:.1f}°C")
        
        st.divider()

        combined_df = pd.concat([df_a, df_b])
        
        tab1, tab2 = st.tabs(["📈 Temperature Trends", "🔢 Raw Data"])
        
        with tab1:
            fig = px.line(
                combined_df, 
                x="Date", 
                y="Max Temp (°C)", 
                color="City",
                title=f"Max Daily Temperature: {city_a} vs {city_b}",
                markers=True,
                line_shape="spline",
                template="plotly_white",
                # Custom Palette: Neon Blue (#00E5FF) and Sunset Orange (#FF5722)
                color_discrete_sequence=["#00E5FF", "#FF5722"] 
            )
            fig.update_layout(
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            try:
                comparison_df = pd.merge(
                    df_a[["Date", "Max Temp (°C)"]].rename(columns={"Max Temp (°C)": f"{city_a} Temp (°C)"}),
                    df_b[["Date", "Max Temp (°C)"]].rename(columns={"Max Temp (°C)": f"{city_b} Temp (°C)"}),
                    on="Date"
                )
                st.dataframe(comparison_df, use_container_width=True, hide_index=True)
            except Exception as e:
                st.error("Error creating comparison table.")
                st.write(e)

else:
    st.info("Please enter both cities and select a valid date range to view the analytics.")
