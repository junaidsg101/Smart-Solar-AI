# -*- coding: utf-8 -*-
"""Matplotlib/Seaborn chart builders for Smart Solar AI."""

from __future__ import annotations
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("white")
ACCENT_BLUE = "#3b82f6"
ACCENT_TEAL = "#17b892"


def plot_monthly_consumption(df: pd.DataFrame):
    """Horizontal bar chart of monthly kWh consumption (matches app preview)."""
    d = df.copy()
    d["date"] = pd.to_datetime(d["date"])
    d["month"] = d["date"].dt.strftime("%b")
    d["month_num"] = d["date"].dt.month
    monthly = (
        d.groupby(["month_num", "month"])["consumption_kwh"]
        .sum()
        .reset_index()
        .sort_values("month_num")
    )

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.barh(monthly["month"], monthly["consumption_kwh"], color=ACCENT_BLUE, height=0.55)
    ax.invert_yaxis()
    for i, v in enumerate(monthly["consumption_kwh"]):
        ax.text(v + max(monthly["consumption_kwh"]) * 0.01, i, f"{v:.0f} kWh",
                 va="center", fontsize=8, color="#666")
    ax.set_xlabel("kWh")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return fig


def plot_solar_generation(hourly_df: pd.DataFrame):
    """Area chart of predicted solar generation across a representative day."""
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.fill_between(hourly_df["hour"], hourly_df["predicted_kwh"], color=ACCENT_TEAL, alpha=0.25)
    ax.plot(hourly_df["hour"], hourly_df["predicted_kwh"], color=ACCENT_TEAL, linewidth=2)
    ax.set_xlim(0, 23)
    ax.set_xticks([0, 4, 8, 12, 16, 20, 23])
    ax.set_xticklabels(["00:00", "04:00", "08:00", "12:00", "16:00", "20:00", "23:00"])
    ax.set_ylabel("kW")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return fig


def plot_forecast(df: pd.DataFrame, forecast_value: float):
    """Bar chart of historical monthly totals with the forecasted next month appended."""
    d = df.copy()
    d["date"] = pd.to_datetime(d["date"])
    d["month"] = d["date"].dt.strftime("%b")
    d["month_num"] = d["date"].dt.month
    monthly = (
        d.groupby(["month_num", "month"])["consumption_kwh"]
        .sum()
        .reset_index()
        .sort_values("month_num")
    )
    labels = list(monthly["month"]) + ["Forecast"]
    values = list(monthly["consumption_kwh"]) + [forecast_value]
    colors = [ACCENT_BLUE] * len(monthly) + ["#ff8a3d"]

    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.bar(labels, values, color=colors)
    ax.set_ylabel("kWh")
    ax.spines[["top", "right"]].set_visible(False)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", fontsize=8)
    fig.tight_layout()
    return fig
