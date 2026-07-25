"""
UrjaPulse AI — Disruption Impact Scenario Engine
Computes supply cascade physics and dynamically calculates color-coded step card severity.
"""

from typing import Dict, Any
import numpy as np
import pandas as pd

from data.industrial_registry import CHOKEPOINTS, ALTERNATE_SUPPLY_ORIGINS


def calculate_corridor_risk_score(
    goldstein_scale: float,
    price_volatility_7d: float,
    base_weight_goldstein: float = 0.6,
    base_weight_volatility: float = 0.4
) -> float:
    """Computes a clamped Corridor Risk Score (0 to 100)."""
    normalized_goldstein_risk = np.clip((5.0 - goldstein_scale) * 6.67, 0.0, 100.0)
    normalized_volatility_risk = np.clip(price_volatility_7d * 2000.0, 0.0, 100.0)

    raw_score = (base_weight_goldstein * normalized_goldstein_risk) + (
        base_weight_volatility * normalized_volatility_risk
    )
    return float(np.round(np.clip(raw_score, 0.0, 100.0), 1))


def run_disruption_cascade_simulation(
    brent_spot: float,
    spr_stock_mbbl: float,
    corridor_risk_score: float,
    hormuz_blockade_pct: float = 45.0,
    red_sea_reroute_pct: float = 30.0,
    spr_drawdown_mbpd: float = 1.8,
    elasticity_beta: float = 0.14,
    freight_surcharge_pct: float = 25.0,
    cape_delay_days: int = 3,
    india_daily_import_mbpd: float = 4.6,
    india_daily_consumption_mbpd: float = 5.2
) -> Dict[str, Any]:
    """Simulates supply cascades, SPR depletion, price surges, and macro economic deficits."""
    # 1. Volume at Risk
    hormuz_share = CHOKEPOINTS["Strait_of_Hormuz"]["share_of_india_imports"]
    red_sea_share = CHOKEPOINTS["Bab_el_Mandeb"]["share_of_india_imports"]

    blocked_hormuz_mbpd = india_daily_import_mbpd * hormuz_share * (hormuz_blockade_pct / 100.0)
    rerouted_red_sea_mbpd = india_daily_import_mbpd * red_sea_share * (red_sea_reroute_pct / 100.0)

    total_volume_at_risk_mbpd = blocked_hormuz_mbpd + (rerouted_red_sea_mbpd * 0.15)
    pct_total_imports_at_risk = (total_volume_at_risk_mbpd / india_daily_import_mbpd) * 100.0

    # 2. SPR Days-of-Cover
    effective_spr = min(spr_stock_mbbl, 48.0) if spr_stock_mbbl > 100 else spr_stock_mbbl
    net_daily_deficit_mbpd = max(0.0, blocked_hormuz_mbpd - spr_drawdown_mbpd)
    
    if net_daily_deficit_mbpd > 0:
        depleted_cover_days = max(1.0, effective_spr / (india_daily_consumption_mbpd * (1.0 + (net_daily_deficit_mbpd / india_daily_import_mbpd))))
        depletion_rate_pct_day = (net_daily_deficit_mbpd / effective_spr) * 100.0
    else:
        depleted_cover_days = effective_spr / india_daily_consumption_mbpd
        depletion_rate_pct_day = 0.0

    # 3. Price Impact Propagation
    disruption_fraction = pct_total_imports_at_risk / 100.0
    price_surge_pct = (disruption_fraction / elasticity_beta) * 100.0
    freight_adder = brent_spot * (freight_surcharge_pct / 100.0) * 0.12
    
    projected_brent_price = brent_spot * (1.0 + (price_surge_pct / 100.0)) + freight_adder
    price_delta_usd_bbl = projected_brent_price - brent_spot

    # 4. Macro Economic Loss
    baseline_daily_cost = india_daily_import_mbpd * 1_000_000 * brent_spot
    projected_daily_cost = india_daily_import_mbpd * 1_000_000 * projected_brent_price
    daily_macro_loss_million_usd = (projected_daily_cost - baseline_daily_cost) / 1_000_000.0

    # Dynamic Severity Color Generators for Scenario Step Cards
    spr_color = "#EF4444" if depleted_cover_days < 10.0 else "#F97316" if depleted_cover_days < 14.0 else "#10B981"
    price_color = "#EF4444" if price_delta_usd_bbl > 10.0 else "#F97316" if price_delta_usd_bbl > 3.0 else "#10B981"

    return {
        "corridor_risk_score": corridor_risk_score,
        "volume_at_risk_mbpd": round(total_volume_at_risk_mbpd, 2),
        "pct_total_imports_at_risk": round(pct_total_imports_at_risk, 1),
        "spr_days_of_cover_remaining": round(depleted_cover_days, 1),
        "spr_depletion_rate_pct_day": round(depletion_rate_pct_day, 2),
        "projected_brent_price": round(projected_brent_price, 2),
        "price_delta_usd_bbl": round(price_delta_usd_bbl, 2),
        "daily_macro_loss_million_usd": round(daily_macro_loss_million_usd, 2),
        "severity_colors": {
            "spr": spr_color,
            "price": price_color
        }
    }


