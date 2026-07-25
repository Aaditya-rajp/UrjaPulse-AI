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
