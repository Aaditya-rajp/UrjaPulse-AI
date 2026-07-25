"""
UrjaPulse AI — Industrial Geospatial & Supply Registry
Hardcoded reference coordinates, capacities, and crude grade compatibility matrix.
"""

# Maritime Chokepoints
CHOKEPOINTS = {
    "Strait_of_Hormuz": {
        "name": "Strait of Hormuz",
        "lat": 26.5667,
        "lon": 56.2500,
        "share_of_india_imports": 0.45,  # 45% of Indian imports pass through
        "status": "CRITICAL",
        "description": "Primary transit corridor for Middle Eastern crude (Ras Tanura, Basra, Fujairah)."
    },
    "Bab_el_Mandeb": {
        "name": "Bab-el-Mandeb / Red Sea",
        "lat": 12.5833,
        "lon": 43.3333,
        "share_of_india_imports": 0.15,
        "status": "ELEVATED_RISK",
        "description": "Gateway to Suez Canal for European & Mediterranean flows."
    },
    "Strait_of_Malacca": {
        "name": "Strait of Malacca",
        "lat": 1.4300,
        "lon": 102.1500,
        "share_of_india_imports": 0.05,
        "status": "MONITORED",
        "description": "Secondary route for East Asian & Pacific product transfers."
    }
}

# Major Indian Refineries
INDIAN_REFINERIES = {
    "Jamnagar": {
        "name": "Jamnagar Refinery (Reliance)",
        "lat": 22.3522,
        "lon": 69.8540,
        "capacity_mbpd": 1.24,
        "preferred_grades": ["Arab Heavy", "Basra Medium", "Urals"],
        "state": "Gujarat"
    },
    "Vadinar": {
        "name": "Vadinar Refinery (Nayara)",
        "lat": 22.3881,
        "lon": 69.7022,
        "capacity_mbpd": 0.40,
        "preferred_grades": ["Arab Light", "Urals", "Maya"],
        "state": "Gujarat"
    },
    "Panipat": {
        "name": "Panipat Refinery (IOCL)",
        "lat": 29.3889,
        "lon": 76.9631,
        "capacity_mbpd": 0.30,
        "preferred_grades": ["Arab Light", "Bonny Light"],
        "state": "Haryana"
    },
    "Mangalore": {
        "name": "Mangalore Refinery (MRPL)",
        "lat": 12.9912,
        "lon": 74.8118,
        "capacity_mbpd": 0.30,
        "preferred_grades": ["Arab Heavy", "Oman Blend"],
        "state": "Karnataka"
    },
    "Barauni": {
        "name": "Barauni Refinery (IOCL)",
        "lat": 25.4800,
        "lon": 86.0100,
        "capacity_mbpd": 0.12,
        "preferred_grades": ["Assam Crude", "Low Sulfur Heavy"],
        "state": "Bihar"
    }
}

# Alternate Supply Origins & Ports (For Node 02 Reranking Matrix)
ALTERNATE_SUPPLY_ORIGINS = {
    "US_Gulf_Coast": {
        "name": "US Gulf Coast (WTI Houston)",
        "lat": 29.7604,
        "lon": -95.3698,
        "transit_days_base": 28,
        "freight_base_usd_bbl": 4.50,
        "api_gravity": 40.0,
        "grade_compat": "High (Light Sweet)",
        "max_capacity_mbpd": 0.80
    },
    "Santos_Brazil": {
        "name": "Santos Basin (Tupi Crude)",
        "lat": -23.9608,
        "lon": -46.3339,
        "transit_days_base": 24,
        "freight_base_usd_bbl": 3.80,
        "api_gravity": 29.5,
        "grade_compat": "Very High (Medium Sweet)",
        "max_capacity_mbpd": 0.50
    },
    "Bonny_Nigeria": {
        "name": "Bonny Terminal (Nigeria)",
        "lat": 4.4500,
        "lon": 7.1667,
        "transit_days_base": 20,
        "freight_base_usd_bbl": 3.20,
        "api_gravity": 35.3,
        "grade_compat": "High (Light Sweet)",
        "max_capacity_mbpd": 0.40
    },
    "Primorsk_Russia": {
        "name": "Primorsk Port (Urals Crude)",
        "lat": 60.3667,
        "lon": 28.6333,
        "transit_days_base": 32,
        "freight_base_usd_bbl": 5.10,
        "api_gravity": 30.6,
        "grade_compat": "High (Sour Medium)",
        "max_capacity_mbpd": 0.60
    },
    "Fujairah_UAE": {
        "name": "Fujairah Hub (Outside Hormuz)",
        "lat": 25.1167,
        "lon": 56.3333,
        "transit_days_base": 4,
        "freight_base_usd_bbl": 1.10,
        "api_gravity": 31.0,
        "grade_compat": "Exact Match",
        "max_capacity_mbpd": 0.35
    }
}