# -*- coding: utf-8 -*-
"""Reusable UI components for Smart Solar AI."""

import streamlit as st


def render_app_header() -> None:
    st.markdown(
        """
        <div class="ssai-header">
            <div class="ssai-header-left">
                <div class="ssai-logo">☀️</div>
                <div>
                    <p class="ssai-title">Smart Solar AI</p>
                    <p class="ssai-subtitle">Intelligent Solar &amp; Battery Sizing</p>
                </div>
            </div>
            <div class="ssai-badge">⚡ Eco Optimized</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(title: str, color: str = "orange", subtitle: str = "", chip: str = "") -> None:
    css_class = "ssai-section-orange" if color == "orange" else "ssai-section-teal"
    sub_html = f'<div class="ssai-section-sub">{subtitle}</div>' if subtitle else ""
    chip_html = f'<div class="ssai-section-chip">{chip}</div>' if chip else ""
    st.markdown(
        f"""
        <div class="{css_class}">
            <div>{title}{sub_html}</div>
            {chip_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(col, icon: str, label: str, value: str) -> None:
    with col:
        st.markdown(
            f"""
            <div class="ssai-metric-card">
                <div class="ssai-metric-icon">{icon}</div>
                <p class="ssai-metric-label">{label}</p>
                <p class="ssai-metric-value">{value}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_anomaly_card(date: str, severity: str, note: str) -> None:
    sev_class = f"ssai-sev-{severity.lower()}"
    st.markdown(
        f"""
        <div class="ssai-anomaly-card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span class="ssai-anomaly-date">{date}</span>
                <span class="{sev_class}">{severity}</span>
            </div>
            <p class="ssai-anomaly-note">{note}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
