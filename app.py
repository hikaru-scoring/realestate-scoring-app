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

APP_TITLE = "REALESTATE-1000"
PRIMARY_COLOR = "#2E8B57"
SCORES_HISTORY_FILE = os.path.join(os.path.dirname(__file__), "scores_history.json")

st.set_page_config(page_title=APP_TITLE, page_icon="\U0001f3e0", layout="wide")

# ---------------------------------------------------------------------------
# CSS Injection (hide Streamlit chrome)
# ---------------------------------------------------------------------------
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
# Header
# ---------------------------------------------------------------------------
st.markdown(f"""
<div style="text-align:center; margin-bottom:10px;">
    <div style="font-size:38px; font-weight:900; color:{PRIMARY_COLOR};">REALESTATE-1000</div>
    <div style="font-size:16px; color:#64748B; margin-top:-4px;">US Real Estate Market Scoring</div>
    <div style="font-size:13px; color:#999; margin-top:2px;">Scoring all 50 states + DC based on real-time market data. Data: Census ACS 2023, BLS, Redfin, FEMA</div>
</div>
""", unsafe_allow_html=True)

# View toggle
view_mode = st.radio("View", ["States", "Metro Areas"], horizontal=True, label_visibility="collapsed")

# Load data with spinner
with st.spinner("Loading market data..."):
    try:
        if view_mode == "States":
            rankings = cached_state_rankings()
        else:
            rankings = cached_metro_rankings()
    except Exception as e:
        st.warning(f"Failed to load data: {e}")
        rankings = []

if not rankings:
    st.error("No data available.")
    st.stop()


# ---------------------------------------------------------------------------
# US Choropleth Map (States view) / Bubble Map (Metro view)
# ---------------------------------------------------------------------------
scores = [r["total"] for r in rankings]

if view_mode == "States":
    df_map = pd.DataFrame([
        {
            "abbr": r["abbr"],
            "name": r["name"],
            "score": r["total"],
            "Affordability": r["axes"]["Affordability"],
            "Momentum": r["axes"]["Market Momentum"],
            "Economy": r["axes"]["Economic Foundation"],
            "Risk": r["axes"]["Risk Profile"],
            "Investment": r["axes"]["Investment Return"],
        }
        for r in rankings
    ])

    fig_map = px.choropleth(
        df_map,
        locations="abbr",
        locationmode="USA-states",
        color="score",
        hover_name="name",
        hover_data={
            "abbr": False,
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
        range_color=[min(scores) - 20, max(scores) + 20],
        scope="usa",
        labels={"score": "Total Score"},
    )
    fig_map.update_layout(
        geo=dict(bgcolor='rgba(0,0,0,0)', lakecolor='#E8F4FD'),
        margin=dict(l=0, r=0, t=0, b=0),
        height=480,
        coloraxis_colorbar=dict(title="Score", thickness=15, len=0.6),
    )
    st.plotly_chart(fig_map, use_container_width=True)

else:
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
        for r in rankings
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
        range_color=[min(scores) - 20, max(scores) + 20],
        scope="usa",
        size_max=25,
        labels={"score": "Total Score"},
    )
    fig_metro.update_layout(
        geo=dict(bgcolor='rgba(0,0,0,0)', lakecolor='#E8F4FD'),
        margin=dict(l=0, r=0, t=0, b=0),
        height=480,
        coloraxis_colorbar=dict(title="Score", thickness=15, len=0.6),
    )
    st.plotly_chart(fig_metro, use_container_width=True)


# ---------------------------------------------------------------------------
# Detail View
# ---------------------------------------------------------------------------
st.markdown("---")
name_list = [r["name"] for r in rankings]
selected_name = st.selectbox("Select a market to view details", name_list)
selected = next((r for r in rankings if r["name"] == selected_name), None)

