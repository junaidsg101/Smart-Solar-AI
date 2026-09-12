# -*- coding: utf-8 -*-
"""
Core electrical-engineering sizing logic for Smart Solar AI.

All formulas here are intentionally guarded against divide-by-zero /
missing-value bugs (the original prototype showed NaN kWh / NaN kW / $NaN
in the recommendation cards because of unguarded divisions) — every
denominator below has a safe floor.
"""

from __future__ import annotations
from typing import Dict

# Average peak-sun-hours per day, by location (rough NREL-style averages).
SUN_HOURS_BY_LOCATION: Dict[str, float] = {
    "San Francisco": 5.5,
    "Los Angeles": 5.9,
    "San Diego": 6.0,
    "Sacramento": 5.8,
    "New York": 4.3,
    "Chicago": 4.4,
    "Houston": 5.0,
    "Phoenix": 6.5,
    "Miami": 5.3,
    "Seattle": 3.8,
    "Denver": 5.6,
    "Austin": 5.4,
}

# Rough average residential utility rate ($/kWh) used to convert a dollar
# bill into an energy estimate when no smart-meter data is available.
DEFAULT_RATE_PER_KWH = 0.28

PANEL_WATTAGE_W = 400          # watts per panel
PANEL_AREA_SQFT = 20           # sq ft footprint per panel (incl. spacing)
SYSTEM_DERATE = 0.80           # inverter/wiring/soiling losses
BATTERY_ROUND_TRIP_EFF = 0.90

COST_PER_WATT_SOLAR = 2.60     # $ per watt installed (panels + install)
COST_PER_KWH_BATTERY = 650.0   # $ per kWh of battery storage
COST_PER_KW_INVERTER = 180.0   # $ per kW of inverter, on top of solar cost

# Extra continuous load added per optional appliance, kW
APPLIANCE_LOADS_KW = {
    "ev": 1.4,        # EV charger, averaged/smoothed load contribution
    "ac": 1.0,         # central air conditioning
    "pool": 0.5,       # pool pump
}

GRID_EMISSION_FACTOR_KG_PER_KWH = 0.40  # US grid average CO2 per kWh avoided


def _safe(value: float, floor: float = 1e-6) -> float:
    """Never let a denominator hit zero (root cause of the old NaN bug)."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return floor
    return v if v > floor else floor


def size_solar_system(location: str, bill: float, roof_area: float,
                       backup_hours: float, critical_load: float,
                       ev: bool = False, ac: bool = False, pool: bool = False,
                       rate_per_kwh: float = DEFAULT_RATE_PER_KWH) -> Dict[str, float]:
    """
    Returns a dict with solar_kw, battery_kwh, inverter_kw, num_panels,
    total_cost, monthly_kwh, and max_panels_by_roof — all guaranteed
    finite numbers (no NaN / inf).
    """
    sun_hours = _safe(SUN_HOURS_BY_LOCATION.get(location, 5.0))
    rate = _safe(rate_per_kwh)

    # 1) Energy usage estimate from the bill.
    monthly_kwh = _safe(bill) / rate
    daily_kwh = monthly_kwh / 30.0

    # 2) Extra continuous load from selected appliances (kW), converted to
    #    an approximate daily kWh addition (assume ~5h/day average use).
    extra_kw = sum(kw for flag, kw in
                   [(ev, APPLIANCE_LOADS_KW["ev"]),
                    (ac, APPLIANCE_LOADS_KW["ac"]),
                    (pool, APPLIANCE_LOADS_KW["pool"])] if flag)
    daily_kwh += extra_kw * 5.0

    # 3) Solar array sizing: daily kWh needed / (sun hours * system derate)
    solar_kw_needed = daily_kwh / (sun_hours * SYSTEM_DERATE)

    # 4) Roof constraint: how much can physically fit?
    max_panels_by_roof = max(1, int(_safe(roof_area) // PANEL_AREA_SQFT))
    max_kw_by_roof = max_panels_by_roof * PANEL_WATTAGE_W / 1000.0

    solar_kw = round(min(solar_kw_needed, max_kw_by_roof) or 0.1, 2)
    solar_kw = max(solar_kw, 0.5)  # never recommend a near-zero system
    num_panels = max(1, round(solar_kw * 1000 / PANEL_WATTAGE_W))

    # 5) Battery sized to cover the critical load for the requested backup
    #    window, accounting for round-trip efficiency.
    battery_kwh = round((_safe(critical_load) * _safe(backup_hours)) /
                         BATTERY_ROUND_TRIP_EFF, 2)

    # 6) Inverter must handle the larger of solar output or critical load,
    #    plus a 20% safety margin.
    inverter_kw = round(max(solar_kw, critical_load) * 1.2, 2)

    # 7) Total investment estimate.
    total_cost = round(
        solar_kw * 1000 * COST_PER_WATT_SOLAR +
        battery_kwh * COST_PER_KWH_BATTERY +
        inverter_kw * COST_PER_KW_INVERTER, 0
    )

    return {
        "solar_kw": solar_kw,
        "battery_kwh": battery_kwh,
        "inverter_kw": inverter_kw,
        "num_panels": int(num_panels),
        "total_cost": total_cost,
        "monthly_kwh": round(monthly_kwh, 1),
        "max_panels_by_roof": max_panels_by_roof,
        "annual_generation_kwh": round(solar_kw * sun_hours * SYSTEM_DERATE * 365, 1),
    }


def estimate_financials(sizing: Dict[str, float], monthly_bill: float) -> Dict[str, float]:
    """Rough payback + savings estimate."""
    annual_gen = _safe(sizing.get("annual_generation_kwh", 0))
    annual_bill = _safe(monthly_bill) * 12
    # Assume solar offsets up to 90% of the bill (net metering, curtailment etc.)
    offset_ratio = min(0.9, annual_gen / _safe(sizing.get("monthly_kwh", 1) * 12))
    annual_savings = round(annual_bill * offset_ratio, 0)
    monthly_savings = round(annual_savings / 12, 0)
    payback_years = round(_safe(sizing.get("total_cost", 0)) / _safe(annual_savings), 1)
    return {
        "annual_savings": annual_savings,
        "monthly_savings": monthly_savings,
        "payback_years": payback_years,
    }


def estimate_co2_reduction(sizing: Dict[str, float]) -> float:
    """kg of CO2 avoided per year."""
    return round(sizing.get("annual_generation_kwh", 0) * GRID_EMISSION_FACTOR_KG_PER_KWH, 0)
