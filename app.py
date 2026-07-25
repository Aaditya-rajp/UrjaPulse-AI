"""
UrjaPulse AI — Master Streamlit Command Center
Assembles Telemetry, Scenario Physics, Prophet Forecasting, Geospatial Intelligence,
and 3-Node Gemini Multi-Agent Advisory into an executive dark command dashboard.
"""

import os
import textwrap
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_folium import st_folium
from dotenv import load_dotenv

# Import Configuration & Data Clients
import config
from data.industrial_registry import CHOKEPOINTS, INDIAN_REFINERIES
from data.eia_client import fetch_crude_prices, fetch_spr_levels
from data.gdelt_client import fetch_geopolitical_signals

# Import Analytical & Physics Modules
from modules.scenario_engine import (
    calculate_corridor_risk_score,
    run_disruption_cascade_simulation,
    generate_supplier_reranking_matrix
)
from modules.forecasting import generate_brent_price_forecast
from modules.geospatial import build_corridor_map
from modules.advisory import run_multi_agent_advisory_chain

# --- Page Configuration ---
st.set_page_config(
    page_title=f"{config.APP_NAME} | Energy Resilience Platform",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

load_dotenv()

# --- Custom Styling: High-Density Dark Command Styling ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #0A0B0E !important;
        color: #E2E8F0;
    }

    .stApp { background-color: #0A0B0E !important; }

    /* Active Risk Banner Over Map */
    .risk-banner {
        background: linear-gradient(90deg, #12141A 0%, #1E1010 100%);
        border: 1px solid #F97316;
        border-radius: 6px;
        padding: 8px 14px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        font-weight: 700;
        color: #F97316;
        box-shadow: 0 0 12px rgba(249, 115, 22, 0.35);
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Metric Panels */
    .metric-panel {
        background: #12141A;
        border: 1px solid #1E222D;
        border-radius: 6px;
        padding: 12px 14px;
    }
    .metric-panel-alert {
        background: #1A0F11;
        border: 1px solid #7F1D1D;
        border-radius: 6px;
        padding: 12px 14px;
    }

    .kpi-label { font-family: 'JetBrains Mono', monospace; font-size: 9px; color: #64748B; text-transform: uppercase; letter-spacing: 0.08em; }
    .kpi-val { font-family: 'JetBrains Mono', monospace; font-size: 22px; font-weight: 700; color: #F8FAFC; margin: 2px 0; }
    .kpi-sub-green { font-size: 10px; color: #10B981; font-weight: 600; }
    .kpi-sub-red { font-size: 10px; color: #EF4444; font-weight: 600; }

    /* Custom Navigation Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; border-bottom: 1px solid #1E222D; padding-bottom: 6px; }
    .stTabs [data-baseweb="tab"] {
        height: 36px;
        background-color: #12141A;
        border: 1px solid #1E222D;
        border-radius: 6px;
        color: #94A3B8;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        font-weight: 600;
        padding: 0 14px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #F97316 !important;
        color: #0A0B0E !important;
        border-color: #F97316 !important;
        box-shadow: 0 0 10px rgba(249, 115, 22, 0.4);
    }

    /* Node Multi-Agent Advisory Cards */
    .agent-card {
        background: #12141A;
        border: 1px solid #1E222D;
        border-radius: 6px;
        padding: 14px;
        height: 100%;
    }
    .agent-card-node1 { border-left: 3px solid #F97316; }
    .agent-card-node2 { border-left: 3px solid #06B6D4; }
    .agent-card-node3 { border-left: 3px solid #10B981; }

    /* Custom HTML Table Styling */
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        background-color: #12141A;
        border-radius: 6px;
        overflow: hidden;
        border: 1px solid #1E222D;
        margin-top: 8px;
    }
    .custom-table th {
        background-color: #181B22;
        color: #64748B;
        text-align: left;
        padding: 10px 12px;
        border-bottom: 1px solid #1E222D;
        text-transform: uppercase;
        font-size: 9px;
    }
    .custom-table td {
        padding: 10px 12px;
        border-bottom: 1px solid #16181F;
        color: #CBD5E1;
    }
    .badge-primary { background: #064E3B; color: #34D399; padding: 2px 6px; border-radius: 4px; font-weight: bold; border: 1px solid #10B981; }
    .badge-secondary { background: #451A03; color: #FB923C; padding: 2px 6px; border-radius: 4px; font-weight: bold; border: 1px solid #F97316; }
    .badge-hedge { background: #4C0519; color: #F43F5E; padding: 2px 6px; border-radius: 4px; font-weight: bold; border: 1px solid #F43F5E; }

    .block-container { padding-top: 1rem; padding-bottom: 2rem; max-width: 96rem; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# --- State Initialization ---
if "scenario_params" not in st.session_state:
    st.session_state.scenario_params = {
        "hormuz_blockade_pct": 45,
        "red_sea_reroute_pct": 90,
        "spr_drawdown_mbpd": 1.8,
        "elasticity_beta": 0.14,
        "freight_surcharge_pct": 25,
        "cape_delay_days": 3
    }

@st.cache_data(ttl=900, show_spinner=False)
def load_telemetry_data(eia_key: str):
    crude_data = fetch_crude_prices(api_key=eia_key)
    spr_data = fetch_spr_levels(api_key=eia_key)
    gdelt_data = fetch_geopolitical_signals()
    return crude_data, spr_data, gdelt_data

eia_api_key = os.getenv("EIA_API_KEY", "")
gemini_api_key = os.getenv("GEMINI_API_KEY", "")

crude_df, spr_df, gdelt_df = load_telemetry_data(eia_api_key)

latest_brent = float(crude_df["brent"].iloc[-1]) if not crude_df.empty else 84.12
latest_wti = float(crude_df["wti"].iloc[-1]) if not crude_df.empty else 79.85
latest_volatility = float(crude_df["brent_volatility_7d"].iloc[-1]) if not crude_df.empty else 0.018
latest_spr_mbbl = config.INDIA_STRATEGIC_RESERVE_MBBL

avg_goldstein = float(gdelt_df["goldstein_scale"].mean()) if not gdelt_df.empty else -5.5
corridor_risk_score = calculate_corridor_risk_score(avg_goldstein, latest_volatility)

params = st.session_state.scenario_params

cascade_results = run_disruption_cascade_simulation(
    brent_spot=latest_brent,
    spr_stock_mbbl=latest_spr_mbbl,
    corridor_risk_score=corridor_risk_score,
    hormuz_blockade_pct=params["hormuz_blockade_pct"],
    red_sea_reroute_pct=params["red_sea_reroute_pct"],
    spr_drawdown_mbpd=params["spr_drawdown_mbpd"],
    elasticity_beta=params["elasticity_beta"],
    freight_surcharge_pct=params["freight_surcharge_pct"],
    cape_delay_days=params["cape_delay_days"]
)

reranking_df = generate_supplier_reranking_matrix(
    current_brent=latest_brent,
    freight_surcharge_pct=params["freight_surcharge_pct"],
    corridor_risk_score=corridor_risk_score
)


def render_html_reranking_table(df: pd.DataFrame) -> str:
    """Renders a whitespace-sanitized HTML table string with neon badge styling."""
    rows_html = ""
    for _, row in df.iterrows():
        status = row["status"]
        if "PRIMARY" in status:
            badge_class = "badge-primary"
        elif "SECONDARY" in status:
            badge_class = "badge-secondary"
        else:
            badge_class = "badge-hedge"

        rows_html += f"""<tr>
            <td style="color: #F97316; font-weight: bold;">{row['rank']}</td>
            <td><b>{row['supplier_hub']}</b></td>
            <td>{row['grade']}</td>
            <td>{row['transit_days']}</td>
            <td style="color: #F8FAFC; font-weight: bold;">{row['landed_cost']}</td>
            <td>{row['compatibility']}</td>
            <td style="color: #10B981; font-weight: bold;">{row['risk_reduction']}</td>
            <td><span class="{badge_class}">{status}</span></td>
        </tr>"""

    raw_html = f"""<table class="custom-table">
        <thead>
            <tr>
                <th>Rank</th>
                <th>Supply Hub / Origin</th>
                <th>Grade</th>
                <th>Transit Window</th>
                <th>Landed Cost</th>
                <th>Grade Match</th>
                <th>Risk Reduction</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>"""
    return textwrap.dedent(raw_html).strip()


def display_html_table(html_content: str):
    """Renders HTML cleanly, preventing markdown string interpretation errors."""
    if hasattr(st, "html"):
        st.html(html_content)
    else:
        st.markdown(html_content, unsafe_allow_html=True)


# --- Executive Board Briefing Dialog ---
@st.dialog("🏛️ EXECUTIVE BOARD BRIEFING — STRATEGIC MANDATE")
def show_board_report_modal():
    st.markdown(f"""
    <div style="background-color: #12141A; padding: 12px; border-radius: 6px; border-left: 3px solid #F97316; font-family: 'JetBrains Mono', monospace; font-size: 11px;">
        CONFIDENTIAL | PREPARED FOR THE OFFICE OF THE CEO & BOARD OF DIRECTORS<br/>
        DATE: {pd.Timestamp.now().strftime('%B %d, %Y')} | ENGINE: UrjaPulse AI v2.4
    </div>
    """, unsafe_allow_html=True)
    st.markdown("")

    st.markdown(f"""
    #### 1. Executive Situation Assessment
    * **Corridor Friction Status:** Active Maritime Bottleneck identified in the **Strait of Hormuz** (Risk Index: **{corridor_risk_score}/100**).
    * **Supply Vulnerability:** **{cascade_results['volume_at_risk_mbpd']} MBPD** ({cascade_results['pct_total_imports_at_risk']}% of national daily import throughput) impacted.
    * **Strategic Petroleum Reserve Cover:** Domestic buffer stands at **{cascade_results['spr_days_of_cover_remaining']} Days** against the 14-day statutory safety threshold.

    #### 2. Financial Exposure & Capital Impact
    * **Landed Benchmark Impact:** Projected Brent spot escalation to **${cascade_results['projected_brent_price']:.2f}/bbl** (+${cascade_results['price_delta_usd_bbl']:.2f}/bbl disruption premium).
    * **Macro Deficit Expansion:** India trade deficit expanding at an estimated **+${cascade_results['daily_macro_loss_million_usd']:.2f}M / day** under current surcharge levels.

    #### 3. Recommended Rerouting & Procurement Mandate
    """)
    
    top_suppliers = reranking_df.head(3).to_dict(orient="records")
    for idx, sup in enumerate(top_suppliers):
        st.markdown(f"**Action {idx+1}: Secure Allocation from {sup['supplier_hub']}**")
        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;*Landed Cost:* `{sup['landed_cost']}` | *Transit Window:* `{sup['transit_days']}` | *Risk Offload:* `{sup['risk_reduction']}`")

    st.markdown("---")
    if st.button("Acknowledge & Close Briefing", width="stretch"):
        st.rerun()


# --- Header Bar ---
h_col1, h_col2 = st.columns([4, 1])
with h_col1:
    st.title("🛢️ UrjaPulse AI")
    st.caption("AI-Driven Energy Supply Chain Resilience Platform — ET AI Hackathon 2026")
with h_col2:
    if st.button("📋 Board Brief", type="primary", width="stretch"):
        show_board_report_modal()

st.markdown("---")


# --- 4 Primary Navigation Tabs ---
tab1, tab2, tab3, tab4 = st.tabs([
    "🖥️ Command Dashboard",
    "🎛️ Scenario Simulator",
    "📈 14D Prophet Forecast",
    "📑 Procurement Reranking"
])


# ==========================================
# TAB 1: COMMAND DASHBOARD (3-Column Grid)
# ==========================================
with tab1:
    col_left, col_center, col_right = st.columns([3, 6, 3])
    
    # Column 1: Benchmarks
    with col_left:
        st.markdown("##### 📊 Telemetry Benchmarks")
        st.markdown(f"""
        <div class="metric-panel">
            <div class="kpi-label">Brent Crude Spot</div>
            <div class="kpi-val">${latest_brent:.2f}</div>
            <div class="kpi-sub-green">▲ Live EIA Benchmark</div>
        </div>
        <div style="height: 8px;"></div>
        <div class="metric-panel">
            <div class="kpi-label">WTI Crude Spot</div>
            <div class="kpi-val">${latest_wti:.2f}</div>
            <div class="kpi-sub-green">▲ Live EIA Benchmark</div>
        </div>
        <div style="height: 8px;"></div>
        <div class="metric-panel-alert">
            <div class="kpi-label">SPR Days-of-Cover</div>
            <div class="kpi-val" style="color: #EF4444;">{cascade_results['spr_days_of_cover_remaining']}d</div>
            <div class="kpi-sub-red">⚠️ BELOW 14D SAFETY TARGET</div>
        </div>
        <div style="height: 8px;"></div>
        <div class="metric-panel">
            <div class="kpi-label">Refinery Intake Rate</div>
            <div class="kpi-val">{config.INDIA_REFINERY_UTILIZATION_PCT}%</div>
            <div class="kpi-sub-green">Domestic Capacity Utilized</div>
        </div>
        """, unsafe_allow_html=True)

    # Column 2: Vector Map with Active Risk & Corridor Overlays
    with col_center:
        st.markdown(f"""
        <div class="risk-banner">
            <span>⚡ ACTIVE RISK: STRAIT OF HORMUZ [SCORE: {corridor_risk_score}]</span>
            <span style="color: #64748B; font-weight: normal;">MONITORED CORRIDORS: 4</span>
        </div>
        """, unsafe_allow_html=True)
        
        m = build_corridor_map(corridor_risk_score=corridor_risk_score)
        st_folium(m, returned_objects=[], width="100%", height=350, key="tab1_map")
        
        mc1, mc2, mc3, mc4 = st.columns(4)
        mc1.metric("VOLUME AT RISK", f"{cascade_results['volume_at_risk_mbpd']} MBPD", f"{cascade_results['pct_total_imports_at_risk']}% Imports")
        mc2.metric("PRICE IMPACT", f"+${cascade_results['price_delta_usd_bbl']:.2f}/bbl", f"${cascade_results['projected_brent_price']:.2f}")
        mc3.metric("SPR COVER REM.", f"{cascade_results['spr_days_of_cover_remaining']} Days", f"Critical < 14d")
        mc4.metric("DAILY TRADE DEFICIT", f"+${cascade_results['daily_macro_loss_million_usd']:.2f}M/day", "INR Pressure")

    # Column 3: GDELT Feed
    with col_right:
        st.markdown("##### 📰 GDELT Geopolitical Feed")
        search_query = st.text_input("Search events...", placeholder="Filter headlines...", label_visibility="collapsed")
        
        filtered_gdelt = gdelt_df
        if search_query:
            filtered_gdelt = gdelt_df[gdelt_df["title"].str.contains(search_query, case=False, na=False)]
            
        if not filtered_gdelt.empty:
            for idx, row in filtered_gdelt.head(4).iterrows():
                goldstein_color = "#EF4444" if row["goldstein_scale"] < 0 else "#10B981"
                st.markdown(f"""
                <div style="background: #12141A; border: 1px solid #1E222D; border-left: 3px solid {goldstein_color}; padding: 8px 10px; margin-bottom: 6px; border-radius: 4px;">
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 9px; color: #06B6D4;">{row['chokepoint']}</div>
                    <a href="{row['url']}" target="_blank" style="color: #E2E8F0; text-decoration: none; font-size: 11px; font-weight: 500;">{row['title'][:60]}...</a>
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 9px; color: {goldstein_color}; margin-top: 2px;">Goldstein: {row['goldstein_scale']} | Tone: {row['tone']}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No matching geopolitical events detected.")

    st.markdown("---")

    # Single-Location Multi-Agent Advisory
    st.markdown("##### 🤖 Gemini 3-Node Multi-Agent Advisory System")
    
    top_suppliers_list = reranking_df.to_dict(orient="records")
    headlines_list = gdelt_df["title"].tolist() if not gdelt_df.empty else []
    
    advisory_output = run_multi_agent_advisory_chain(
        cascade_metrics=cascade_results,
        top_reranked_suppliers=top_suppliers_list,
        gdelt_headlines=headlines_list,
        api_key=gemini_api_key
    )

    node_col1, node_col2, node_col3 = st.columns(3)
    with node_col1:
        st.markdown(f"""
        <div class="agent-card agent-card-node1">
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; color: #F97316;">[NODE 01] RISK ANALYST</div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 9px; color: #64748B;">TELEMETRY SYNTHESIS</div>
            <div style="font-size: 11px; line-height: 1.5; color: #CBD5E1; margin-top: 6px;">"{advisory_output['node_01_risk']}"</div>
        </div>
        """, unsafe_allow_html=True)
        
    with node_col2:
        st.markdown(f"""
        <div class="agent-card agent-card-node2">
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; color: #06B6D4;">[NODE 02] PROCUREMENT STRATEGIST</div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 9px; color: #64748B;">EXECUTABLE RERANKING</div>
            <div style="font-size: 11px; line-height: 1.5; color: #CBD5E1; margin-top: 6px;">{advisory_output['node_02_procurement'].replace('\n', '<br/>')}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with node_col3:
        st.markdown(f"""
        <div class="agent-card agent-card-node3">
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; color: #10B981;">[NODE 03] EXECUTIVE BRIEF</div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 9px; color: #64748B;">BOARD ACTION MANDATE</div>
            <div style="font-size: 11px; line-height: 1.5; color: #CBD5E1; margin-top: 6px;">{advisory_output['node_03_executive']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("##### 📊 SUPPLIER & ROUTE RERANKING MATRIX")
    display_html_table(render_html_reranking_table(reranking_df))


# ==========================================
# TAB 2: SCENARIO SIMULATOR
# ==========================================
with tab2:
    st.subheader("🎛️ SCENARIO IMPACT SIMULATOR (SECTION 4 ENGINE)")
    st.caption("Adjust disruption vectors to simulate cascading supply impact.")

    sc_col1, sc_col2, sc_col3 = st.columns(3)
    with sc_col1:
        st.session_state.scenario_params["hormuz_blockade_pct"] = st.slider("Strait of Hormuz Blockade %", 0, 100, st.session_state.scenario_params["hormuz_blockade_pct"])
        st.session_state.scenario_params["elasticity_beta"] = st.select_slider("Price Elasticity Factor (β)", options=[0.05, 0.08, 0.14, 0.20], value=st.session_state.scenario_params["elasticity_beta"])
    with sc_col2:
        st.session_state.scenario_params["red_sea_reroute_pct"] = st.slider("Red Sea Transit Reroute %", 0, 100, st.session_state.scenario_params["red_sea_reroute_pct"])
        st.session_state.scenario_params["freight_surcharge_pct"] = st.slider("War Risk Freight Surcharge %", 0, 50, st.session_state.scenario_params["freight_surcharge_pct"])
    with sc_col3:
        st.session_state.scenario_params["spr_drawdown_mbpd"] = st.slider("SPR Buffer Release Rate (MBPD)", 0.0, 3.0, st.session_state.scenario_params["spr_drawdown_mbpd"], step=0.1)
        st.session_state.scenario_params["cape_delay_days"] = st.slider("Cape Reroute Delay (+Days)", 0, 20, st.session_state.scenario_params["cape_delay_days"])

    st.markdown("---")

    # Dynamic Severity Step Cards
    sev_colors = cascade_results["severity_colors"]
    step1, step2, step3, step4 = st.columns(4)
    
    with step1:
        st.markdown(f"""
        <div style="background: #12141A; border: 1px solid #1E222D; border-top: 3px solid #F97316; padding: 12px; border-radius: 6px; font-size: 11px;">
            <b style="color: #F97316; font-family: monospace;">1. CHOKEPOINT TRANSIT</b><br/>
            Hormuz transit bottlenecked. {params['hormuz_blockade_pct']}% capacity blockade affecting {cascade_results['volume_at_risk_mbpd']} MBPD.
        </div>
        """, unsafe_allow_html=True)
    with step2:
        st.markdown(f"""
        <div style="background: #12141A; border: 1px solid #1E222D; border-top: 3px solid {sev_colors['spr']}; padding: 12px; border-radius: 6px; font-size: 11px;">
            <b style="color: {sev_colors['spr']}; font-family: monospace;">2. REFINERY STOCKPILES</b><br/>
            Domestic crude inventories declining. Strategic cover down to {cascade_results['spr_days_of_cover_remaining']} days.
        </div>
        """, unsafe_allow_html=True)
    with step3:
        st.markdown(f"""
        <div style="background: #12141A; border: 1px solid #1E222D; border-top: 3px solid {sev_colors['price']}; padding: 12px; border-radius: 6px; font-size: 11px;">
            <b style="color: {sev_colors['price']}; font-family: monospace;">3. LANDED COST & FREIGHT</b><br/>
            Projected Brent landed cost +${cascade_results['price_delta_usd_bbl']:.2f}/bbl. Cape reroute adds +{params['cape_delay_days']}d transit.
        </div>
        """, unsafe_allow_html=True)
    with step4:
        st.markdown(f"""
        <div style="background: #12141A; border: 1px solid #1E222D; border-top: 3px solid #10B981; padding: 12px; border-radius: 6px; font-size: 11px;">
            <b style="color: #10B981; font-family: monospace;">4. MACRO TRADE BALANCE</b><br/>
            Daily trade deficit expansion: +${cascade_results['daily_macro_loss_million_usd']:.2f}M/day under current surcharges.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    sim_left, sim_right = st.columns([1, 1])
    with sim_left:
        st.markdown("##### 🗺️ Simulated Corridor Vectors")
        m_sim = build_corridor_map(corridor_risk_score=corridor_risk_score)
        st_folium(m_sim, returned_objects=[], width="100%", height=380, key="tab2_map")

    with sim_right:
        st.markdown("##### 📊 Dynamic Reranking Matrix")
        display_html_table(render_html_reranking_table(reranking_df))


# ==========================================
# TAB 3: 14D PROPHET FORECAST
# ==========================================
with tab3:
    st.subheader("📈 14-DAY PROPHET PRICE FORECAST & BACKTEST VALIDATION")
    
    forecast_results = generate_brent_price_forecast(crude_df, forecast_days=14)
    forecast_df = forecast_results["forecast_df"]
    metrics = forecast_results["metrics"]

    fig = go.Figure()

    hist_mask = ~forecast_df["is_forecast"]
    fig.add_trace(go.Scatter(
        x=forecast_df.loc[hist_mask, "ds"],
        y=forecast_df.loc[hist_mask, "y_actual"],
        mode="lines+markers",
        name="Historical Spot Price",
        line=dict(color="#06B6D4", width=2)
    ))

    fut_mask = forecast_df["is_forecast"]
    fig.add_trace(go.Scatter(
        x=forecast_df.loc[fut_mask, "ds"],
        y=forecast_df.loc[fut_mask, "yhat"],
        mode="lines+markers",
        name="Prophet 14D Projection",
        line=dict(color="#F97316", width=2, dash="dash")
    ))

    fig.add_trace(go.Scatter(
        x=forecast_df.loc[fut_mask, "ds"],
        y=forecast_df.loc[fut_mask, "yhat_upper"],
        mode="lines",
        name="80% Upper Band",
        line=dict(width=0),
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=forecast_df.loc[fut_mask, "ds"],
        y=forecast_df.loc[fut_mask, "yhat_lower"],
        mode="lines",
        name="80% Lower Band",
        fill="tonexty",
        fillcolor="rgba(249, 115, 22, 0.12)",
        line=dict(width=0),
        showlegend=False
    ))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#12141A",
        plot_bgcolor="#12141A",
        margin=dict(l=20, r=20, t=30, b=20),
        height=380,
        xaxis_title="Date",
        yaxis_title="Brent Crude Spot ($/bbl)"
    )

    st.plotly_chart(fig, width="stretch")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("MAE (Accuracy)", f"${metrics['mae']}", "Mean Absolute Error")
    m2.metric("RMSE Metric", f"${metrics['rmse']}", "Root Mean Squared Error")
    m3.metric("Prior Scale", "0.03 β", "Damped Changepoint")
    m4.metric("Backtest Window", "14 Days", "Historical Train/Test Split")


# ==========================================
# TAB 4: PROCUREMENT RERANKING
# ==========================================
with tab4:
    st.subheader("📑 Automated Supplier & Route Reranking Matrix")
    st.caption("Evaluated against refinery metallurgy, transit delay, and risk reduction margins.")
    display_html_table(render_html_reranking_table(reranking_df))