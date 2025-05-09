import streamlit as st
import numpy as np
import pandas as pd
import requests
import matplotlib.pyplot as plt
import base64
import os
import PyCO2SYS as pyco2

# ---- BACKGROUND IMAGE FUNCTION ----
def set_background(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
        page_bg_img = f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-attachment: fixed;
        }}
        </style>
        """
        st.markdown(page_bg_img, unsafe_allow_html=True)
    else:
        st.warning("Background image not found. Proceeding without it.")

# ---- SETUP PAGE ----
st.set_page_config(page_title="Coastal & Ocean Engineering Toolkit", layout="wide")

# ---- Set Background ----
set_background("assets/coastal_bg.jpg")

# ---- TITLE ----
st.markdown("""
    <h1 style='text-align: center; color: black; font-weight: bold;'>🌊 Coastal & Ocean Engineering Toolkit</h1>
    <p style='text-align: center; color: black;'>Analyze tides, sediment transport, and shoreline change.</p>
""", unsafe_allow_html=True)

# ---- SIDEBAR ----
module = st.sidebar.radio("Choose Module", ["Tidal Analysis", "Sediment Transport", "Shoreline Change Prediction"])

# ---- 1. Tidal Analysis ----
if module == "Tidal Analysis":
    st.subheader("🌙 Tidal Analysis and Visualization")

    station_id = "9410230"  # San Francisco
    api_key = "YOUR_NOAA_API_KEY"  # Replace with your actual NOAA API Key
    start_date = "2023-05-01"
    end_date = "2023-05-02"

    url = f"https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?begin_date={start_date}&end_date={end_date}&station={station_id}&product=predictions&datum=MLLW&units=english&time_zone=GMT&format=csv&api_key={api_key}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        from io import StringIO
        tide_data = pd.read_csv(StringIO(response.text), skiprows=2)

        # Rename columns safely
        tide_data.columns = [col.strip().lower() for col in tide_data.columns]
        time_col = tide_data.columns[0]
        height_col = tide_data.columns[1]

        st.write("Tidal Predictions Data:", tide_data.head())

        # Plot
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(pd.to_datetime(tide_data[time_col]), tide_data[height_col].astype(float),
                label="Tide Height", color='navy')
        ax.set_title("Tidal Heights Prediction from NOAA API")
        ax.set_xlabel("Time")
        ax.set_ylabel("Tide Height (ft)")
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)

        tidal_range = tide_data[height_col].astype(float).max() - tide_data[height_col].astype(float).min()
        st.metric("Tidal Range", f"{tidal_range:.2f} ft")

    except Exception as e:
        st.error(f"Error fetching or processing tidal data: {e}")

# ---- 2. Sediment Transport ----
elif module == "Sediment Transport":
    st.subheader("🏖️ Sediment Transport Calculator")

    u = st.number_input("Flow velocity (m/s)", value=1.0)
    d50 = st.number_input("Median grain size D50 (mm)", value=0.2)

    if st.button("Calculate Bedload Transport"):
        try:
            rho = 1025
            g = 9.81
            d50_m = d50 / 1000
            tau = rho * g * d50_m * u
            qs = 8 * ((tau - 0.047 * rho * g * d50_m)**1.5)
            st.metric("Sediment Transport Rate", f"{qs:.4f} m³/s/m")
        except Exception as e:
            st.error(f"Error in sediment transport calculation: {e}")

# ---- 3. Shoreline Change Prediction ----
elif module == "Shoreline Change Prediction":
    st.subheader("📉 Shoreline Change Prediction")

    ta = st.number_input("Total Alkalinity (µmol/kg)", value=2300)
    dic = st.number_input("Dissolved Inorganic Carbon (µmol/kg)", value=2000)
    temp = st.number_input("Temperature (°C)", value=20.0)
    sal = st.number_input("Salinity", value=35.0)

    if st.button("Run CO2SYS"):
        try:
            result = pyco2.sys(
                par1=dic, par2=ta, par1_type=2, par2_type=1,
                salinity=sal, temperature=temp, pressure=0,
                opt_pH_scale=1, opt_k_carbonic=10
            )
            omega_arag = result["saturation_aragonite"]
            st.metric("Ωₐ (Aragonite Saturation State)", f"{omega_arag:.2f}")
        except Exception as e:
            st.error(f"Error running PyCO2SYS: {e}")

    st.subheader("Shoreline Erosion Projection")
    year = st.slider("Years to Project", 1, 100, 10)
    erosion_rate = st.number_input("Erosion Rate (m/year)", value=0.5)

    future_change = erosion_rate * year
    st.metric("Projected Shoreline Retreat", f"{future_change:.2f} meters")
