"""
UrjaPulse AI — EIA Open Data API v2 Telemetry Client
Fetches daily Brent & WTI spot prices and weekly Strategic Petroleum Reserve (SPR) stocks.
Includes Streamlit caching and graceful fallback failover.
"""

from typing import Optional
import os
import requests
import pandas as pd
import numpy as np
import streamlit as st

from data.fallback_data import get_fallback_crude_data, get_fallback_spr_data

EIA_V2_BASE_URL = "https://api.eia.gov/v2"


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_crude_prices(api_key: Optional[str] = None, days: int = 180) -> pd.DataFrame:
    """
    Fetches daily Brent and WTI crude spot prices from EIA v2 API.
    Calculates 7-day rolling return volatility.
    
    Returns DataFrame with columns: ['date', 'brent', 'wti', 'brent_volatility_7d']
    """
    key = api_key or os.getenv("EIA_API_KEY", "").strip()

    if not key:
        return get_fallback_crude_data(days=days)

    try:
        # Endpoint for Petroleum Spot Prices
        url = f"{EIA_V2_BASE_URL}/petroleum/pri/spt/data/"
        
        # Query parameters for Brent and WTI daily spot prices
        params = {
            "api_key": key,
            "frequency": "daily",
            "data[0]": "value",
            "facets[series][]": ["PET.RBRTE.D", "PET.RWTC.D"],
            "sort[0][column]": "period",
            "sort[0][direction]": "desc",
            "length": days * 2  # Pull enough rows for both series
        }

        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            return get_fallback_crude_data(days=days)

        payload = response.json()
        data_rows = payload.get("response", {}).get("data", [])

        if not data_rows:
            return get_fallback_crude_data(days=days)

        # Parse into pandas DataFrame
        raw_df = pd.DataFrame(data_rows)
        
        # Required fields check
        if "series" not in raw_df.columns or "period" not in raw_df.columns or "value" not in raw_df.columns:
            return get_fallback_crude_data(days=days)

        # Clean values
        raw_df["value"] = pd.to_numeric(raw_df["value"], errors="coerce")
        raw_df = raw_df.dropna(subset=["value"])

        # Pivot table to get Brent and WTI in separate columns
        pivoted = raw_df.pivot_table(
            index="period",
            columns="series",
            values="value",
            aggfunc="first"
        ).reset_index()

        pivoted = pivoted.rename(columns={
            "period": "date",
            "PET.RBRTE.D": "brent",
            "PET.RWTC.D": "wti"
        })

        # Ensure both benchmark columns exist
        if "brent" not in pivoted.columns:
            pivoted["brent"] = 82.50
        if "wti" not in pivoted.columns:
            pivoted["wti"] = 78.00

        # Sort chronologically
        pivoted["dt"] = pd.to_datetime(pivoted["date"])
        pivoted = pivoted.sort_values("dt").reset_index(drop=True)

        # Forward fill any missing weekend/holiday values
        pivoted["brent"] = pivoted["brent"].ffill().bfill()
        pivoted["wti"] = pivoted["wti"].ffill().bfill()

        # Calculate 7-day rolling standard deviation of percentage returns
        pivoted["returns"] = pivoted["brent"].pct_change()
        pivoted["brent_volatility_7d"] = (
            pivoted["returns"].rolling(window=7, min_periods=1).std().fillna(0.015)
        )

        # Clean up temporary columns
        result_df = pivoted[["date", "brent", "wti", "brent_volatility_7d"]].tail(days).reset_index(drop=True)
        return result_df

    except Exception:
        # Shock Absorber: On any exception, return clean fallback stream
        return get_fallback_crude_data(days=days)


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_spr_levels(api_key: Optional[str] = None) -> pd.DataFrame:
    """
    Fetches weekly U.S. Strategic Petroleum Reserve (SPR) stock levels.
    
    Returns DataFrame with columns: ['date', 'spr_mbbl', 'days_of_cover_india']
    """
    key = api_key or os.getenv("EIA_API_KEY", "").strip()

    if not key:
        return get_fallback_spr_data()

    try:
        url = f"{EIA_V2_BASE_URL}/petroleum/stoc/wstk/data/"
        params = {
            "api_key": key,
            "frequency": "weekly",
            "data[0]": "value",
            "facets[series][]": "WTTSTUS1",  # US SPR Crude Stocks (Thousand Barrels)
            "sort[0][column]": "period",
            "sort[0][direction]": "desc",
            "length": 52
        }

        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            return get_fallback_spr_data()

        payload = response.json()
        data_rows = payload.get("response", {}).get("data", [])

        if not data_rows:
            return get_fallback_spr_data()

        df = pd.DataFrame(data_rows)
        df["spr_mbbl"] = pd.to_numeric(df["value"], errors="coerce") / 1000.0  # Convert to Millions of Barrels
        df = df.dropna(subset=["spr_mbbl"])
        df = df.rename(columns={"period": "date"})

        df["dt"] = pd.to_datetime(df["date"])
        df = df.sort_values("dt").reset_index(drop=True)

        # Static calculation for India's strategic days-of-cover baseline (~5.2 MBPD consumption)
        daily_consumption_india = 5.2
        df["days_of_cover_india"] = np.round(df["spr_mbbl"] / daily_consumption_india, 1)

        return df[["date", "spr_mbbl", "days_of_cover_india"]].tail(26).reset_index(drop=True)

    except Exception:
        return get_fallback_spr_data()