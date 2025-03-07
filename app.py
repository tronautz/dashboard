import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime

# Fungsi untuk mengambil data dari ThingSpeak
def fetch_data():
    url = "https://api.thingspeak.com/channels/2572257/feeds.json?api_key=KHO554NBRCHPVLGB&results=50"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        feeds = data["feeds"]
        # Konversi data ke dalam DataFrame
        df = pd.DataFrame(feeds)
        df["Timestamp"] = pd.to_datetime(df["created_at"])
        df["Moisture (%)"] = pd.to_numeric(df["field1"], errors="coerce")
        df["Temperature (°C)"] = pd.to_numeric(df["field2"], errors="coerce")
        return df
    else:
        st.error("Gagal mengambil data dari ThingSpeak!")
        return None

# Fungsi utama aplikasi Streamlit
def main():
    st.title("IoT Monitoring System")
    st.markdown("### Data Monitoring untuk Soil Moisture dan Temperature")
    
    # Ambil data dari ThingSpeak
    df = fetch_data()
    if df is not None:
        # Tampilkan data pada tabel
        st.subheader("Tabel Data")
        st.dataframe(df[["Timestamp", "Moisture (%)", "Temperature (°C)"]])

        # Grafik Moisture
        st.subheader("Grafik Soil Moisture")
        fig_moisture = px.line(df, x="Timestamp", y="Moisture (%)", title="Soil Moisture Over Time")
        fig_moisture.update_layout(
            xaxis_title="Time",
            yaxis_title="Moisture (%)",
            template="plotly_dark",
            yaxis=dict(
                autorange="reversed",  # Membalikkan sumbu Y
                tickformat=".0f"      # Format angka tanpa desimal
            )
        )
        st.plotly_chart(fig_moisture, use_container_width=True)

        # Grafik Temperature
        st.subheader("Grafik Soil Temperature")
        fig_temperature = px.line(df, x="Timestamp", y="Temperature (°C)", title="Soil Temperature Over Time")
        fig_temperature.update_layout(
            xaxis_title="Time",
            yaxis_title="Temperature (°C)",
            template="plotly_dark",
            yaxis=dict(
                autorange="reversed",  # Membalikkan sumbu Y
                tickformat=".0f"      # Format angka tanpa desimal
            )
        )
        st.plotly_chart(fig_temperature, use_container_width=True)

if __name__ == "__main__":
    main()
