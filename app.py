import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# ThingSpeak Configuration
CHANNEL_ID = "2572257"
READ_API_KEY = "KHO554NBRCHPVLGB"
BASE_URL = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?api_key={READ_API_KEY}"

# Streamlit Configuration
st.set_page_config(
    page_title="Smart Soil Monitor",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Auto-refresh every 30 seconds
st_autorefresh(interval=30000, limit=None, key="data_refresh")

# Modern UI Styling
st.markdown("""
<style>
    /* Main Theme Colors */
    :root {
        --primary-color: #2E7D32;
        --secondary-color: #1B5E20;
        --background-color: #121212;
        --surface-color: #1E1E1E;
        --text-color: #E0E0E0;
        --accent-color: #4CAF50;
    }

    /* Global Styles */
    .main {
        background-color: var(--background-color);
        color: var(--text-color);
    }

    /* Header Styling */
    .dashboard-header {
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    /* Metric Cards */
    .metric-card {
        background: var(--surface-color);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid var(--accent-color);
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    /* Chart Container */
    .chart-container {
        background: var(--surface-color);
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    /* Sidebar Styling */
    .css-1d391kg {
        background-color: var(--surface-color);
    }

    /* Custom Metric Styling */
    .stMetric {
        background-color: var(--surface-color) !important;
        padding: 1rem !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
    }

    /* Text Elements */
    h1, h2, h3 {
        color: var(--text-color) !important;
        font-weight: 600 !important;
    }

    /* Buttons */
    .stButton > button {
        background-color: var(--primary-color) !important;
        color: white !important;
        border-radius: 5px !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.3s ease !important;
    }

    .stButton > button:hover {
        background-color: var(--secondary-color) !important;
        transform: translateY(-2px) !important;
    }
</style>
""", unsafe_allow_html=True)

def fetch_data(results):
    try:
        response = requests.get(BASE_URL, params={"results": results})
        response.raise_for_status()
        data = response.json()
        feeds = data.get("feeds", [])
        
        if feeds:
            df = pd.DataFrame(feeds)
            df["created_at"] = pd.to_datetime(df["created_at"]).dt.tz_convert("Asia/Jakarta")
            
            # Convert numeric columns
            numeric_fields = {
                "field1": "Soil Moisture",
                "field2": "Temperature",
                "field3": "pH",
                "field4": "Conductivity",
                "field5": "Nitrogen",
                "field6": "Phosphorus",
                "field7": "Kalium"
            }
            
            for field in numeric_fields:
                df[field] = pd.to_numeric(df[field], errors="coerce")
            
            # Resample data
            df.set_index("created_at", inplace=True)
            df_resampled = df.resample('10T').mean().reset_index()
            
            return df_resampled
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

def create_chart(data, x_col, y_col, title, y_label, color_scheme=None, range_y=None):
    fig = px.area(
        data,
        x=x_col,
        y=y_col,
        title=title
    )
    
    fig.update_layout(
        title_x=0.5,
        title_font_size=20,
        xaxis_title="Time",
        yaxis_title=y_label,
        template="plotly_dark",
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    
    if range_y:
        fig.update_yaxes(range=range_y)
    
    if color_scheme:
        fig.update_traces(line_color=color_scheme)
    
    return fig

def main():
    # Dashboard Header
    st.markdown("""
        <div class="dashboard-header">
            <h1>🌱 Smart Soil Monitoring System</h1>
            <p>Real-time soil quality monitoring dashboard</p>
        </div>
    """, unsafe_allow_html=True)

    # Sidebar Configuration
    with st.sidebar:
        st.image("cropped-logo-uin.png", width=100)
        st.title("Dashboard Controls")
        results = st.slider("Data Points to Display:", 
                          min_value=100, 
                          max_value=1000, 
                          value=650,
                          step=50)
        st.button("🔄 Refresh Data")

    # Fetch and process data
    data = fetch_data(results)
    if data.empty:
        st.error("⚠️ No data available!")
        return

    # Current Metrics Section
    st.subheader("📊 Current Readings")
    
    # First row - 4 columns
    first_row_cols = st.columns(4)
    first_row_metrics = [
        ("Soil Moisture 💧", f"{data['field1'].iloc[-1]:.1f}%", "60-80%"),
        ("Temperature 🌡️", f"{data['field2'].iloc[-1]:.1f}°C", "22-26°C"),
        ("pH Level 🧪", f"{data['field3'].iloc[-1]:.1f}", "6.0-7.0"),
        ("Conductivity ⚡", f"{data['field4'].iloc[-1]:.1f} µS/cm", "40-65 µS/cm")
    ]
    
    for col, (label, value, ideal) in zip(first_row_cols, first_row_metrics):
        with col:
            st.markdown(f"""
                <div class="metric-card">
                    <h3>{label}</h3>
                    <h2>{value}</h2>
                    <p>Ideal Range: {ideal}</p>
                </div>
            """, unsafe_allow_html=True)
    
    # Second row - 3 columns
    second_row_cols = st.columns(3)
    second_row_metrics = [
        ("Nitrogen 🌿", f"{data['field5'].iloc[-1]:.1f} mg/L", "200-300 mg/L"),
        ("Phosphorus 🍃", f"{data['field6'].iloc[-1]:.1f} mg/L", "190-400 mg/L"),
        ("Kalium 🌱", f"{data['field7'].iloc[-1]:.1f} mg/L", "190-400 mg/L")
    ]
    
    for col, (label, value, ideal) in zip(second_row_cols, second_row_metrics):
        with col:
            st.markdown(f"""
                <div class="metric-card">
                    <h3>{label}</h3>
                    <h2>{value}</h2>
                    <p>Ideal Range: {ideal}</p>
                </div>
            """, unsafe_allow_html=True)

    # Charts
    st.subheader("📈 Sensor Readings Over Time")
    
    # First Row of Charts
    col1, col2 = st.columns(2)
    with col1:
        moisture_chart = create_chart(
            data, "created_at", "field1",
            "Soil Moisture Trends",
            "Moisture (%)",
            "#00BCD4",
            [60, 80]
        )
        st.plotly_chart(moisture_chart, use_container_width=True)

    with col2:
        temp_chart = create_chart(
            data, "created_at", "field2",
            "Temperature Variations",
            "Temperature (°C)",
            "#FF5722",
            [22, 26]
        )
        st.plotly_chart(temp_chart, use_container_width=True)

    # Second Row of Charts
    col3, col4 = st.columns(2)
    with col3:
        ph_chart = create_chart(
            data, "created_at", "field3",
            "pH Level Changes",
            "pH Level",
            "#4CAF50",
            [0, 14]
        )
        st.plotly_chart(ph_chart, use_container_width=True)

    with col4:
        conductivity_chart = create_chart(
            data, "created_at", "field4",
            "Soil Conductivity",
            "Conductivity (µS/cm)",
            "#FFC107",
            [40, 65]
        )
        st.plotly_chart(conductivity_chart, use_container_width=True)

    # NPK Analysis Section
    st.subheader("🧪 NPK Analysis")
    npk_cols = st.columns(3)
    
    with npk_cols[0]:
        nitrogen_chart = create_chart(
            data, "created_at", "field5",
            "Nitrogen Levels",
            "Nitrogen (mg/L)",
            "#9C27B0",
            [200, 300]
        )
        st.plotly_chart(nitrogen_chart, use_container_width=True)

    with npk_cols[1]:
        phosphorus_chart = create_chart(
            data, "created_at", "field6",
            "Phosphorus Levels",
            "Phosphorus (mg/L)",
            "#E91E63",
            [190, 400]
        )
        st.plotly_chart(phosphorus_chart, use_container_width=True)

    with npk_cols[2]:
        kalium_chart = create_chart(
            data, "created_at", "field7",
            "Kalium Levels",
            "Kalium (mg/L)",
            "#3F51B5",
            [190, 400]
        )
        st.plotly_chart(kalium_chart, use_container_width=True)

    # Footer
    st.markdown("""
        <div style="text-align: center; margin-top: 2rem; padding: 1rem; background-color: var(--surface-color); border-radius: 10px;">
            <p>Last Updated: {}</p>
            <p>Smart Soil Monitoring System v2.0</p>
        </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)

if __name__ == "__main__":
    main()