if selected:
    d = selected["data"]
    total = selected["total"]
    axes = selected["axes"]
    sc = score_color(total)

    # Total score centered
    st.markdown(f"""
    <div style="text-align:center; margin-top:4px; margin-bottom:10px;">
        <div style="font-size:14px; letter-spacing:2px; color:#666;">TOTAL SCORE</div>
        <div style="font-size:90px; font-weight:800; color:{sc}; line-height:1;">
            {total}
            <span style="font-size:35px; color:#BBB;">/ 1000</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Layout: Radar Chart (left) + Score Cards (right)
    col_left, col_right = st.columns([1.5, 1])

    with col_left:
        # Radar chart
        labels = list(axes.keys())
        values = list(axes.values())
        values_closed = values + [values[0]]
        labels_closed = labels + [labels[0]]

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values_closed,
            theta=labels_closed,
            fill='toself',
            fillcolor='rgba(46, 139, 87, 0.1)',
            line_color=PRIMARY_COLOR,
            line=dict(width=4),
            name=selected["name"],
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 200], gridcolor="#F0F0F0"),
                angularaxis=dict(rotation=90, direction="clockwise"),
                bgcolor='white',
            ),
            showlegend=False,
            margin=dict(l=50, r=50, t=20, b=20),
            height=500,
            clickmode='none',
            dragmode=False,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col_right:
        # Individual axis score cards
        for ax_name in AXES_LABELS:
            ax_val = axes.get(ax_name, 0)
            desc = AXES_DESCRIPTIONS.get(ax_name, "")
            st.markdown(f"""
            <div style="
                background-color: #FFFFFF;
                padding: 20px;
                border-radius: 12px;
                margin-bottom: 12px;
                border: 1px solid #E0E0E0;
                border-left: 8px solid {PRIMARY_COLOR};
                box-shadow: 2px 2px 5px rgba(0,0,0,0.07);
            ">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                    <span style="font-size: 1.4em; font-weight: 800; color: #333333;">{ax_name}</span>
                    <span style="font-size: 1.9em; font-weight: 900; line-height: 1;">
                        <span style="color: {PRIMARY_COLOR};">{ax_val}</span>
                        <span style="color:#bbb;font-size:0.5em;font-weight:600;"> /200</span>
                    </span>
                </div>
                <p style="font-size: 1.05em; color: #777777; margin: 0; line-height: 1.3; font-weight: 500;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    # Key metrics
    st.markdown("#### Key Metrics")

    pti = round(d["median_home_price"] / d["median_income"], 1) if d["median_income"] else 0

    mc1, mc2, mc3, mc4 = st.columns(4)
    with mc1:
        st.metric("Median Home Price", f"${d['median_home_price']:,}")
        st.metric("Median Income", f"${d['median_income']:,}")
        st.metric("Price-to-Income Ratio", f"{pti}x")
    with mc2:
        st.metric("Unemployment Rate", f"{d['unemployment']}%")
        st.metric("Population Growth", f"{d['pop_growth']}%")
        st.metric("Disaster Events (5yr)", d["disaster_freq"])
    with mc3:
        st.metric("Rental Yield (Cap Rate)", f"{d['cap_rate']}%")
        st.metric("5yr Appreciation", f"{d['price_appreciation_5yr']}%")
        st.metric("Vacancy Rate", f"{d['vacancy_rate']}%")
    with mc4:
        st.metric("YoY Price Change", f"{d['yoy_price_change']}%")
        st.metric("Months of Inventory", f"{d['months_inventory']}")
        st.metric("Days on Market", f"{d['days_on_market']}")


# ---------------------------------------------------------------------------
# Score History
# ---------------------------------------------------------------------------
history = _load_scores_history()
if history:
    st.markdown("---")
    st.markdown("#### Score History")

    dates = sorted(history.keys())
    if len(dates) >= 1:
        prefix = "State:" if view_mode == "States" else "Metro:"

        # Get history for selected market
        if selected:
            sel_name = selected["name"]
            hist_dates = []
            hist_values = []
            for date in dates:
                day_data = history[date]
                for key, score_val in day_data.items():
                    if key.startswith(prefix):
                        market_name = key[len(prefix):]
                        if view_mode == "States":
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
                    line=dict(color=PRIMARY_COLOR, width=2),
                    marker=dict(size=5),
                    fill='tozeroy',
                    fillcolor='rgba(46, 139, 87, 0.05)',
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


# ---------------------------------------------------------------------------
# Ranking Table
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown("#### Full Rankings")

table_rows = []
for i, r in enumerate(rankings, 1):
    row = {
        "Rank": i,
        "Name": r["name"],
        "Score /1000": r["total"],
    }
    for ax in AXES_LABELS:
        row[f"{ax} /200"] = r["axes"][ax]
    table_rows.append(row)

df_table = pd.DataFrame(table_rows)

st.dataframe(
    df_table,
    use_container_width=True,
    hide_index=True,
    height=450,
)


# ---------------------------------------------------------------------------
# Methodology
# ---------------------------------------------------------------------------
with st.expander("Scoring Methodology"):
    st.markdown("### REALESTATE-1000 Scoring System")
    st.markdown("Each market is scored on 5 axes, each worth 0-200 points, for a maximum total of 1,000.")
    st.markdown("")
    for ax, desc in AXES_DESCRIPTIONS.items():
        st.markdown(f"**{ax}** (0-200): {desc}")
    st.markdown("")
    st.markdown("Data sources: US Census Bureau (ACS 2023), Bureau of Labor Statistics, Redfin, FEMA, Bureau of Economic Analysis.")
    st.markdown("Scores use proportional scaling. Lower risk = higher Risk Profile score (inverse scoring).")
