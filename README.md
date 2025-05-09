# 🌊 Coastal & Ocean Engineering Toolkit

This is an interactive **Streamlit web application** designed to support engineers and scientists working in the field of **coastal and ocean engineering**. The toolkit offers functionality for tidal analysis, sediment transport estimation, and shoreline change predictions using real-time data and carbonate chemistry calculations.

---

## 📦 Features

1. **Tidal Analysis**  
   - Pulls tide prediction data from the NOAA API  
   - Visualizes tide heights over time  
   - Calculates tidal range

2. **Sediment Transport**  
   - Estimates bedload transport based on flow velocity and median grain size (D50)

3. **Shoreline Change Prediction**  
   - Uses PyCO2SYS to compute the aragonite saturation state (Ωₐ)  
   - Projects shoreline erosion based on user-defined rates

4. **Custom Background**  
   - Add a visually appealing background image via CSS and base64 encoding

---

## 🛠️ Installation

1. **Clone this repository:**

```bash
git clone https://github.com/yourusername/coastal-engineering-toolkit.git
cd coastal-engineering-toolkit
