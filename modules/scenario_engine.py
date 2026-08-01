"""
Scenario Engine — Physics & Mathematical Simulation Engine
Calculates dynamic risk scores, disruption cascades, SPR cover, and supplier reranking.
"""

import pandas as pd


def calculate_corridor_risk_score(
    avg_goldstein: float, 
    volatility: float, 
    hormuz_pct: float = 0.0, 
    red_sea_pct: float = 0.0
) -> float:
    """
    Calculates dynamic corridor risk score (0-100) combining GDELT conflict scale,
    price volatility, and active scenario blockade sliders.
    """
    # Base GDELT risk: Goldstein scale ranges from -10 (conflict) to +10 (cooperation)
    base_risk = max(0.0, min(100.0, (5.0 - avg_goldstein) * 5.0))
    volatility_boost = min(20.0, volatility * 500.0)
    
    # Dynamic scenario slider impact
    scenario_boost = (hormuz_pct * 0.40) + (red_sea_pct * 0.20)
    
    total_score = base_risk + volatility_boost + scenario_boost
    return round(max(5.0, min(99.9, total_score)), 1)


def run_disruption_cascade_simulation(
    brent_spot: float,
    spr_stock_mbbl: float,
    corridor_risk_score: float,
    hormuz_blockade_pct: float,
    red_sea_reroute_pct: float,
    spr_drawdown_mbpd: float,
    elasticity_beta: float,
    freight_surcharge_pct: float,
    cape_delay_days: int
) -> dict:
    """Calculates volume at risk, dynamic SPR depletion, price surges, and daily trade loss."""
    base_import_mbpd = 4.6  # Baseline daily crude import volume
    
    # 1. Volume at Risk
    hormuz_vol = base_import_mbpd * 0.50 * (hormuz_blockade_pct / 100.0)
    red_sea_vol = base_import_mbpd * 0.15 * (red_sea_reroute_pct / 100.0)
    volume_at_risk = round(hormuz_vol + red_sea_vol, 2)
    pct_at_risk = round((volume_at_risk / base_import_mbpd) * 100.0, 1)

    # 2. Dynamic SPR Days of Cover
    net_daily_deficit = max(0.05, volume_at_risk - spr_drawdown_mbpd)
    if volume_at_risk <= 0:
        spr_days = 74.0  # Baseline static buffer
    else:
        spr_days = spr_stock_mbbl / net_daily_deficit
    spr_days_remaining = round(max(1.0, min(90.0, spr_days)), 1)

    # 3. Price Escalation Impact ($/bbl)
    disruption_ratio = volume_at_risk / base_import_mbpd
    price_delta = (disruption_ratio / max(0.01, elasticity_beta)) * 8.5 + (brent_spot * (freight_surcharge_pct / 100.0) * 0.15)
    projected_brent = round(brent_spot + price_delta, 2)

    # 4. Daily Macro Deficit Loss ($M/day)
    daily_trade_loss = round((volume_at_risk * projected_brent) + (base_import_mbpd * price_delta * 0.4), 1)

    # Severity Colors
    spr_color = "#EF4444" if spr_days_remaining < 14 else ("#F97316" if spr_days_remaining < 30 else "#10B981")
    price_color = "#EF4444" if price_delta > 15 else ("#F97316" if price_delta > 5 else "#10B981")

    return {
        "volume_at_risk_mbpd": volume_at_risk,
        "pct_total_imports_at_risk": pct_at_risk,
        "spr_days_of_cover_remaining": spr_days_remaining,
        "price_delta_usd_bbl": round(price_delta, 2),
        "projected_brent_price": projected_brent,
        "daily_macro_loss_million_usd": daily_trade_loss,
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
    """Generates dynamic supplier reranking with individual route-level risk scores."""
    surcharge_multiplier = 1.0 + (freight_surcharge_pct / 100.0)
    
    # Calculate route-specific risk scores based on physical chokepoint exposure
    ras_tanura_risk = round(corridor_risk_score, 1)                             # 100% exposed to Hormuz
    fujairah_risk = round(max(10.0, corridor_risk_score * 0.35), 1)            # Partially bypasses Hormuz (-65% risk)
    santos_risk = round(max(5.0, corridor_risk_score * 0.15), 1)              # Bypasses Middle East completely (-85% risk)

    suppliers = [
        {
            "rank": 1 if corridor_risk_score > 50 else 2,
            "supplier_hub": "Fujairah / West Africa",
            "grade": "Bonny Light / Forcados",
            "transit_days": "12 - 14 Days",
            "landed_cost": f"${(current_brent + 2.40) * surcharge_multiplier:.2f}/bbl",
            "compatibility": "96% High Match",
            "risk_score": f"{fujairah_risk} / 100",
            "risk_reduction": f"-{round(100 - (fujairah_risk / max(1.0, ras_tanura_risk) * 100))}% Offload",
            "status": "PRIMARY ALTERNATE"
        },
        {
            "rank": 2 if corridor_risk_score > 50 else 1,
            "supplier_hub": "Santos Basin (Brazil)",
            "grade": "Lula / Mero Heavy",
            "transit_days": "22 - 25 Days",
            "landed_cost": f"${(current_brent + 1.10) * surcharge_multiplier:.2f}/bbl",
            "compatibility": "88% Medium Match",
            "risk_score": f"{santos_risk} / 100",
            "risk_reduction": f"-{round(100 - (santos_risk / max(1.0, ras_tanura_risk) * 100))}% Offload",
            "status": "SECONDARY ROUTE"
        },
        {
            "rank": 3,
            "supplier_hub": "Ras Tanura (Saudi Arabia)",
            "grade": "Arab Light / Medium",
            "transit_days": "4 - 6 Days",
            "landed_cost": f"${current_brent:.2f}/bbl",
            "compatibility": "100% Exact Match",
            "risk_score": f"{ras_tanura_risk} / 100",
            "risk_reduction": "0% (Fully Exposed)",
            "status": "HEDGE ONLY"
        }
    ]
    df = pd.DataFrame(suppliers)
    return df.sort_values(by="rank").reset_index(drop=True)
