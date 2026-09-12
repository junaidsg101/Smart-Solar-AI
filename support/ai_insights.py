# -*- coding: utf-8 -*-
"""
Optional natural-language insight generation via an OpenAI-compatible API
(defaults to Groq's OpenAI-compatible endpoint). Fully optional: if no
API key is configured the app still works, just without the AI narrative.
"""

from __future__ import annotations
import os
import streamlit as st


def _get_client():
    try:
        from openai import OpenAI
    except Exception:
        return None, None

    api_key = st.secrets.get("API_KEY", "") or os.getenv("API_KEY", "")
    base_url = st.secrets.get("BASE_URL", "") or os.getenv("BASE_URL", "https://api.groq.com/openai/v1")
    model = st.secrets.get("MODEL", "") or os.getenv("MODEL", "llama-3.3-70b-versatile")

    if not api_key:
        return None, None

    client = OpenAI(api_key=api_key, base_url=base_url)
    return client, model


def generate_recommendation_summary(sizing: dict, financials: dict, co2_kg: float, inputs: dict) -> str:
    """Returns a short, plain-language explanation of the recommendation.
    Falls back to a templated summary if no API key is set."""
    client, model = _get_client()

    fallback = (
        f"Based on your inputs, a {sizing['solar_kw']} kW solar array "
        f"({sizing['num_panels']} panels) paired with a {sizing['battery_kwh']} kWh battery "
        f"should cover your household needs in {inputs.get('location', 'your area')}, "
        f"with roughly {backup_txt(inputs)} of backup power. "
        f"Estimated investment is ${sizing['total_cost']:,.0f}, with a payback period around "
        f"{financials['payback_years']} years and about {co2_kg:,.0f} kg of CO₂ avoided per year."
    )

    if client is None:
        return fallback

    prompt = (
        "You are a friendly solar energy advisor. In 3-4 short sentences, plain language, "
        "no jargon, summarize this recommendation for a homeowner:\n"
        f"Location: {inputs.get('location')}\n"
        f"Solar system: {sizing['solar_kw']} kW ({sizing['num_panels']} panels)\n"
        f"Battery: {sizing['battery_kwh']} kWh\n"
        f"Inverter: {sizing['inverter_kw']} kW\n"
        f"Total investment: ${sizing['total_cost']:,.0f}\n"
        f"Estimated monthly savings: ${financials['monthly_savings']:,.0f}\n"
        f"Payback period: {financials['payback_years']} years\n"
        f"CO2 avoided per year: {co2_kg:,.0f} kg\n"
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a concise, friendly renewable-energy advisor."},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return fallback


def backup_txt(inputs: dict) -> str:
    hours = inputs.get("backup_hours", 4)
    return f"{hours} hour{'s' if hours != 1 else ''}"
