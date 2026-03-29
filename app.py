# app.py
"""REALESTATE-1000 -- US Real Estate Market Scoring Platform."""
import json
import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data_logic import (
    AXES_LABELS,
    AXES_DESCRIPTIONS,
    STATE_FIPS,
    get_state_rankings,
    get_metro_rankings,
)
from ui_components import inject_css, render_radar_chart

APP_TITLE = "REALESTATE-1000"
PRIMARY_COLOR = "#2E8B57"
SCORES_HISTORY_FILE = os.path.join(os.path.dirname(__file__), "scores_history.json")

# State coordinates for map score labels
STATE_COORDS = {
    "AL": (32.8, -86.8), "AK": (64.2, -152.5), "AZ": (34.2, -111.7),
    "AR": (34.8, -92.2), "CA": (37.2, -119.5), "CO": (39.0, -105.5),
    "CT": (41.6, -72.7), "DE": (39.0, -75.5), "FL": (28.6, -82.4),
    "GA": (32.7, -83.5), "HI": (20.8, -156.3), "ID": (44.4, -114.6),
    "IL": (40.0, -89.2), "IN": (39.8, -86.2), "IA": (42.0, -93.5),
    "KS": (38.5, -98.3), "KY": (37.8, -85.3), "LA": (31.0, -92.0),
    "ME": (45.4, -69.2), "MD": (39.0, -76.7), "MA": (42.3, -71.8),
    "MI": (44.3, -85.4), "MN": (46.3, -94.3), "MS": (32.7, -89.7),
    "MO": (38.4, -92.5), "MT": (47.0, -109.6), "NE": (41.5, -99.8),
    "NV": (39.3, -116.6), "NH": (43.7, -71.6), "NJ": (40.1, -74.7),
    "NM": (34.5, -106.0), "NY": (42.9, -75.5), "NC": (35.5, -79.4),
    "ND": (47.4, -100.5), "OH": (40.4, -82.8), "OK": (35.5, -97.5),
    "OR": (43.9, -120.6), "PA": (40.9, -77.8), "RI": (41.7, -71.5),
    "SC": (33.9, -80.9), "SD": (44.4, -100.2), "TN": (35.9, -86.4),
    "TX": (31.5, -99.3), "UT": (39.3, -111.7), "VT": (44.1, -72.6),
    "VA": (37.5, -78.9), "WA": (47.4, -120.5), "WV": (38.6, -80.6),
    "WI": (44.6, -89.8), "WY": (43.0, -107.6), "DC": (38.9, -77.0),
}

SHORT_DESCRIPTIONS = {
    "Affordability": "Price-to-income, mortgage burden, rent-to-income",
    "Market Momentum": "Price YoY, inventory, days on market, sale-to-list",
    "Economic Foundation": "Unemployment, population growth, GDP",
    "Risk Profile": "FEMA disaster frequency (inverse)",
    "Investment Return": "Rental yield, 5-year appreciation",
}

WHY_EXPLANATIONS = {
    "Affordability": "Based on price-to-income ratio, mortgage burden, and rent-to-income ratio across all 50 states.",
    "Market Momentum": "Based on YoY price change, months of supply, days on market, and sale-to-list ratio.",
    "Economic Foundation": "Based on unemployment rate, population growth, and GDP growth.",
    "Risk Profile": "Based on FEMA disaster frequency over the past 5 years. Fewer disasters = higher score.",
    "Investment Return": "Based on rental yield and 5-year price appreciation.",
}

st.set_page_config(page_title=APP_TITLE, page_icon="\U0001f3e0", layout="wide")

