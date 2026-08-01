"""
Geospatial Intelligence Module — Folium Dark Vector Map Engine
Renders executive dark vector maps with explicit route labels, 
glowing HTML DivIcons, midpoint vector callouts, and interactive legend overlays.
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
    route-level text labels, and an integrated map legend.
    """
    # Base Map centered on Indian Ocean trade lanes
    m = folium.Map(
        location=[19.0, 65.0],
        zoom_start=4,
        tiles="CartoDB dark_matter",
        zoom_control=True,
        control_scale=True
    )

    # -------------------------------------------------------------
    # 1. ROUTE-SPECIFIC RISK COMPUTATION
    # -------------------------------------------------------------
    hormuz_risk = round(corridor_risk_score, 1)
    hormuz_color = _get_risk_color(hormuz_risk)

    red_sea_risk = round(max(10.0, corridor_risk_score * 0.45), 1)
    red_sea_color = _get_risk_color(red_sea_risk)

    cape_risk = round(max(5.0, corridor_risk_score * 0.15), 1)
    cape_color = _get_risk_color(cape_risk)

    # -------------------------------------------------------------
    # 2. SHIPPING LANES / POLY LINES WITH MIDPOINT LABELS
    # -------------------------------------------------------------
    routes = [
        {
            "id": "LANE 01",
            "name": "Strait of Hormuz Direct Route",
            "coords": [[26.5, 56.2], [23.5, 62.0], [22.4, 69.7]],
            "label_pos": [24.5, 61.0],  # Midpoint position for floating label
            "risk": hormuz_risk,
            "color": hormuz_color,
            "dash": "6, 8" if hormuz_risk > 50 else None
        },
        {
            "id": "LANE 02",
            "name": "Red Sea / Bab-el-Mandeb Route",
            "coords": [[12.6, 43.3], [14.0, 55.0], [22.4, 69.7]],
            "label_pos": [14.8, 54.0],  # Midpoint position
            "risk": red_sea_risk,
            "color": red_sea_color,
            "dash": "4, 6" if red_sea_risk > 50 else None
        },
        {
            "id": "LANE 03",
            "name": "Cape of Good Hope / Atlantic Route",
            "coords": [[4.3, 6.9], [-5.0, 20.0], [-15.0, 45.0], [5.0, 65.0], [12.9, 74.8]],
            "label_pos": [2.0, 58.0],   # Midpoint position
            "risk": cape_risk,
            "color": cape_color,
            "dash": None
        }
    ]

    # Draw Polylines and Midpoint Permanent Labels
    for r in routes:
        # Draw Line
        folium.PolyLine(
            locations=r["coords"],
            color=r["color"],
            weight=4 if r["risk"] > 50 else 3,
            opacity=0.85,
            dash_array=r["dash"],
            tooltip=f"<b>{r['id']}: {r['name']}</b><br/>Risk Index: {r['risk']}/100"
        ).add_to(m)

        # Permanent Text Badge Placed Directly on Map Route Midpoint
        label_html = f"""
        <div style="
            background: #12141A;
            border: 1px solid {r['color']};
            border-radius: 4px;
            padding: 2px 6px;
            font-family: monospace;
            font-size: 9px;
            font-weight: bold;
            color: #F8FAFC;
            box-shadow: 0 0 8px {r['color']};
            white-space: nowrap;
        ">
            <span style="color: {r['color']};">{r['id']}</span>: {r['name'].upper()} [{r['risk']}]
        </div>
        """
        
        folium.Marker(
            location=r["label_pos"],
            icon=DivIcon(icon_size=(160, 20), icon_anchor=(80, 10), html=label_html)
        ).add_to(m)

    # -------------------------------------------------------------
    # 3. CHOKEPOINTS & SUPPLY HUBS (NODES)
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
        icon_html = f"""
        <div style="
            background-color: {hub['color']};
            width: 12px;
            height: 12px;
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
            icon=DivIcon(icon_size=(12, 12), icon_anchor=(6, 6), html=icon_html),
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{hub['name']} (Risk: {hub['risk']})"
        ).add_to(m)

    # -------------------------------------------------------------
    # 4. DOMESTIC REFINERY ARRIVAL NODES
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
        folium.Marker(
            location=ref["coords"],
            icon=DivIcon(icon_size=(10, 10), icon_anchor=(5, 5), html=ref_icon),
            tooltip=f"Refinery Hub: {ref['name']} ({ref['cap']})"
        ).add_to(m)

    # -------------------------------------------------------------
    # 5. FLOATING MAP LEGEND OVERLAY
    # -------------------------------------------------------------
    legend_html = f"""
    <div style="
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 220px;
        background-color: #12141A;
        border: 1px solid #1E222D;
        border-radius: 6px;
        padding: 10px;
        font-family: monospace;
        font-size: 10px;
        color: #E2E8F0;
        z-index: 9999;
        box-shadow: 0 0 10px rgba(0,0,0,0.5);
    ">
        <b style="color: #F8FAFC;">MARITIME ROUTE RISK INDEX</b><br/>
        <hr style="border: 0; border-top: 1px solid #1E222D; margin: 4px 0 8px 0;"/>
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <span style="background: {hormuz_color}; width: 12px; height: 3px; display: inline-block; margin-right: 8px;"></span>
            <span>Lane 01: Hormuz ({hormuz_risk})</span>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <span style="background: {red_sea_color}; width: 12px; height: 3px; display: inline-block; margin-right: 8px;"></span>
            <span>Lane 02: Red Sea ({red_sea_risk})</span>
        </div>
        <div style="display: flex; align-items: center;">
            <span style="background: {cape_color}; width: 12px; height: 3px; display: inline-block; margin-right: 8px;"></span>
            <span>Lane 03: Atlantic/Cape ({cape_risk})</span>
        </div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    return m
