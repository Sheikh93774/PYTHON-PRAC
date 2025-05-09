import streamlit as st
import numpy as np
import pandas as pd
import xarray as xr
import pyco2sys as pyco2
import oceanspy as ospy
import matplotlib.pyplot as plt
from PIL import Image
import base64

# ---- BACKGROUND IMAGE FUNCTION ----
def set_background(image_path):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    page_bg_img = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)

# ---- SETUP PAGE ----
st.set_page_config(page_title="Coastal & Ocean Engineering Toolkit", layout="wide")

# Set background image safely
try:
    set_background("assets/coastal_bg.jpg")  # Make sure this path exists
except FileNotFoundError:
    st.warning("Background image not found. Proceeding without it.")

# ---- TITLE ----
st.markdown("""
    <h1 style='text-align: center; color: white;'>🌊 Coastal & Ocean Engineering Toolkit</h1>
    <p style='text-align: center; color: white;'>Model wave dynamics, sediment transport, and shoreline change using OceanSpy, PyCO2SYS, and SchismPy.</p>
""", unsafe_allow_html=True)

# ---- SIDEBAR ----
module = st.sidebar.radio("Choose Module", ["Wave Modeling", "Sediment Transport", "Shoreline Change Prediction"])

# ---- 1. Wave Modeling ----
if module == "Wave Modeling":
    st.subheader("🌊 Wave Modeling with OceanSpy")
    uploaded_file = st.file_uploader("Upload NetCDF Ocean Model File", type=["nc"])

    if uploaded_file:
        try:
            ds = xr.open_dataset(uploaded_file)
            ods = ospy.OceanDataset(ds)
            st.success("Dataset loaded successfully.")
            st.write("Variables in dataset:", list(ods.dataset.data_vars))

            var = st.selectbox("Select variable to plot", list(ods.dataset.data_vars))
            time_index = st.slider("Time index", 0, len(ods.dataset.time) - 1, 0)

            fig, ax = plt.subplots()
            ods.dataset[var].isel(time=time_index).plot(ax=ax)
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Failed to load dataset with OceanSpy: {e}")

# ---- 2. Sediment Transport ----
elif module == "Sediment Transport":
    st.subheader("🏖️ Sediment Transport Calculator")

    u = st.number_input("Flow velocity (m/s)", value=1.0)
    d50 = st.number_input("Median grain size D50 (mm)", value=0.2)

    if st.button("Calculate Bedload Transport"):
        try:
            rho = 1025  # seawater density (kg/m³)
            g = 9.81    # gravity (m/s²)
            d50_m = d50 / 1000  # mm to meters
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
            result = pyco2.sys(par1=dic, par2=ta, par1_type=2, par2_type=1,
                               salinity=sal, temperature=temp, pressure=0,
                               opt_pH_scale=1, opt_k_carbonic=10)
            omega_arag = result["saturation_aragonite"]
            st.metric("Ωₐ (Aragonite Saturation State)", f"{omega_arag:.2f}")
        except Exception as e:
            st.error(f"Error running PyCO2SYS: {e}")

    st.subheader("Shoreline Erosion Projection")
    year = st.slider("Years to Project", 1, 100, 10)
    erosion_rate = st.number_input("Erosion Rate (m/year)", value=0.5)

    future_change = erosion_rate * year
    st.metric("Projected Shoreline Retreat", f"{future_change:.2f} meters")
