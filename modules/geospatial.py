"""
Geospatial Intelligence Module — Folium Dark Vector Map Engine
Renders high-density dark vector maps with route-specific risk scoring, 
custom glowing HTML DivIcons, and interactive chokepoint telemetry.
"""

import folium
from folium import DivIcon


def _get_risk_color(score: float) -> str:
    """Returns hexadecimal color code based on numerical risk score."""
    if score >= 60.0:
        return "#EF4444"  # Critical Red
    elif score >= 35.0:
        return "#F97316"  # Warning Orange
    return "#10B981"      # Safe Emerald Green


def build_corridor_map(corridor_risk_score: float) -> folium.Map:
    """
    Builds an executive-grade dark vector map showing global supply routes, 
    individual route risk scores, and refinery arrival nodes.
    """
    # Map view centered over the Arabian Sea / Indian Ocean trade lanes
    m = folium.Map(
        location=[19.0, 68.0],
        zoom_start=4,
        tiles="CartoDB dark_matter",
        zoom_control=True,
        control_scale=True
    )

    # -------------------------------------------------------------
    # 1. ROUTE-SPECIFIC RISK COMPUTATION
    # -------------------------------------------------------------
    # Chokepoint 1: Strait of Hormuz (Direct Middle East corridor - 100% Exposed)
    hormuz_risk = round(corridor_risk_score, 1)
    hormuz_color = _get_risk_color(hormuz_risk)

    # Chokepoint 2: Red Sea / Bab-el-Mandeb (Suez / Red Sea transit)
    red_sea_risk = round(max(10.0, corridor_risk_score * 0.45), 1)
    red_sea_color = _get_risk_color(red_sea_risk)

    # Route 3: Atlantic / Cape of Good Hope Bypass (Alternate origin - Low risk)
    cape_risk = round(max(5.0, corridor_risk_score * 0.15), 1)
    cape_color = _get_risk_color(cape_risk)

    # -------------------------------------------------------------
    # 2. CHOKEPOINTS & SUPPLY HUBS (NODES)
    # -------------------------------------------------------------
    hubs = [
        {
            "name": "Strait of Hormuz",
            "type": "Critical Chokepoint",
            "coords": [26.5, 56.2],
            "risk": f"{hormuz_risk} / 100",
            "color": hormuz_color,
            "detail": "100% Exposed to Middle East Blockade Risks"
        },
        {
            "name": "Bab-el-Mandeb / Red Sea",
            "type": "Transit Corridor",
            "coords": [12.6, 43.3],
            "risk": f"{red_sea_risk} / 100",
            "color": red_sea_color,
            "detail": "Maritime Friction & Missile Defense Zone"
        },
        {
            "name": "Fujairah Bunkering Hub",
            "type": "Primary Alternate Hub",
            "coords": [25.1, 56.3],
            "risk": f"{red_sea_risk} / 100",
            "color": "#06B6D4",
            "detail": "Gulf of Oman Offshore Crude Pipeline Bypass"
        },
        {
            "name": "Bonny Light (West Africa)",
            "type": "Secondary Origin",
            "coords": [4.3, 6.9],
            "risk": f"{cape_risk} / 100",
            "color": "#10B981",
            "detail": "Atlantic Ocean Route — Bypasses Middle East"
        }
    ]

    for hub in hubs:
        # Custom Glowing Neon Marker
        icon_html = f"""
        <div style="
            background-color: {hub['color']};
            width: 14px;
            height: 14px;
            border-radius: 50%;
            border: 2px solid #0A0B0E;
            box-shadow: 0 0 10px {hub['color']};
        "></div>
        """
        
        popup_html = f"""
        <div style="font-family: monospace; background-color: #12141A; color: #E2E8F0; padding: 10px; border-radius: 6px; border: 1px solid {hub['color']}; min-width: 180px;">
            <b style="color: {hub['color']}; font-size: 12px;">{hub['name']}</b><br/>
            <span style="color: #94A3B8; font-size: 10px;">TYPE: {hub['type']}</span><br/>
            <hr style="border: 0; border-top: 1px solid #1E222D; margin: 6px 0;"/>
            <div style="font-size: 11px;"><b>Risk Score:</b> <span style="color: {hub['color']};">{hub['risk']}</span></div>
            <div style="font-size: 10px; color: #CBD5E1; margin-top: 4px;">{hub['detail']}</div>
        </div>
        """

        folium.Marker(
            location=hub["coords"],
            icon=DivIcon(icon_size=(14, 14), icon_anchor=(7, 7), html=icon_html),
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{hub['name']} (Risk: {hub['risk']})"
        ).add_to(m)

    # -------------------------------------------------------------
    # 3. DOMESTIC REFINERY NODES
    # -------------------------------------------------------------
    refineries = [
        {"name": "Vadinar Refinery", "coords": [22.4, 69.7], "cap": "20.0 MTPA"},
        {"name": "Panipat Refinery", "coords": [29.4, 76.9], "cap": "15.0 MTPA"},
        {"name": "Mangalore Refinery", "coords": [12.9, 74.8], "cap": "15.0 MTPA"}
    ]

    for ref in refineries:
        ref_icon = """
        <div style="
            background-color: #06B6D4;
            width: 10px;
            height: 10px;
            border-radius: 2px;
            border: 1px solid #FFFFFF;
            box-shadow: 0 0 8px #06B6D4;
        "></div>
        """
        ref_popup = f"""
        <div style="font-family: monospace; background-color: #12141A; color: #E2E8F0; padding: 8px; border-radius: 6px; border: 1px solid #06B6D4;">
            <b style="color: #06B6D4;">🏭 {ref['name']}</b><br/>
            <span style="font-size: 10px; color: #94A3B8;">Capacity: {ref['cap']}</span>
        </div>
        """
        folium.Marker(
            location=ref["coords"],
            icon=DivIcon(icon_size=(10, 10), icon_anchor=(5, 5), html=ref_icon),
            popup=folium.Popup(ref_popup, max_width=200),
            tooltip=f"Refinery: {ref['name']}"
        ).add_to(m)

    # -------------------------------------------------------------
    # 4. VECTOR SHIPPING LANES (POLY LINES)
    # -------------------------------------------------------------

    # Lane 1: Strait of Hormuz -> Vadinar (Direct High-Risk Corridor)
    folium.PolyLine(
        locations=[[26.5, 56.2], [23.5, 62.0], [22.4, 69.7]],
        color=hormuz_color,
        weight=4 if hormuz_risk > 50 else 3,
        opacity=0.9,
        dash_array="6, 8" if hormuz_risk > 50 else None,
        tooltip=f"Hormuz Direct Route | Risk: {hormuz_risk}/100"
    ).add_to(m)

    # Lane 2: Red Sea -> Vadinar (Arabian Sea Route)
    folium.PolyLine(
        locations=[[12.6, 43.3], [14.0, 55.0], [22.4, 69.7]],
        color=red_sea_color,
        weight=3,
        opacity=0.7,
        dash_array="4, 6" if red_sea_risk > 50 else None,
        tooltip=f"Red Sea Transit Route | Risk: {red_sea_risk}/100"
    ).add_to(m)

    # Lane 3: West Africa / Cape Bypass -> Mangalore / Vadinar (Safe Route)
    folium.PolyLine(
        locations=[[4.3, 6.9], [-5.0, 20.0], [-15.0, 45.0], [5.0, 65.0], [12.9, 74.8]],
        color=cape_color,
        weight=3,
        opacity=0.8,
        tooltip=f"Atlantic/Cape Safe Route | Risk: {cape_risk}/100"
    ).add_to(m)

    # Inland pipeline connection: Vadinar -> Panipat
    folium.PolyLine(
        locations=[[22.4, 69.7], [29.4, 76.9]],
        color="#64748B",
        weight=2,
        opacity=0.5,
        dash_array="2, 4",
        tooltip="Domestic Inland Crude Pipeline"
    ).add_to(m)

    return m