def generate_supplier_reranking_matrix(
    current_brent: float,
    freight_surcharge_pct: float,
    corridor_risk_score: float
) -> pd.DataFrame:
    """Evaluates alternate supply hubs and outputs a ranked procurement matrix."""
    matrix_rows = []

    for key, hub in ALTERNATE_SUPPLY_ORIGINS.items():
        base_freight = hub["freight_base_usd_bbl"]
        surcharge_adder = base_freight * (freight_surcharge_pct / 100.0)
        
        if key == "Fujairah_UAE" and corridor_risk_score > 60:
            extra_delay = 3
            status = "PRIMARY ALTERNATE"
            status_code = "PRIMARY_ALT"
        elif key in ["US_Gulf_Coast", "Santos_Brazil"]:
            extra_delay = 0
            status = "SECONDARY ROUTE"
            status_code = "SECONDARY"
        elif key == "Bonny_Nigeria":
            extra_delay = 2
            status = "PRIMARY ALTERNATE"
            status_code = "PRIMARY_ALT"
        else:
            extra_delay = 4
            status = "HEDGE ONLY"
            status_code = "HEDGE"

        landed_cost = current_brent + base_freight + surcharge_adder
        total_delay_days = hub["transit_days_base"] + extra_delay
        
        if key in ["US_Gulf_Coast", "Santos_Brazil"]:
            risk_reduction_pct = 92.0
            grade_compat_pct = "89%"
        elif key == "Bonny_Nigeria":
            risk_reduction_pct = 88.0
            grade_compat_pct = "95%"
        elif key == "Fujairah_UAE":
            risk_reduction_pct = 62.0
            grade_compat_pct = "92%"
        elif key == "Primorsk_Russia":
            risk_reduction_pct = 40.0
            grade_compat_pct = "82%"
        else:
            risk_reduction_pct = 15.0
            grade_compat_pct = "98%"

        matrix_rows.append({
            "rank": 0,
            "supplier_hub": hub["name"],
            "region": "International",
            "grade": hub["grade_compat"],
            "transit_days": f"{total_delay_days}d (+{extra_delay}d)",
            "landed_cost": f"${landed_cost:.2f}/bbl",
            "compatibility": grade_compat_pct,
            "risk_reduction": f"-{risk_reduction_pct:.0f}%",
            "status": status,
            "status_code": status_code,
            "sort_cost": landed_cost,
            "sort_risk": risk_reduction_pct
        })

    df = pd.DataFrame(matrix_rows)
    df = df.sort_values(by=["sort_risk", "sort_cost"], ascending=[False, True]).reset_index(drop=True)
    df["rank"] = [f"#{i+1}" for i in range(len(df))]
    
    return df[["rank", "supplier_hub", "region", "grade", "transit_days", "landed_cost", "compatibility", "risk_reduction", "status", "status_code"]]