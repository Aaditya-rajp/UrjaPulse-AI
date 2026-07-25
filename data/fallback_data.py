"""
UrjaPulse AI — Fallback Data Engine ("Shock Absorber")
Generates realistic, mathematically coherent fallback data streams for EIA crude benchmarks,
US Strategic Petroleum Reserve (SPR) levels, and GDELT geopolitical news feeds.
"""

from datetime import datetime, timedelta
import numpy as np
import pandas as pd


def get_fallback_crude_data(days: int = 180) -> pd.DataFrame:
    """Generates synthetic daily Brent and WTI crude price series with rolling volatility.

    Returns DataFrame with columns: ['date', 'brent', 'wti',
    'brent_volatility_7d']
    """
    end_date = datetime.now()
    dates = [end_date - timedelta(days=i) for i in range(days)]
    dates.reverse()

    # Seed for reproducible realistic fluctuations
    np.random.seed(42)

    # Base price trajectory around $82.50 Brent, $78.00 WTI
    brent_base = 82.50
    wti_base = 78.00

    # Geometric random walk simulation
    brent_returns = np.random.normal(0.0003, 0.015, days)
    wti_returns = np.random.normal(0.00025, 0.016, days)

    brent_prices = brent_base * np.exp(np.cumsum(brent_returns))
    wti_prices = wti_base * np.exp(np.cumsum(wti_returns))

    df = pd.DataFrame({
        "date": [d.strftime("%Y-%m-%d") for d in dates],
        "brent": np.round(brent_prices, 2),
        "wti": np.round(wti_prices, 2),
    })

    # Convert date to datetime for rolling volatility calculation
    df["dt"] = pd.to_datetime(df["date"])
    df = df.sort_values("dt").reset_index(drop=True)

    # Calculate 7-day rolling standard deviation of percentage returns
    df["returns"] = df["brent"].pct_change()
    df["brent_volatility_7d"] = (
        df["returns"].rolling(window=7, min_periods=1).std().fillna(0.015)
    )

    df = df.drop(columns=["dt", "returns"])
    return df


def get_fallback_spr_data() -> pd.DataFrame:
    """Generates synthetic Strategic Petroleum Reserve (SPR) stock levels (Millions of Barrels).

    Baseline: ~347.8 MBBL (US SPR baseline). Returns DataFrame with columns:
    ['date', 'spr_mbbl', 'days_of_cover_india']
    """
    end_date = datetime.now()
    dates = [end_date - timedelta(weeks=i) for i in range(26)]  # 26 weeks
    dates.reverse()

    # Slight weekly replenishment trend
    base_spr = 347.8
    spr_levels = [base_spr + (i * 0.4) + (np.sin(i) * 0.8) for i in range(26)]

    # India consumes ~5.2 MBPD; assume static strategic reserve buffer calculation
    daily_consumption_india = 5.2
    days_cover = [round(spr / daily_consumption_india, 1) for spr in spr_levels]

    df = pd.DataFrame({
        "date": [d.strftime("%Y-%m-%d") for d in dates],
        "spr_mbbl": np.round(spr_levels, 2),
        "days_of_cover_india": days_cover,
    })
    return df


def get_fallback_gdelt_signals() -> pd.DataFrame:
    """Generates synthetic geopolitical risk event stream matching GDELT schema.

    Returns DataFrame with columns: ['url', 'title', 'goldstein_scale', 'tone',
    'chokepoint', 'seendate']
    """
    now_str = datetime.now().strftime("%Y%m%d%H%M%S")

    fallback_articles = [
        {
            "url": (
                "https://example.com/energy/hormuz-patrols-increased-maritime"
            ),
            "title": (
                "Naval Forces Increase Patrols Near Strait of Hormuz Amid"
                " Rising Regional Tensions"
            ),
            "goldstein_scale": -6.5,  # Moderate-high conflict score (-10 to +10)
            "tone": -4.2,  # Negative sentiment
            "chokepoint": "Strait_of_Hormuz",
            "seendate": now_str,
        },
        {
            "url": "https://example.com/shipping/red-sea-reroute-cape-good-hope",
            "title": (
                "Container Fleets Divert Around Cape of Good Hope to Bypass"
                " Red Sea Risk"
            ),
            "goldstein_scale": -5.0,
            "tone": -3.8,
            "chokepoint": "Bab_el_Mandeb",
            "seendate": now_str,
        },
        {
            "url": "https://example.com/opec/production-quota-meeting-vienna",
            "title": (
                "OPEC+ Reaffirms Voluntary Production Cuts Through Q3 2026"
            ),
            "goldstein_scale": 1.2,  # Slightly cooperative/neutral
            "tone": 0.5,
            "chokepoint": "Global_OPEC",
            "seendate": now_str,
        },
        {
            "url": "https://example.com/maritime/insurance-surcharges-gulf",
            "title": (
                "War-Risk Insurance Premiums Spike 15% for Arabian Gulf Crude"
                " Tankers"
            ),
            "goldstein_scale": -4.8,
            "tone": -5.1,
            "chokepoint": "Strait_of_Hormuz",
            "seendate": now_str,
        },
    ]

    return pd.DataFrame(fallback_articles)