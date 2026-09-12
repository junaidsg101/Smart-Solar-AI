# Smart Solar AI ☀️🔋

Intelligent solar + battery sizing tool. Combines electrical-engineering
sizing formulas (array size, battery capacity, inverter rating) with
AI/ML (consumption forecasting, anomaly detection, generation prediction)
to give homeowners a personalized, data-driven solar recommendation —
no engineering background required.

## Features

- **System Configuration** — location, monthly bill, roof area, backup
  hours, critical load, and optional appliance loads (EV, AC, pool pump).
- **Recommended System Design** — solar array size (kW + panel count),
  battery storage (kWh), inverter size (kW), and total investment —
  computed with guarded formulas (no more `NaN` results).
- **Financial & environmental insights** — estimated monthly savings,
  payback period, and CO₂ avoided per year.
- **AI-generated explanation** — optional natural-language summary via
  any OpenAI-compatible API (defaults to Groq's endpoint + Llama 3.3).
- **Consumption analytics** — monthly usage chart, next-month forecast
  (scikit-learn linear regression), and anomaly detection
  (IsolationForest) surfaced as flagged dates with severity.
- **Predicted Solar Generation** — hourly generation curve for a
  representative day, using a tiny TensorFlow model when TensorFlow is
  installed, with an automatic physics-based fallback when it isn't.
- **CSV data load/export** — historical data loads from
  `data/datasets.csv`; users can download the dataset from the app.

## Project structure

```
Smart Solar AI/
│
├── main_app.py                 # Main application run, visualization logic, CSV handling
├── README.md                   # Project documentation and setup instructions
├── requirements.txt
├── data/
│   └── datasets.csv            # Daily consumption history used for charts/forecast/anomalies
└── support/
    ├── engineering.py          # Solar/battery/inverter sizing + financial/CO2 formulas
    ├── ml.py                   # Forecasting, anomaly detection, generation prediction
    ├── ai_insights.py          # Optional OpenAI-compatible  narrative summaries
    ├── ui/                     # Custom UI components and CSS styling modules
    │   ├── styling.py
    │   └── components.py
    └── visualize/              # Chart-building logic (matplotlib / seaborn)
        └── charts.py
```

## Setup

1. Create a virtual environment and install dependencies:

   ```bash
   cd "Smart Solar AI"
   python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. (Optional) Add your Groq/OpenAI-compatible API key in
   `.streamlit/secrets.toml`. The app works fine without it — you'll just
   get a templated recommendation summary instead of an AI-generated one.

3. Run the app:

   ```bash
   streamlit run main_app.py
   ```

4. Open the URL Streamlit prints (usually `http://localhost:8501`).

## How the sizing works

- **Energy estimate**: monthly bill ÷ average $/kWh rate → estimated
  monthly/daily usage, plus extra load for any selected appliances.
- **Solar array**: daily kWh needed ÷ (peak sun hours × system derate),
  capped by how many panels physically fit your roof area.
- **Battery**: critical load (kW) × backup hours ÷ round-trip efficiency.
- **Inverter**: 1.2× the larger of solar output or critical load.
- **Cost**: $/watt for panels + $/kWh for battery + $/kW for inverter.
- **Savings/payback/CO₂**: derived from estimated annual generation vs.
  your annual bill, plus a grid emissions factor.

All formulas floor their denominators to avoid the divide-by-zero bug
that caused `NaN kWh` / `NaN kW` / `$NaN` in the original prototype.

## Notes

- `tensorflow` is optional at runtime — if it's not installed (or fails
  to import), the app automatically uses a lightweight physics-based
  generation curve instead, so the app never crashes because of it.
- `data/datasets.csv` ships with a year of synthetic daily consumption
  data (with a few injected anomalies) so the app works out of the box;
  swap in your own smart-meter export with the same two columns
  (`date`, `consumption_kwh`) to use real data.

## Deploying

Easiest path: push this folder to a GitHub repo and deploy for free on
[Streamlit Community Cloud](https://streamlit.io/cloud) — point it at
`main_app.py` and add your secrets in the app's settings.
