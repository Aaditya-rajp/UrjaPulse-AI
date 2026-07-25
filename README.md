# 🛢️ UrjaPulse AI — Energy Supply Chain Resilience Platform

![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.30+-orange.svg)
![Gemini 2.5 Flash](https://img.shields.io/badge/AI-Gemini%202.5%20Flash-green.svg)
![License](https://img.shields.io/badge/license-MIT-brightgreen.svg)

UrjaPulse AI is an executive-level command dashboard engineered to model, forecast, and mitigate geopolitical disruptions across critical maritime oil transit corridors (Strait of Hormuz, Bab-el-Mandeb / Red Sea). 

By synthesizing live EIA energy benchmarks, real-time GDELT event signals, deterministic supply-cascade math, Meta Prophet time-series forecasting, and a sequential 3-Node Gemini multi-agent system, UrjaPulse AI provides instant strategic visibility and procurement reranking for C-suite decision-makers.

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph Layer1 ["1. Live Telemetry & Ingestion Layer"]
        EIA["EIA API v2<br/>(Brent/WTI Spot & SPR Stocks)"]
        GDELT["GDELT DOC API v2<br/>(Goldstein Conflict Signals)"]
        FALLBACK["Fallback Data Engine<br/>(Zero-Crash Offline Matrix)"]
    end

    subgraph Layer2 ["2. Analytics, Physics & Forecasting Engine"]
        SE["scenario_engine.py<br/>(Disruption Physics & Deficit Loss Math)"]
        PF["forecasting.py<br/>(14D Prophet Time-Series & MAE Backtesting)"]
        GEO["geospatial.py<br/>(Folium Vector Maps & Risk Radius Beacons)"]
    end

    subgraph Layer3 ["3. Agentic Intelligence Pipeline"]
        N1["Node 01: Risk Analyst<br/>(Geopolitical Sentiment Synthesis)"]
        N2["Node 02: Procurement Strategist<br/>(Alternate Supplier Allocation & Reranking)"]
        N3["Node 03: Executive Brief<br/>(C-Suite Board Action & Exposure Mandate)"]
        N1 --> N2 --> N3
    end

    subgraph Layer4 ["4. Streamlit Command Center (app.py)"]
        T1["Tab 1: Command Dashboard<br/>(3-Column Grid Layout)"]
        T2["Tab 2: Scenario Simulator<br/>(2x3 Interactive Control Deck)"]
        T3["Tab 3: 14D Prophet Forecast<br/>(Backtest Validation & Confidence Bands)"]
        T4["Tab 4: Procurement Reranking<br/>(Custom Neon-Badge Status Table)"]
        MODAL["st.dialog: Board Briefing Modal"]
    end

    Layer1 --> Layer2
    Layer2 --> Layer3
    Layer2 --> Layer4
    Layer3 --> Layer4
```
📂 Repository Structure
UrjaPulseAI/
├── .streamlit/
│   └── config.toml          # Dark command-center theme configuration
├── data/
│   ├── eia_client.py        # EIA API v2 benchmark connector
│   ├── gdelt_client.py      # GDELT v2 geopolitical signal parser
│   ├── fallback_data.py     # Offline shock-absorber stream engine
│   └── industrial_registry.py # Maritime chokepoint & refinery specs
├── modules/
│   ├── scenario_engine.py   # Disruption physics math & reranking matrix
│   ├── forecasting.py       # Prophet model fitting & MAE/RMSE metrics
│   ├── geospatial.py        # Folium vector map & glowing HTML DivIcons
│   └── advisory.py          # 3-Node Gemini Multi-Agent System (google-genai)
├── .gitignore               # Repository governance exclusions
├── app.py                   # Master Streamlit Command Center
├── config.py                # Macro constants & risk threshold defaults
└── requirements.txt         # Production dependency constraints

⚙️ Core CapabilitiesLive Geopolitical Telemetry: Ingests daily EIA spot prices alongside real-time GDELT event streams, calculating dynamic Goldstein conflict scores to quantify transit risk.Interactive Disruption Simulator: Allows users to adjust blockade severity, freight surcharges, and price elasticity ($\beta$) to compute immediate volume at risk, SPR depletion rates, and daily trade deficit expansion ($M/day).Prophet Price Forecasting: Fits a damped 14-day time-series forecasting model with 80% confidence intervals and historical train/test split backtest metrics (MAE / RMSE).Geospatial Risk Mapping: Renders interactive dark vector maps with custom HTML DivIcons highlighting refineries, supply hubs, and active flow vector lines without page refresh reloads.3-Node Sequential Multi-Agent Advisory: Employs Gemini 2.5 Flash via the official @google/genai SDK to execute structured advisory chains:Node 01 (Risk Analyst): Synthesizes telemetry into conflict summaries.Node 02 (Procurement Strategist): Generates actionable alternate supplier reranking.Node 03 (Executive Brief): Drafts C-suite board briefs with exact financial exposure figures.🚀 Quickstart GuideLocal SetupClone Repository:Bashgit clone [https://github.com/YourUsername/UrjaPulseAI.git](https://github.com/YourUsername/UrjaPulseAI.git)
cd UrjaPulseAI
Activate Virtual Environment:Bashpython -m venv venv
# On Windows CMD:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
Install Dependencies:Bashpip install -r requirements.txt
Set Up Local Credentials:Create a .env file in the project root:Code snippetEIA_API_KEY=your_eia_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
Launch Application:Bashstreamlit run app.py
☁️ Streamlit Cloud DeploymentPush code to GitHub (ensure .env and venv/ are excluded).Connect your repository to Streamlit Community Cloud.Set Main file path to app.py.Add your API keys under Advanced Settings $\rightarrow$ Secrets:Ini, TOMLEIA_API_KEY = "your_actual_eia_key"
GEMINI_API_KEY = "your_actual_gemini_key"
