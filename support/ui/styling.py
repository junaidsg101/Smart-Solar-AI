# -*- coding: utf-8 -*-
"""Custom CSS styling for Smart Solar AI (Streamlit)."""

import streamlit as st

CUSTOM_CSS = """
<style>
.ssai-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.5rem 0 1rem 0;
}
.ssai-header-left { display: flex; align-items: center; gap: 0.75rem; }
.ssai-logo {
    width: 44px; height: 44px; border-radius: 12px;
    background: linear-gradient(135deg, #ffb56b, #ff8a3d);
    display: flex; align-items: center; justify-content: center;
    font-size: 22px;
}
.ssai-title { font-size: 1.3rem; font-weight: 700; margin: 0; color: inherit; }
.ssai-subtitle { font-size: 0.85rem; color: #8a8a8a; margin: 0; }
.ssai-badge {
    background: #e4f7ec; color: #1f9d55; padding: 4px 12px;
    border-radius: 999px; font-size: 0.8rem; font-weight: 600;
}

.ssai-section-orange, .ssai-section-teal {
    padding: 0.85rem 1.1rem; border-radius: 10px; color: white;
    font-weight: 700; font-size: 1.05rem; margin: 1.1rem 0 1rem 0;
    display: flex; justify-content: space-between; align-items: center;
}
.ssai-section-orange { background: linear-gradient(90deg, #ff8a3d, #ff6a3d); }
.ssai-section-teal { background: linear-gradient(90deg, #17b892, #0e9c86); }
.ssai-section-sub { font-size: 0.78rem; font-weight: 400; opacity: 0.9; }
.ssai-section-chip {
    background: rgba(255,255,255,0.25); padding: 2px 10px;
    border-radius: 999px; font-size: 0.78rem; font-weight: 600;
}

.ssai-metric-card {
    background: rgba(127,127,127,0.06); border-radius: 10px;
    padding: 1rem; margin-bottom: 0.75rem;
}
.ssai-metric-icon { font-size: 1.4rem; }
.ssai-metric-label { font-size: 0.8rem; color: #8a8a8a; margin: 0.35rem 0 0.15rem 0; }
.ssai-metric-value { font-size: 1.35rem; font-weight: 700; margin: 0; }

.ssai-anomaly-card {
    border: 1px solid rgba(127,127,127,0.15); border-radius: 10px;
    padding: 0.75rem 1rem; margin-bottom: 0.6rem;
}
.ssai-anomaly-date { font-weight: 700; font-size: 0.9rem; }
.ssai-anomaly-note { font-size: 0.8rem; color: #8a8a8a; margin: 0.2rem 0; }
.ssai-sev-low { color: #1f9d55; background:#e4f7ec; border-radius:999px; padding:2px 10px; font-size:0.75rem; font-weight:600;}
.ssai-sev-medium { color: #b8860b; background:#fff4d6; border-radius:999px; padding:2px 10px; font-size:0.75rem; font-weight:600;}
.ssai-sev-high { color: #c0392b; background:#fde3e1; border-radius:999px; padding:2px 10px; font-size:0.75rem; font-weight:600;}
</style>
"""


def load_custom_css() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
