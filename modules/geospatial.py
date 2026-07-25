"""
UrjaPulse AI — Geospatial Intelligence Map Module
Renders a high-density dark vector map with glowing HTML DivIcons,
active corridor overlays, and pulsating chokepoint beacons.
"""

from typing import Optional
import folium

from data.industrial_registry import CHOKEPOINTS, INDIAN_REFINERIES, ALTERNATE_SUPPLY_ORIGINS


def build_corridor_map(
    corridor_risk_score: float,
    selected_corridor: str = "Persian Gulf -> Jamnagar/Vadinar"
) -> folium.Map:
    """Constructs Folium dark map with custom neon DivIcon markers and glowing flow vectors."""
    m = folium.Map(
        location=[18.5, 62.0],
        zoom_start=4,
        tiles="CartoDB dark_matter",
        control_scale=False
    )

    # Determine Active Risk Color Palette
    if corridor_risk_score >= 70.0:
        main_risk_color = "#EF4444"  # Critical Red
        glow_shadow = "rgba(239, 68, 68, 0.6)"
    elif corridor_risk_score >= 40.0:
        main_risk_color = "#F97316"  # Warning Amber
        glow_shadow = "rgba(249, 115, 22, 0.6)"
    else:
        main_risk_color = "#10B981"  # Safe Green
        glow_shadow = "rgba(16, 185, 129, 0.6)"

    # 1. Chokepoints (Glowing Red/Amber Warning Beacons)
    for key, ckp in CHOKEPOINTS.items():
        color = main_risk_color if key == "Strait_of_Hormuz" else "#F97316"
        
        # HTML DivIcon Badge
        icon_html = f"""
        <div style="
            background-color: #12141A;
            border: 1px solid {color};
            border-radius: 4px;
            padding: 3px 6px;
            color: #F8FAFC;
            font-family: monospace;
            font-size: 10px;
            font-weight: bold;
            box-shadow: 0 0 10px {glow_shadow};
            white-space: nowrap;
            display: flex;
            align-items: center;
            gap: 4px;">
            <span style="color: {color};">❗</span> {ckp['name']}
        </div>
        """
        
        folium.Marker(
            location=[ckp["lat"], ckp["lon"]],
            icon=folium.DivIcon(html=icon_html, icon_size=(120, 24), icon_anchor=(60, 12)),
            tooltip=f"{ckp['name']} (Risk: {corridor_risk_score}/100)"
        ).add_to(m)

        folium.Circle(
            location=[ckp["lat"], ckp["lon"]],
            radius=160_000 + (corridor_risk_score * 2_000),
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.18,
            weight=1.5
        ).add_to(m)

    # 2. Indian Refineries (Glowing Cyan/Blue Badges)
    for name, ref in INDIAN_REFINERIES.items():
        ref_html = f"""
        <div style="
            background-color: #0F172A;
            border: 1px solid #38BDF8;
            border-radius: 4px;
            padding: 2px 6px;
            color: #F8FAFC;
            font-family: monospace;
            font-size: 10px;
            box-shadow: 0 0 8px rgba(56, 189, 248, 0.5);
            white-space: nowrap;">
            🏭 {ref['name'].split()[0]}
        </div>
        """
        folium.Marker(
            location=[ref["lat"], ref["lon"]],
            icon=folium.DivIcon(html=ref_html, icon_size=(90, 22), icon_anchor=(45, 11)),
            tooltip=f"Refinery: {ref['name']} ({ref['capacity_mbpd']} MBPD)"
        ).add_to(m)

    # 3. Alternate Supply Hubs (Glowing Emerald Green Anchor Badges)
    for key, hub in ALTERNATE_SUPPLY_ORIGINS.items():
        hub_html = f"""
        <div style="
            background-color: #064E3B;
            border: 1px solid #10B981;
            border-radius: 4px;
            padding: 2px 6px;
            color: #ECFDF5;
            font-family: monospace;
            font-size: 10px;
            font-weight: bold;
            box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);
            white-space: nowrap;">
            ⚓ {hub['name'].split()[0]}
        </div>
        """
        folium.Marker(
            location=[hub["lat"], hub["lon"]],
            icon=folium.DivIcon(html=hub_html, icon_size=(90, 22), icon_anchor=(45, 11)),
            tooltip=f"Supply Origin: {hub['name']}"
        ).add_to(m)

    # 4. Maritime Flow Vectors
    _add_maritime_vectors(m, corridor_risk_score)

    return m


def _add_maritime_vectors(m: folium.Map, corridor_risk_score: float) -> None:
    """Draws styled polyline vectors representing active crude corridors."""
    jamnagar = [INDIAN_REFINERIES["Jamnagar"]["lat"], INDIAN_REFINERIES["Jamnagar"]["lon"]]
    mangalore = [INDIAN_REFINERIES["Mangalore"]["lat"], INDIAN_REFINERIES["Mangalore"]["lon"]]

    fujairah_loc = [ALTERNATE_SUPPLY_ORIGINS["Fujairah_UAE"]["lat"], ALTERNATE_SUPPLY_ORIGINS["Fujairah_UAE"]["lon"]]
    santos_loc = [ALTERNATE_SUPPLY_ORIGINS["Santos_Brazil"]["lat"], ALTERNATE_SUPPLY_ORIGINS["Santos_Brazil"]["lon"]]
    bonny_loc = [ALTERNATE_SUPPLY_ORIGINS["Bonny_Nigeria"]["lat"], ALTERNATE_SUPPLY_ORIGINS["Bonny_Nigeria"]["lon"]]

    # Primary Hormuz Corridor (Critical Orange/Red)
    folium.PolyLine(
        locations=[fujairah_loc, [26.5, 56.2], jamnagar],
        color="#EF4444" if corridor_risk_score > 60 else "#F97316",
        weight=2.5,
        opacity=0.85,
        dash_array="6, 6"
    ).add_to(m)

    # Safe Reroute Corridors (Emerald Green)
    folium.PolyLine(
        locations=[santos_loc, [-34.0, 18.0], mangalore],
        color="#10B981",
        weight=2.0,
        opacity=0.75,
        dash_array="6, 6"
    ).add_to(m)

    folium.PolyLine(
        locations=[bonny_loc, [-34.0, 18.0], jamnagar],
        color="#10B981",
        weight=2.0,
        opacity=0.75,
        dash_array="6, 6"
    ).add_to(m)