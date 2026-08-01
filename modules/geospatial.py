"""
Geospatial Module — Folium Dark Vector Map
Renders interactive dark maps with individual route-specific risk vector styling.
"""

import folium


def build_corridor_map(corridor_risk_score: float) -> folium.Map:
    """Builds interactive dark map with route-specific risk colors."""
    # Base Map centered between Middle East and India
    m = folium.Map(
        location=[18.5, 64.0],
        zoom_start=4,
        tiles="CartoDB dark_matter",
        zoom_control=True
    )

    # Route-Specific Risk Scores
    hormuz_risk = corridor_risk_score                          # High Risk (Chokepoint)
    red_sea_risk = max(10.0, corridor_risk_score * 0.45)        # Medium Risk
    cape_risk = max(5.0, corridor_risk_score * 0.15)           # Low Risk (Safe Alternate)

    def get_color(score):
        if score > 60:
            return "#EF4444"  # Red
        elif score > 30:
            return "#F97316"  # Orange / Amber
        return "#10B981"      # Green

    # Nodes (Locations)
    nodes = [
        {"name": "Strait of Hormuz", "coords": [26.5, 56.2], "risk": f"{hormuz_risk:.1f}", "color": get_color(hormuz_risk)},
        {"name": "Bab-el-Mandeb / Red Sea", "coords": [12.6, 43.3], "risk": f"{red_sea_risk:.1f}", "color": get_color(red_sea_risk)},
        {"name": "Fujairah Hub", "coords": [25.1, 56.3], "risk": f"{red_sea_risk:.1f}", "color": "#06B6D4"},
        {"name": "Vadinar Refinery", "coords": [22.4, 69.7], "risk": "Safe", "color": "#06B6D4"},
        {"name": "Panipat Refinery", "coords": [29.4, 76.9], "risk": "Safe", "color": "#06B6D4"}
    ]

    # Add Circle Markers for Nodes
    for node in nodes:
        folium.CircleMarker(
            location=node["coords"],
            radius=8 if "Refinery" not in node["name"] else 6,
            popup=f"<b>{node['name']}</b><br>Risk Index: {node['risk']}",
            color=node["color"],
            fill=True,
            fill_color=node["color"],
            fill_opacity=0.7
        ).add_to(m)

    # Individual Vector Lines
    # 1. Hormuz to Vadinar (High Risk)
    folium.PolyLine(
        locations=[[26.5, 56.2], [22.4, 69.7]],
        color=get_color(hormuz_risk),
        weight=3,
        opacity=0.8,
        dash_array="5, 10" if hormuz_risk > 50 else None
    ).add_to(m)

    # 2. Red Sea to Vadinar (Medium Risk)
    folium.PolyLine(
        locations=[[12.6, 43.3], [22.4, 69.7]],
        color=get_color(red_sea_risk),
        weight=2,
        opacity=0.6
    ).add_to(m)

    # 3. Southern Ocean / Atlantic Bypass (Low Risk)
    folium.PolyLine(
        locations=[[-5.0, 50.0], [12.0, 65.0], [22.4, 69.7]],
        color=get_color(cape_risk),
        weight=2,
        opacity=0.5
    ).add_to(m)

    return m
