"""
UrjaPulse AI — 3-Node Gemini Multi-Agent System Module
Executes sequential multi-agent advisory chain using the official google-genai SDK.
Nodes: [NODE 01] Risk Analyst -> [NODE 02] Procurement Strategist -> [NODE 03] Executive Brief.
"""

from typing import Dict, Any, Optional
import os

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


def run_multi_agent_advisory_chain(
    cascade_metrics: Dict[str, Any],
    top_reranked_suppliers: list,
    gdelt_headlines: list,
    api_key: Optional[str] = None
) -> Dict[str, str]:
    """Executes the 3-Node Gemini Agent pipeline."""
    key = api_key or os.getenv("GEMINI_API_KEY", "").strip()

    if not key or not GENAI_AVAILABLE:
        return _get_fallback_advisory_response(cascade_metrics)

    try:
        client = genai.Client(api_key=key)

        risk_score = cascade_metrics.get("corridor_risk_score", 65.0)
        volume_risk = cascade_metrics.get("volume_at_risk_mbpd", 1.31)
        spr_days = cascade_metrics.get("spr_days_of_cover_remaining", 9.3)
        proj_price = cascade_metrics.get("projected_brent_price", 88.77)
        daily_loss = cascade_metrics.get("daily_macro_loss_million_usd", 24.18)

        news_context = "\n".join([f"- {h}" for h in gdelt_headlines[:3]]) if gdelt_headlines else "- Moderate naval activity detected near Hormuz transit lanes."
        suppliers_context = "\n".join([f"{i+1}. {s['supplier_hub']} (Landed: {s['landed_cost']}, Risk Reduction: {s['risk_reduction']})" for i, s in enumerate(top_reranked_suppliers[:3])])

        # --- NODE 01: Risk Analyst ---
        prompt_node_1 = f"""
        You are Node 01 [Risk Analyst] for UrjaPulse AI energy resilience platform.
        Synthesize these telemetry inputs into a sharp, 2-sentence geopolitical risk assessment:
        - Corridor Risk Score: {risk_score}/100
        - Volume at Risk: {volume_risk} MBPD
        - India Strategic SPR Cover: {spr_days} Days
        - Recent Headlines:
        {news_context}
        Focus purely on supply chain risk exposure. Do not offer solutions yet.
        """

        res_node_1 = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt_node_1,
            config=types.GenerateContentConfig(temperature=0.2, max_output_tokens=250)
        )
        node_1_text = res_node_1.text.strip() if res_node_1.text else "Convergence of negative GDELT sentiment in Persian Gulf and SPR stock depletion indicates high risk of transit bottlenecks in Strait of Hormuz."

        # --- NODE 02: Procurement Strategist ---
        prompt_node_2 = f"""
        You are Node 02 [Procurement Strategist] for UrjaPulse AI.
        Based on Node 01 Risk Assessment: "{node_1_text}"
        And Ranked Alternate Suppliers:
        {suppliers_context}

        Provide exactly 3 numbered, highly actionable mitigation steps for refinery procurement directors (Jamnagar, Vadinar, Panipat).
        Use strict double-line-break separation between numbered points. Be direct and technical.
        """

        res_node_2 = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt_node_2,
            config=types.GenerateContentConfig(temperature=0.3, max_output_tokens=350)
        )
        node_2_text = res_node_2.text.strip() if res_node_2.text else "1. Reroute 2x VLCC tankers from Persian Gulf to West Africa (Bonny Light) to protect 1.14 MBPD refinery intake.\n\n2. Exercise spot option for 1.8M bbl Brazilian Tupi Medium Sweet crude via Santos port.\n\n3. Accelerate Strategic Petroleum Reserve drawdown allocation to maintain operational buffers."

        # --- NODE 03: Executive Brief ---
        prompt_node_3 = f"""
        You are Node 03 [Executive Brief] for C-Suite Leadership.
        Projected Landed Brent Price: ${proj_price}/bbl
        Daily Trade Deficit Expansion: +${daily_loss}M/day
        Procurement Plan:
        {node_2_text}

        Write a 2-sentence executive summary highlighting immediate board action required and daily financial exposure.
        """

        res_node_3 = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt_node_3,
            config=types.GenerateContentConfig(temperature=0.2, max_output_tokens=250)
        )
        node_3_text = res_node_3.text.strip() if res_node_3.text else f"BOARD ACTION REQUIRED: Approve emergency rerouting budget (+${daily_loss}M/day exposure buffer). Market volatility warrants defensive procurement positioning before spot prices breach ${proj_price}/bbl."

        return {
            "node_01_risk": node_1_text,
            "node_02_procurement": node_2_text,
            "node_03_executive": node_3_text,
            "status": "GEMINI_2.5_FLASH_ACTIVE"
        }

    except Exception:
        return _get_fallback_advisory_response(cascade_metrics)


def _get_fallback_advisory_response(cascade_metrics: Dict[str, Any]) -> Dict[str, str]:
    """Fallback response if API key is unconfigured."""
    daily_loss = cascade_metrics.get("daily_macro_loss_million_usd", 24.18)
    proj_price = cascade_metrics.get("projected_brent_price", 88.77)
    spr_days = cascade_metrics.get("spr_days_of_cover_remaining", 9.3)

    return {
        "node_01_risk": f"Convergence of negative GDELT sentiment in the Persian Gulf and strategic stock depletion ({spr_days}d cover) indicates high risk of transit bottlenecks in the Strait of Hormuz.",
        "node_02_procurement": "1. Reroute 2x VLCC tankers from Persian Gulf to West Africa (Bonny Light) to protect domestic refinery intake.\n\n2. Exercise spot option for 1.8M bbl Brazilian Tupi Medium Sweet crude via Santos port.\n\n3. Accelerate Strategic Petroleum Reserve drawdown allocation to maintain operational buffers.",
        "node_03_executive": f"BOARD ACTION REQUIRED: Approve emergency rerouting budget (+${daily_loss}M/day exposure buffer). Market volatility warrants defensive procurement positioning before spot prices breach ${proj_price}/bbl.",
        "status": "OFFLINE_FALLBACK_ACTIVE"
    }