# ---------------------------------------------------------------------------
# CSS Injection (shared across all scoring apps)
# ---------------------------------------------------------------------------
inject_css()
st.markdown("""
<style>
.block-container { padding-top: 1rem !important; }
header[data-testid="stHeader"] { display: none !important; }
footer { display: none !important; }
#MainMenu { display: none !important; }
.viewerBadge_container__r5tak { display: none !important; }
.styles_viewerBadge__CvC9N { display: none !important; }
[data-testid="stActionButtonIcon"] { display: none !important; }
[data-testid="manage-app-button"] { display: none !important; }
a[href*="github.com"] img { display: none !important; }
div[class*="viewerBadge"] { display: none !important; }
div[class*="StatusWidget"] { display: none !important; }
div[data-testid="stStatusWidget"] { display: none !important; }
iframe[title="streamlit_lottie.streamlit_lottie"] { display: none !important; }
.stDeployButton { display: none !important; }
div[class*="stToolbar"] { display: none !important; }
div.embeddedAppMetaInfoBar_container__DxxL1 { display: none !important; }
div[class*="embeddedAppMetaInfoBar"] { display: none !important; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def score_color(score):
    """Return a hex color based on score thresholds."""
    if score >= 800:
        return "#10b981"  # green
    elif score >= 600:
        return "#2E7BE6"  # blue
    elif score >= 400:
        return "#f59e0b"  # amber
    else:
        return "#ef4444"  # red


def axis_score_color(score):
    """Return a hex color based on axis score thresholds (/200)."""
    if score >= 160:
        return "#10b981"
    elif score >= 120:
        return "#2E7BE6"
    elif score >= 80:
        return "#f59e0b"
    else:
        return "#ef4444"


def _load_scores_history():
    """Load scores_history.json and return dict."""
    if os.path.exists(SCORES_HISTORY_FILE):
        with open(SCORES_HISTORY_FILE, "r") as f:
            return json.load(f)
    return {}


def render_score_delta(asset_name: str, current_total: int, prefix: str = ""):
    history = _load_scores_history()
    if not history:
        return
    dates = sorted(history.keys(), reverse=True)
    prev_score = None
    for d in dates:
        day_data = history[d]
        # Try direct key first
        s = day_data.get(asset_name)
        if s is not None:
            prev_score = s
            break
        # Try with prefix mapping (State:abbr -> full name)
        if prefix:
            for key, score_val in day_data.items():
                if key.startswith(prefix):
                    market_name = key[len(prefix):]
                    if prefix == "State:":
                        for fips_info in STATE_FIPS.values():
                            if fips_info["abbr"] == market_name:
                                market_name = fips_info["name"]
                                break
                    if market_name == asset_name:
                        prev_score = score_val
                        break
            if prev_score is not None:
                break
    if prev_score is None:
        return
    delta = current_total - prev_score
    if delta > 0:
        color, arrow = "#10b981", "&#9650;"
    elif delta < 0:
        color, arrow = "#ef4444", "&#9660;"
    else:
        color, arrow = "#94a3b8", "&#9644;"
    st.markdown(
        f'<div style="text-align:center; font-size:1.1em; font-weight:700; color:{color}; margin-top:-8px; margin-bottom:10px;">'
        f'{arrow} {delta:+d} from last record ({prev_score})'
        f'</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Data loading (cached)
# ---------------------------------------------------------------------------
@st.cache_data(ttl=3600)
def cached_state_rankings():
    return get_state_rankings()


@st.cache_data(ttl=3600)
def cached_metro_rankings():
    return get_metro_rankings()


# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab_dash, tab_detail, tab_rankings = st.tabs(["Dashboard", "Market Detail", "Rankings"])

# Load data with spinner
with st.spinner("Loading market data..."):
    try:
        state_rankings = cached_state_rankings()
    except Exception as e:
        state_rankings = []
    try:
        metro_rankings = cached_metro_rankings()
    except Exception as e:
        metro_rankings = []

# ===================================================================
# DASHBOARD TAB
# ===================================================================
with tab_dash:
    st.markdown(
        "<div style='font-size:1.5em; font-weight:900; color:#1e3a8a; margin-bottom:5px;'>"
        "Real Estate Dashboard</div>"
        "<p style='color:#64748b; margin-bottom:20px;'>"
        "Real-time overview of all 50 states + DC scored on a 1000-point scale.</p>",
        unsafe_allow_html=True,
    )

    with st.expander("How to use REALESTATE-1000"):
        st.markdown("""
**Dashboard** shows the overall Market Health Score, top/bottom movers, and state cards at a glance. Toggle between States and Metro Areas views.

**Market Detail** lets you drill into any state or metro area. View radar charts, score breakdowns, key metrics, and score history.

**Rankings** shows the full ranking table and scoring methodology.

**Data Sources**: US Census Bureau (ACS 2023), Bureau of Labor Statistics, Redfin, FEMA, Bureau of Economic Analysis. All public, no authentication required.
""")

    # View toggle
    view_mode = st.radio("View", ["States", "Metro Areas"], horizontal=True, label_visibility="collapsed")

    if view_mode == "States":
        rankings = state_rankings
    else:
        rankings = metro_rankings

    if not rankings:
        st.error("No data available.")
        st.stop()

    # Sort by total score descending
    all_scores = sorted(rankings, key=lambda x: x["total"], reverse=True)

    # Market Health Score
    avg_score = int(sum(s["total"] for s in all_scores) / len(all_scores))
    if avg_score >= 700:
        health_color, health_label = "#10b981", "STRONG"
    elif avg_score >= 500:
        health_color, health_label = "#2E7BE6", "MODERATE"
    else:
        health_color, health_label = "#ef4444", "WEAK"

    count_label = f"{len(all_scores)} states" if view_mode == "States" else f"{len(all_scores)} metro areas"

    st.markdown(
        f"""<div style="text-align:center; padding:25px; background:linear-gradient(135deg, #f8fafc, #e2e8f0);
        border-radius:20px; margin-bottom:25px;">
        <div style="font-size:0.9em; color:#64748b; font-weight:700; letter-spacing:2px;">
        MARKET HEALTH SCORE</div>
        <div style="font-size:4em; font-weight:900; color:{health_color}; line-height:1.1;">
        {avg_score}</div>
        <div style="font-size:1em; font-weight:700; color:{health_color};">{health_label}</div>
        <div style="font-size:0.8em; color:#94a3b8; margin-top:5px;">
        Average across {count_label}</div>
        </div>""",
        unsafe_allow_html=True,
    )

    # Top / Bottom movers
    history = _load_scores_history()
    if history:
        dates = sorted(history.keys(), reverse=True)
        if dates:
            prev = history[dates[0]]
            prefix = "State:" if view_mode == "States" else "Metro:"
            deltas = []
            for s in all_scores:
                # Find previous score using prefix mapping
                prev_score = None
                for key, score_val in prev.items():
                    if key.startswith(prefix):
                        market_name = key[len(prefix):]
                        if view_mode == "States":
                            for fips_info in STATE_FIPS.values():
                                if fips_info["abbr"] == market_name:
                                    market_name = fips_info["name"]
                                    break
                        if market_name == s["name"]:
                            prev_score = score_val
                            break
                if prev_score is not None:
                    deltas.append({"name": s["name"], "delta": s["total"] - prev_score})

            if deltas and any(d["delta"] != 0 for d in deltas):
                deltas.sort(key=lambda x: x["delta"], reverse=True)
                top_movers = deltas[:3]
                bottom_movers = sorted(deltas, key=lambda x: x["delta"])[:3]

                mv1, mv2 = st.columns(2)
                with mv1:
                    st.markdown("<div style='font-size:1em; font-weight:700; color:#10b981; margin-bottom:10px;'>Top Movers</div>", unsafe_allow_html=True)
                    for m in top_movers:
                        if m["delta"] > 0:
                            st.markdown(f"""
                            <div style="display:flex; justify-content:space-between; align-items:center; padding:10px 14px; background:#f0fdf4; border-radius:8px; margin-bottom:6px;">
                                <span style="font-weight:600; color:#1e293b;">{m['name']}</span>
                                <span style="font-weight:700; color:#10b981;">&#9650; {m['delta']:+d}</span>
                            </div>
                            """, unsafe_allow_html=True)
                with mv2:
                    st.markdown("<div style='font-size:1em; font-weight:700; color:#ef4444; margin-bottom:10px;'>Bottom Movers</div>", unsafe_allow_html=True)
                    for m in bottom_movers:
                        if m["delta"] < 0:
                            st.markdown(f"""
                            <div style="display:flex; justify-content:space-between; align-items:center; padding:10px 14px; background:#fef2f2; border-radius:8px; margin-bottom:6px;">
                                <span style="font-weight:600; color:#1e293b;">{m['name']}</span>
                                <span style="font-weight:700; color:#ef4444;">&#9660; {m['delta']:+d}</span>
                            </div>
                            """, unsafe_allow_html=True)

                st.markdown("<div style='height:15px;'></div>", unsafe_allow_html=True)

    # State/Metro cards grid
    label = "All States" if view_mode == "States" else "All Metro Areas"
    st.markdown(f"<div class='section-title'>{label}</div>", unsafe_allow_html=True)

    cols = st.columns(3)
    for i, s in enumerate(all_scores):
        score = s["total"]
        if score >= 700:
            border_color = "#10b981"
        elif score >= 500:
            border_color = "#2E7BE6"
        elif score >= 300:
            border_color = "#f59e0b"
        else:
            border_color = "#ef4444"

        abbr_label = s.get("abbr", "")
        name_label = s["name"]
        extra = f"${s['data']['median_home_price']:,}" if "data" in s and "median_home_price" in s.get("data", {}) else ""

        with cols[i % 3]:
            st.markdown(
                f"""<div style="background:#fff; border-radius:12px; padding:18px; margin-bottom:12px;
                border-left:4px solid {border_color}; box-shadow:0 2px 8px rgba(0,0,0,0.04);">
                <div style="font-size:0.75em; color:#94a3b8; font-weight:600;">{abbr_label}</div>
                <div style="font-size:0.95em; font-weight:700; color:#1e293b; margin:2px 0;">
                {name_label}</div>
                <div style="display:flex; justify-content:space-between; align-items:baseline;">
                <span style="font-size:1.8em; font-weight:900; color:{border_color};">{score}</span>
                <span style="font-size:0.8em; color:#94a3b8;">{extra}</span>
                </div></div>""",
                unsafe_allow_html=True,
            )



# ===================================================================
# MARKET DETAIL TAB
# ===================================================================
with tab_detail:
    view_mode_detail = st.radio("View", ["States", "Metro Areas"], horizontal=True, label_visibility="collapsed", key="detail_view")

    if view_mode_detail == "States":
        detail_rankings = state_rankings
    else:
        detail_rankings = metro_rankings

    if not detail_rankings:
        st.error("No data available.")
    else:
        name_list = [r["name"] for r in detail_rankings]

        # ----- Map at top of Market Detail -----
        _map_event = None
        scores_detail = [r["total"] for r in detail_rankings]

        if view_mode_detail == "States":
            _abbrs = [r["abbr"] for r in detail_rankings]
            _totals = [r["total"] for r in detail_rankings]
            _hovers = [f"{r['name']} ({r['abbr']})" for r in detail_rankings]

            fig_map = go.Figure()
            fig_map.add_trace(go.Choropleth(
                locations=_abbrs,
                locationmode="USA-states",
                z=_totals,
                colorscale=[
                    [0, "#d32f2f"],
                    [0.5, "#ffd54f"],
                    [1, "#2e7d32"],
                ],
                zmin=min(scores_detail) - 20,
                zmax=max(scores_detail) + 20,
                text=_hovers,
                hoverinfo="text",
                colorbar=dict(title="Score", thickness=15, len=0.6),
            ))

            # Score labels on each state
            _lats = []
            _lons = []
            _labels = []
            for r in detail_rankings:
                coords = STATE_COORDS.get(r["abbr"])
                if coords:
                    _lats.append(coords[0])
                    _lons.append(coords[1])
                    _labels.append(str(r["total"]))

            if _lats:
                fig_map.add_trace(go.Scattergeo(
                    locationmode="USA-states",
                    lat=_lats,
                    lon=_lons,
                    text=_labels,
                    mode="markers+text",
                    marker=dict(size=32, color="white", opacity=0.85, line=dict(width=0)),
                    textfont=dict(size=10, color="#1e293b", family="Arial Black"),
                    hoverinfo="skip",
                    showlegend=False,
                ))

            fig_map.update_layout(
                geo=dict(scope="usa", bgcolor="rgba(0,0,0,0)", lakecolor="#E8F4FD"),
                margin=dict(l=0, r=0, t=0, b=0),
                height=500,
                paper_bgcolor="white",
                dragmode=False,
            )
            fig_map.update_geos(projection_type="albers usa")
            _map_event = st.plotly_chart(fig_map, use_container_width=True, config={
                "displayModeBar": False, "scrollZoom": False, "doubleClick": False,
            }, on_select="rerun", key="state_map_detail")

        else:
            # Metro bubble map
            df_metro = pd.DataFrame([
                {
                    "name": r["name"],
                    "lat": r["lat"],
                    "lng": r["lng"],
                    "score": r["total"],
                    "state": r["state"],
                    "Affordability": r["axes"]["Affordability"],
                    "Momentum": r["axes"]["Market Momentum"],
                    "Economy": r["axes"]["Economic Foundation"],
                    "Risk": r["axes"]["Risk Profile"],
                    "Investment": r["axes"]["Investment Return"],
                }
                for r in detail_rankings
            ])

            fig_metro = px.scatter_geo(
                df_metro,
                lat="lat",
                lon="lng",
                size="score",
                color="score",
                hover_name="name",
                hover_data={
                    "lat": False, "lng": False, "state": True,
                    "score": True,
                    "Affordability": True,
                    "Momentum": True,
                    "Economy": True,
                    "Risk": True,
                    "Investment": True,
                },
                color_continuous_scale=[
                    [0, "#d32f2f"],
                    [0.5, "#ffd54f"],
                    [1, "#2e7d32"],
                ],
                range_color=[min(scores_detail) - 20, max(scores_detail) + 20],
                scope="usa",
                size_max=25,
                labels={"score": "Total Score"},
            )
            fig_metro.update_layout(
                geo=dict(bgcolor='rgba(0,0,0,0)', lakecolor='#E8F4FD'),
                margin=dict(l=0, r=0, t=0, b=0),
                height=480,
                dragmode=False,
                coloraxis_colorbar=dict(title="Score", thickness=15, len=0.6),
            )
            st.plotly_chart(fig_metro, use_container_width=True, config={
                "displayModeBar": False, "scrollZoom": False, "doubleClick": False,
            })

        # Handle map click to update selectbox
        if view_mode_detail == "States" and _map_event:
            try:
                _points = _map_event.selection.points
                if _points:
                    _clicked_loc = _points[0].get("location", "")
                    for r in detail_rankings:
                        if r.get("abbr") == _clicked_loc:
                            st.session_state["market_detail_select"] = r["name"]
                            break
            except Exception:
                pass

        selected_name = st.selectbox("Select a market to view details", name_list, key="market_detail_select")
        selected = next((r for r in detail_rankings if r["name"] == selected_name), None)

        if selected:
            d = selected["data"]
            total = selected["total"]
            axes = selected["axes"]
            sc = score_color(total)

            # Total score centered
            st.markdown(f"""
            <div style="text-align:center; margin-top:4px; margin-bottom:10px;">
                <div style="font-size:14px; letter-spacing:2px; color:#666;">TOTAL SCORE</div>
                <div style="font-size:90px; font-weight:800; color:#2E7BE6; line-height:1;">
                    {total}
                    <span style="font-size:35px; color:#BBB;">/ 1000</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Score delta from last record
            prefix = "State:" if view_mode_detail == "States" else "Metro:"
            render_score_delta(selected["name"], total, prefix=prefix)

            # Layout: Radar Chart (left) + Score Cards (right)
            col_left, col_right = st.columns([1.5, 1])

            with col_left:
                st.markdown("<div style='font-size: 1.1em; font-weight: bold; color: #333; margin-top: -10px; margin-bottom: 5px;'>I. Intelligence Radar</div>", unsafe_allow_html=True)

                fig_r = render_radar_chart(
                    {"axes": axes, "name": selected["name"]},
                    None,
                    AXES_LABELS,
                )
                st.plotly_chart(fig_r, use_container_width=True)

            with col_right:
                st.markdown("<div style='font-size: 0.9em; font-weight: bold; color: #333; margin-top: -10px; margin-bottom: 15px; border-left: 3px solid #2E7BE6; padding-left: 8px;'>II. ANALYSIS SCORE METRICS</div>", unsafe_allow_html=True)
                # Individual axis score cards
                for ax_name in AXES_LABELS:
                    ax_val = axes.get(ax_name, 0)
                    desc = SHORT_DESCRIPTIONS.get(ax_name, "")
                    st.markdown(f"""
                    <div style="
                        background-color: #FFFFFF;
                        padding: 20px;
                        border-radius: 12px;
                        margin-bottom: 12px;
                        border: 1px solid #E0E0E0;
                        border-left: 8px solid #2E7BE6;
                        box-shadow: 2px 2px 5px rgba(0,0,0,0.07);
                    ">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                            <span style="font-size: 1.4em; font-weight: 800; color: #333333;">{ax_name}</span>
                            <span style="font-size: 1.9em; font-weight: 900; line-height: 1;">
                                <span style="color: #2E7BE6;">{ax_val}</span>
                                <span style="color:#bbb;font-size:0.5em;font-weight:600;"> /200</span>
                            </span>
                        </div>
                        <p style="font-size: 1.05em; color: #777777; margin: 0; line-height: 1.3; font-weight: 500;">{desc}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    with st.expander(f"Why {int(ax_val)}?", expanded=False):
                        if ax_name == "Affordability":
                            _pti = round(d["median_home_price"] / d["median_income"], 1) if d.get("median_income") else "N/A"
                            st.markdown(f"""
**Formula:** `Percentile rank of price-to-income (inverted) + mortgage burden (inverted) + rent-to-income (inverted)`

**Raw Data:** Median Home Price: ${int(d.get('median_home_price', 0)):,} | Median Income: ${int(d.get('median_income', 0)):,} | Price-to-Income: {_pti}x | Mortgage Rate: {d.get('mortgage_rate', 'N/A')}%

**Source:** Census ACS 2023, Redfin, Freddie Mac
                            """)
                        elif ax_name == "Market Momentum":
                            st.markdown(f"""
**Formula:** `Percentile rank of YoY price change + months of supply (inverted) + days on market (inverted) + sale-to-list ratio`

**Raw Data:** YoY Price Change: {d.get('yoy_price_change', 'N/A')}% | Months of Supply: {d.get('months_inventory', 'N/A')} | Days on Market: {d.get('days_on_market', 'N/A')} | Sale-to-List: {d.get('sale_to_list_ratio', 'N/A')}

**Source:** Redfin
                            """)
                        elif ax_name == "Economic Foundation":
                            st.markdown(f"""
**Formula:** `Percentile rank of unemployment (inverted) + population growth + GDP growth`

**Raw Data:** Unemployment: {d.get('unemployment', 'N/A')}% | Pop Growth: {d.get('pop_growth', 'N/A')}% | GDP Growth: {d.get('gdp_growth', 'N/A')}%

**Source:** BLS, Census Bureau, BEA
                            """)
                        elif ax_name == "Risk Profile":
                            st.markdown(f"""
**Formula:** `Percentile rank of FEMA disaster frequency (inverted: fewer disasters = higher score)`

**Raw Data:** Disaster Events (5yr): {d.get('disaster_freq', 'N/A')}

**Source:** FEMA Disaster Declarations API
                            """)
                        elif ax_name == "Investment Return":
                            st.markdown(f"""
**Formula:** `Percentile rank of rental yield + 5-year price appreciation`

**Raw Data:** Rental Yield: {d.get('cap_rate', 'N/A')}% | 5yr Appreciation: {d.get('price_appreciation_5yr', 'N/A')}%

**Source:** Census ACS 2023, Redfin
                            """)

            # Key metrics (snapshot style)
            st.markdown(
                "<div style='font-size: 0.9em; font-weight: bold; color: #333; margin-top: 10px; margin-bottom: 15px; border-left: 3px solid #2E7BE6; padding-left: 8px;'>III. KEY METRICS SNAPSHOT</div>",
                unsafe_allow_html=True,
            )

            # TOTAL / STRONGEST / WEAKEST summary row
            sc1, sc2, sc3 = st.columns(3)
            _best_ax = max(axes, key=axes.get) if axes else "N/A"
            _best_val = int(axes.get(_best_ax, 0))
            _worst_ax = min(axes, key=axes.get) if axes else "N/A"
            _worst_val = int(axes.get(_worst_ax, 0))
            sc1.markdown(f"""
            <div style="background:#f8fafc; border-radius:10px; padding:14px; margin-bottom:10px; border:1px solid #e2e8f0;">
                <div style="font-size:0.75em; color:#64748b; font-weight:600;">TOTAL SCORE</div>
                <div style="font-size:1.5em; font-weight:900; color:#1e293b; line-height:1.2;">{total} <span style="font-size:0.5em; color:#999;">/1000</span></div>
            </div>
            """, unsafe_allow_html=True)
            sc2.markdown(f"""
            <div style="background:#f0fdf4; border-radius:10px; padding:14px; margin-bottom:10px; border:1px solid #bbf7d0;">
                <div style="font-size:0.75em; color:#64748b; font-weight:600;">STRONGEST</div>
                <div style="font-size:1.5em; font-weight:900; color:#10b981; line-height:1.2;">{_best_ax} ({_best_val})</div>
            </div>
            """, unsafe_allow_html=True)
            sc3.markdown(f"""
            <div style="background:#fef2f2; border-radius:10px; padding:14px; margin-bottom:10px; border:1px solid #fecaca;">
                <div style="font-size:0.75em; color:#64748b; font-weight:600;">WEAKEST</div>
                <div style="font-size:1.5em; font-weight:900; color:#ef4444; line-height:1.2;">{_worst_ax} ({_worst_val})</div>
            </div>
            """, unsafe_allow_html=True)

            pti = round(d["median_home_price"] / d["median_income"], 1) if d["median_income"] else 0
            home_price = f"${int(d['median_home_price']):,}" if d["median_home_price"] else "N/A"
            income = f"${int(d['median_income']):,}" if d["median_income"] else "N/A"

            snapshot_items = [
                ("Median Home Price", home_price),
                ("Median Income", income),
                ("Price-to-Income", f"{pti}x"),
                ("Unemployment", f"{d['unemployment']}%"),
                ("Population Growth", f"{d['pop_growth']}%"),
                ("Disaster Events (5yr)", str(d["disaster_freq"])),
                ("Rental Yield", f"{d['cap_rate']}%"),
                ("5yr Appreciation", f"{d['price_appreciation_5yr']}%"),
                ("YoY Price Change", f"{d['yoy_price_change']}%"),
                ("Months of Supply", f"{d['months_inventory']}"),
                ("Days on Market", f"{d['days_on_market']}"),
            ]

            snap_cols = st.columns(4)
            for idx, (label, val) in enumerate(snapshot_items):
                with snap_cols[idx % 4]:
                    st.markdown(f"""
                    <div style="background:#f8fafc; border-radius:10px; padding:14px; margin-bottom:10px; border:1px solid #e2e8f0;">
                        <div style="font-size:0.75em; color:#64748b; font-weight:600;">{label}</div>
                        <div style="font-size:1.5em; font-weight:900; color:#2E7BE6; line-height:1.2;">{val}</div>
                    </div>
                    """, unsafe_allow_html=True)

            # Score History
            history_data = _load_scores_history()
            if history_data:
                st.markdown("#### Score History")

                dates = sorted(history_data.keys())
                if len(dates) >= 1:
                    sel_name = selected["name"]
                    hist_dates = []
                    hist_values = []
                    for date in dates:
                        day_data = history_data[date]
                        for key, score_val in day_data.items():
                            if key.startswith(prefix):
                                market_name = key[len(prefix):]
                                if view_mode_detail == "States":
                                    full_name = None
                                    for fips_info in STATE_FIPS.values():
                                        if fips_info["abbr"] == market_name:
                                            full_name = fips_info["name"]
                                            break
                                    if full_name is None:
                                        full_name = market_name
                                    market_name = full_name
                                if market_name == sel_name:
                                    hist_dates.append(date)
                                    hist_values.append(score_val)

                    if hist_values:
                        fig_daily = go.Figure()
                        fig_daily.add_trace(go.Scatter(
                            x=hist_dates,
                            y=hist_values,
                            mode='lines+markers',
                            line=dict(color='#2E7BE6', width=2),
                            marker=dict(size=5),
                            fill='tozeroy',
                            fillcolor='rgba(46,123,230,0.05)',
                            name=sel_name,
                        ))
                        fig_daily.update_layout(
                            yaxis=dict(range=[0, 1000], title="Score"),
                            height=250,
                            margin=dict(l=0, r=0, t=10, b=0),
                            plot_bgcolor='white',
                            hovermode="x unified",
                            clickmode='none',
                            dragmode=False,
                        )
                        st.plotly_chart(fig_daily, use_container_width=True, config={"displayModeBar": False})
                    else:
                        st.caption("No history data for the selected market yet.")


# ===================================================================
# RANKINGS TAB
# ===================================================================
with tab_rankings:
    view_mode_rank = st.radio("View", ["States", "Metro Areas"], horizontal=True, label_visibility="collapsed", key="rank_view")

    if view_mode_rank == "States":
        rank_rankings = state_rankings
    else:
        rank_rankings = metro_rankings

    if not rank_rankings:
        st.error("No data available.")
    else:
        st.markdown("#### Full Rankings")

        sorted_rankings = sorted(rank_rankings, key=lambda x: x["total"], reverse=True)
        history = _load_scores_history()
        prev_scores = {}
        if history:
            dates = sorted(history.keys(), reverse=True)
            if dates:
                prev_scores = history[dates[0]]

        for i, r in enumerate(sorted_rankings, 1):
            name = r["name"]
            score = r["total"]
            badge_label = r.get("abbr") or r.get("state") or ""
            badge_color = "#2E8B57"

            # Score color
            if score >= 800:
                bar_color = "#10b981"
            elif score >= 600:
                bar_color = "#2E7BE6"
            elif score >= 400:
                bar_color = "#f59e0b"
            else:
                bar_color = "#ef4444"

            # Change indicator
            prev = prev_scores.get(name)
            if prev is not None:
                delta = score - prev
                if delta > 0:
                    change_html = f'<span style="font-size:0.8em; font-weight:700; color:#10b981;">&#9650; +{delta}</span>'
                elif delta < 0:
                    change_html = f'<span style="font-size:0.8em; font-weight:700; color:#ef4444;">&#9660; {delta}</span>'
                else:
                    change_html = '<span style="font-size:0.8em; font-weight:700; color:#94a3b8;">&#9644; 0</span>'
            else:
                change_html = ""

            pct = score / 10
            st.markdown(
                f'<div style="display:flex; align-items:center; padding:14px 20px; background:#fff; border-radius:12px; margin-bottom:8px; border:1px solid #e2e8f0; box-shadow:0 1px 3px rgba(0,0,0,0.04);">'
                f'<div style="font-size:1.4em; font-weight:900; color:#94a3b8; width:40px;">#{i}</div>'
                f'<div style="flex:1;">'
                f'<div style="font-size:1.05em; font-weight:700; color:#1e293b;">{name}</div>'
                f'<span style="font-size:0.75em; background:{badge_color}; color:#fff; padding:2px 8px; border-radius:20px;">{badge_label}</span> '
                f'{change_html}'
                f'</div>'
                f'<div style="text-align:right; min-width:80px;">'
                f'<div style="font-size:1.5em; font-weight:900; color:{bar_color};">{score}</div>'
                f'<div style="background:#f1f5f9; border-radius:4px; height:6px; width:80px; margin-top:4px;">'
                f'<div style="background:{bar_color}; height:6px; border-radius:4px; width:{pct}%;"></div>'
                f'</div></div></div>',
                unsafe_allow_html=True,
            )

        with st.expander("Scoring Methodology"):
            st.markdown("### REALESTATE-1000 Scoring System")
            st.markdown("Each market is scored on 5 axes, each worth 0-200 points, for a maximum total of 1,000.")
            st.markdown("")
            for ax, desc in AXES_DESCRIPTIONS.items():
                st.markdown(f"**{ax}** (0-200): {desc}")
            st.markdown("")
            st.markdown("Data sources: US Census Bureau (ACS 2023), Bureau of Labor Statistics, Redfin, FEMA, Bureau of Economic Analysis.")
            st.markdown("Scores use proportional scaling. Lower risk = higher Risk Profile score (inverse scoring).")
