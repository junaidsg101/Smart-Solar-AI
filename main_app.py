# -*- coding: utf-8 -*-
"""
Smart Solar AI — main Streamlit application.

Combines electrical-engineering sizing (support/engineering.py) with
AI/ML forecasting & anomaly detection (support/ml.py) to recommend a
solar + battery system, estimate savings/payback/CO2, and visualize
consumption + predicted generation.
"""

import os
import pandas as pd
import streamlit as st

from support.ui.styling import load_custom_css
from support.ui.components import (
    render_app_header, render_section_header, render_metric_card, render_anomaly_card,
)
from support.visualize.charts import plot_monthly_consumption, plot_solar_generation, plot_forecast
from support.engineering import size_solar_system, estimate_financials, estimate_co2_reduction, SUN_HOURS_BY_LOCATION
from support.ml import forecast_next_month, detect_anomalies, predict_hourly_generation
from support.ai_insights import generate_recommendation_summary

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "datasets.csv")

st.set_page_config(page_title="Smart Solar AI", page_icon="☀️", layout="centered")
load_custom_css()
render_app_header()

# ----------------------------------------------------------------------------
# System Configuration
# ----------------------------------------------------------------------------
render_section_header("🏠 System Configuration", color="orange")

location = st.selectbox("Location", list(SUN_HOURS_BY_LOCATION.keys()), index=0)
bill = st.number_input("Monthly Electricity Bill ($)", min_value=20, max_value=2000, value=250, step=10)
roof_area = st.number_input("Roof Area (sq ft)", min_value=100, max_value=10000, value=500, step=10)
backup_hours = st.slider("Backup Hours Needed", min_value=1, max_value=12, value=4, format="%dh")
critical_load = st.slider("Critical Load (kW)", min_value=1, max_value=10, value=3, format="%dkW")

st.markdown("**Additional Loads**")
c1, c2, c3 = st.columns(3)
with c1:
    ev = st.toggle("Electric Vehicle", value=False)
with c2:
    ac = st.toggle("Air Conditioning", value=True)
with c3:
    pool = st.toggle("Pool Pump", value=False)

generate = st.button("⚡ Generate Recommendation", use_container_width=True, type="primary")

if generate:
    st.session_state["generated"] = True
    st.session_state["inputs"] = dict(
        location=location, bill=bill, roof_area=roof_area,
        backup_hours=backup_hours, critical_load=critical_load,
        ev=ev, ac=ac, pool=pool,
    )
# ----------------------------------------------------------------------------
# Secret settings
# ----------------------------------------------------------------------------
with st.sidebar:
    st.header("Settings")
    api_key = st.secrets.get("API_KEY", "") or os.getenv(
        "API_KEY", "") or st.text_input("API Key", type="password")
    base_url = st.secrets.get("BASE_URL", "") or os.getenv(
        "BASE_URL", "https://api.groq.com/openai/v1")
    model = st.secrets.get("MODEL", "") or os.getenv(
        "MODEL", "llama-3.3-70b-versatile")
# ----------------------------------------------------------------------------
# Recommended System Design
# ----------------------------------------------------------------------------
if st.session_state.get("generated"):
    inputs = st.session_state["inputs"]
    sizing = size_solar_system(**inputs)
    financials = estimate_financials(sizing, inputs["bill"])
    co2_kg = estimate_co2_reduction(sizing)

    render_section_header(
        "Recommended System Design",
        color="teal",
        subtitle=f"{inputs['location']} · Optimized for your needs",
        chip=f"{sizing['num_panels']} panels",
    )

    r1c1, r1c2 = st.columns(2)
    render_metric_card(r1c1, "☀️", "Solar Capacity", f"{sizing['solar_kw']} kW")
    render_metric_card(r1c2, "🔋", "Battery Storage", f"{sizing['battery_kwh']} kWh")
    r2c1, r2c2 = st.columns(2)
    render_metric_card(r2c1, "⚡", "Inverter Size", f"{sizing['inverter_kw']} kW")
    render_metric_card(r2c2, "💰", "Total Investment", f"${sizing['total_cost']:,.0f}")

    st.info(
        f"💵 Est. monthly savings: **${financials['monthly_savings']:,.0f}** • "
        f"Payback: **{financials['payback_years']} yrs** • "
        f"🌱 CO₂ avoided: **{co2_kg:,.0f} kg/yr**"
    )

    with st.expander("💬 AI-generated explanation", expanded=False):
        with st.spinner("Thinking..."):
            summary = generate_recommendation_summary(sizing, financials, co2_kg, inputs)
        st.write(summary)
else:
    sizing = None

# ----------------------------------------------------------------------------
# Consumption history, forecast & anomalies
# ----------------------------------------------------------------------------
df = pd.read_csv(DATA_PATH)

render_section_header("📊 Consumption History", color="orange")
chart_col, anomaly_col = st.columns([2, 1])

with chart_col:
    st.pyplot(plot_monthly_consumption(df), use_container_width=True)

with anomaly_col:
    st.markdown("**Anomaly Detection**")
    anomalies = detect_anomalies(df)
    if anomalies:
        for a in anomalies:
            render_anomaly_card(a["date"], a["severity"], a["note"])
    else:
        st.caption("No significant anomalies detected.")

next_month_kwh = forecast_next_month(df)
st.caption(f"📈 Forecasted consumption next month: **{next_month_kwh} kWh**")
with st.expander("View forecast chart"):
    st.pyplot(plot_forecast(df, next_month_kwh), use_container_width=True)

# ----------------------------------------------------------------------------
# Predicted Solar Generation
# ----------------------------------------------------------------------------
render_section_header("☀️ Predicted Solar Generation", color="teal")
sun_hours = SUN_HOURS_BY_LOCATION.get(location, 5.0)
solar_kw_for_curve = sizing["solar_kw"] if sizing else 4.0
hourly = predict_hourly_generation(sun_hours, solar_kw_for_curve)
st.pyplot(plot_solar_generation(hourly), use_container_width=True)

# ----------------------------------------------------------------------------
# Data export
# ----------------------------------------------------------------------------
st.divider()
st.download_button(
    "⬇️ Download Consumption Data (CSV)",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="smart_solar_consumption.csv",
    mime="text/csv",
    use_container_width=True,
)

st.caption("Smart Solar AI — recommendations are estimates for planning purposes; consult a licensed installer for a final design.")
