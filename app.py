# app.py
"""REALESTATE-1000 -- US Real Estate Market Scoring Platform."""
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
st.set_page_config(page_title=APP_TITLE, layout="wide")

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');
.block-container { max-width: 1600px; padding-top: 1rem; font-family: 'Inter', sans-serif; }

.hero-title { font-size: 42px; font-weight: 900; color: #2E8B57; margin-bottom: 0; }
.hero-sub { font-size: 16px; color: #666; margin-top: 4px; margin-bottom: 24px; }

.metric-card {
    background: #ffffff; border-radius: 12px; padding: 16px 20px;
    border: 1px solid #E8E8E8; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    text-align: center;
}
.metric-label { font-size: 12px; color: #888; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; }
.metric-value { font-size: 28px; font-weight: 900; color: #1E293B; }
.metric-name { font-size: 14px; color: #2E8B57; font-weight: 600; margin-top: 2px; }

.score-big { font-size: 72px; font-weight: 900; color: #2E8B57; text-align: center; line-height: 1; }
.score-label { font-size: 14px; color: #888; text-align: center; font-weight: 600; letter-spacing: 2px; }

.axis-card {
    background: #ffffff; border-radius: 10px; padding: 12px 16px;
    border: 1px solid #EDEDED; margin-bottom: 8px;
    display: flex; justify-content: space-between; align-items: center;
}
.axis-label { font-size: 14px; color: #444; font-weight: 600; }
.axis-value { font-size: 22px; font-weight: 900; color: #1A1C1E; }

.section-title {
    font-size: 15px; font-weight: 700; color: #2E8B57;
    text-transform: uppercase; letter-spacing: 1px; margin: 24px 0 12px;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def score_color(score, max_score=1000):
    """Return a hex color from red (low) to green (high)."""
    ratio = score / max_score
    if ratio >= 0.7:
        return "#2E8B57"
    elif ratio >= 0.5:
        return "#DAA520"
    else:
        return "#DC3545"


def affordability_indicator(score_200):
    """Return traffic light emoji and label for affordability."""
    if score_200 >= 140:
        return "🟢", "Affordable"
    elif score_200 >= 80:
        return "🟡", "Moderate"
    else:
        return "🔴", "Expensive"


def render_radar_chart(axes_dict, name, color="#2E8B57"):
    """Render a 5-axis radar chart."""
    labels = list(axes_dict.keys())
    values = list(axes_dict.values())
    values_closed = values + [values[0]]
    labels_closed = labels + [labels[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=labels_closed,
        fill='toself',
        fillcolor=f'rgba(46, 139, 87, 0.15)',
        line_color=color,
        line=dict(width=3),
        name=name,
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 200], gridcolor="#F0F0F0", tickfont=dict(size=10)),
            angularaxis=dict(rotation=90, direction="clockwise", tickfont=dict(size=11)),
            bgcolor='white',
        ),
        showlegend=False,
        margin=dict(l=60, r=60, t=30, b=30),
        height=400,
    )
    return fig


def render_breakdown_bar(axes_dict):
    """Render horizontal bar chart for score breakdown."""
    labels = list(axes_dict.keys())
    values = list(axes_dict.values())
    colors = ['#2E8B57' if v >= 140 else '#DAA520' if v >= 80 else '#DC3545' for v in values]

    fig = go.Figure(go.Bar(
        x=values,
        y=labels,
        orientation='h',
        marker_color=colors,
        text=[f"{v}/200" for v in values],
        textposition='auto',
        textfont=dict(size=13, color='white'),
    ))
    fig.update_layout(
        xaxis=dict(range=[0, 200], title="Score", gridcolor="#F0F0F0"),
        yaxis=dict(autorange="reversed"),
        margin=dict(l=10, r=20, t=10, b=40),
        height=250,
        plot_bgcolor='white',
    )
    return fig


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
@st.cache_data(ttl=3600)
def cached_state_rankings():
    return get_state_rankings()

@st.cache_data(ttl=3600)
def cached_metro_rankings():
    return get_metro_rankings()


# ---------------------------------------------------------------------------
# Main app
# ---------------------------------------------------------------------------
st.markdown('<div class="hero-title">REALESTATE-1000</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">US Real Estate Market Scoring. 50 States + DC and Top 30 Metro Areas scored on a 0-1000 scale across 5 axes.</div>', unsafe_allow_html=True)

# View toggle
view_mode = st.radio("View", ["States", "Metro Areas"], horizontal=True, label_visibility="collapsed")

if view_mode == "States":
    rankings = cached_state_rankings()
else:
    rankings = cached_metro_rankings()

if not rankings:
    st.error("No data available.")
    st.stop()

# ---------------------------------------------------------------------------
# Summary metrics
# ---------------------------------------------------------------------------
scores = [r["total"] for r in rankings]
best = max(rankings, key=lambda x: x["total"])
worst = min(rankings, key=lambda x: x["total"])
avg_score = int(round(sum(scores) / len(scores)))

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Highest Score</div>
        <div class="metric-value">{best['total']}</div>
        <div class="metric-name">{best['name']}</div>
    </div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">National Average</div>
        <div class="metric-value">{avg_score}</div>
        <div class="metric-name">{len(rankings)} markets scored</div>
    </div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Lowest Score</div>
        <div class="metric-value">{worst['total']}</div>
        <div class="metric-name">{worst['name']}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("")

# ---------------------------------------------------------------------------
# Map
# ---------------------------------------------------------------------------
if view_mode == "States":
    # Choropleth map of US states
    df_map = pd.DataFrame([
        {"abbr": r["abbr"], "name": r["name"], "score": r["total"],
         "Affordability": r["axes"]["Affordability"],
         "Momentum": r["axes"]["Market Momentum"],
         "Economy": r["axes"]["Economic Foundation"],
         "Risk": r["axes"]["Risk Profile"],
         "Investment": r["axes"]["Investment Return"]}
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
            [0, "#DC3545"],
            [0.35, "#FF8C00"],
            [0.5, "#DAA520"],
            [0.65, "#90EE90"],
            [1, "#2E8B57"],
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
    # Bubble map of metro areas
    df_metro = pd.DataFrame([
        {"name": r["name"], "lat": r["lat"], "lng": r["lng"],
         "score": r["total"], "state": r["state"],
         "Affordability": r["axes"]["Affordability"],
         "Momentum": r["axes"]["Market Momentum"],
         "Economy": r["axes"]["Economic Foundation"],
         "Risk": r["axes"]["Risk Profile"],
         "Investment": r["axes"]["Investment Return"]}
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
            [0, "#DC3545"],
            [0.35, "#FF8C00"],
            [0.5, "#DAA520"],
            [0.65, "#90EE90"],
            [1, "#2E8B57"],
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
# Ranking table
# ---------------------------------------------------------------------------
st.markdown('<div class="section-title">Full Rankings</div>', unsafe_allow_html=True)

table_rows = []
for i, r in enumerate(rankings, 1):
    row = {
        "Rank": i,
        "Name": r["name"],
        "Total (/1000)": r["total"],
    }
    for ax in AXES_LABELS:
        row[f"{ax} (/200)"] = r["axes"][ax]
    table_rows.append(row)

df_table = pd.DataFrame(table_rows)
st.dataframe(df_table, use_container_width=True, hide_index=True, height=450)


# ---------------------------------------------------------------------------
# Top 10 / Bottom 10
# ---------------------------------------------------------------------------
col_top, col_bot = st.columns(2)
with col_top:
    st.markdown('<div class="section-title">Top 10</div>', unsafe_allow_html=True)
    for i, r in enumerate(rankings[:10], 1):
        c = score_color(r["total"])
        st.markdown(
            f'<div class="axis-card"><span class="axis-label">{i}. {r["name"]}</span>'
            f'<span class="axis-value" style="color:{c}">{r["total"]}</span></div>',
            unsafe_allow_html=True,
        )

with col_bot:
    st.markdown('<div class="section-title">Bottom 10</div>', unsafe_allow_html=True)
    bottom = rankings[-10:]
    bottom_rev = list(reversed(bottom))
    for i, r in enumerate(bottom_rev, len(rankings) - 9):
        c = score_color(r["total"])
        st.markdown(
            f'<div class="axis-card"><span class="axis-label">{i}. {r["name"]}</span>'
            f'<span class="axis-value" style="color:{c}">{r["total"]}</span></div>',
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
# Detail view
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown('<div class="section-title">Market Detail</div>', unsafe_allow_html=True)

name_list = [r["name"] for r in rankings]
selected_name = st.selectbox("Select a market to view details", name_list)
selected = next((r for r in rankings if r["name"] == selected_name), None)

if selected:
    d = selected["data"]
    total = selected["total"]
    axes = selected["axes"]

    # Header
    col_score, col_radar = st.columns([1, 2])
    with col_score:
        st.markdown(f'<div class="score-label">TOTAL SCORE</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="score-big" style="color:{score_color(total)}">{total}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="score-label">/1000</div>', unsafe_allow_html=True)

        st.markdown("")
        # Axis breakdown
        for ax_name, ax_val in axes.items():
            c = score_color(ax_val, 200)
            st.markdown(
                f'<div class="axis-card"><span class="axis-label">{ax_name}</span>'
                f'<span class="axis-value" style="color:{c}">{ax_val}/200</span></div>',
                unsafe_allow_html=True,
            )

    with col_radar:
        st.plotly_chart(render_radar_chart(axes, selected["name"]), use_container_width=True)

    # Breakdown bar chart
    st.markdown('<div class="section-title">Score Breakdown</div>', unsafe_allow_html=True)
    st.plotly_chart(render_breakdown_bar(axes), use_container_width=True)

    # Key metrics
    st.markdown('<div class="section-title">Key Metrics</div>', unsafe_allow_html=True)

    mc1, mc2, mc3, mc4 = st.columns(4)
    with mc1:
        st.metric("Median Home Price", f"${d['median_home_price']:,}")
        st.metric("Median Income", f"${d['median_income']:,}")
        pti = round(d['median_home_price'] / d['median_income'], 1)
        st.metric("Price-to-Income Ratio", f"{pti}x")
    with mc2:
        st.metric("YoY Price Change", f"{d['yoy_price_change']}%")
        st.metric("Months of Inventory", f"{d['months_inventory']}")
        st.metric("Days on Market", f"{d['days_on_market']}")
    with mc3:
        st.metric("Unemployment Rate", f"{d['unemployment']}%")
        st.metric("Job Growth", f"{d['job_growth']}%")
        st.metric("Population Growth", f"{d['pop_growth']}%")
    with mc4:
        st.metric("Cap Rate", f"{d['cap_rate']}%")
        st.metric("5yr Appreciation", f"{d['price_appreciation_5yr']}%")
        st.metric("Vacancy Rate", f"{d['vacancy_rate']}%")

    # Affordability indicator
    st.markdown('<div class="section-title">Affordability Assessment</div>', unsafe_allow_html=True)
    indicator, label = affordability_indicator(axes["Affordability"])
    monthly_rate = d["mortgage_rate"] / 100 / 12
    principal = d["median_home_price"] * 0.8
    n = 360
    if monthly_rate > 0:
        payment = principal * monthly_rate * (1 + monthly_rate)**n / ((1 + monthly_rate)**n - 1)
    else:
        payment = principal / n
    rent_pct = round(d["rent_median"] * 12 / d["median_income"] * 100, 1)

    ac1, ac2, ac3 = st.columns(3)
    with ac1:
        st.markdown(f"### {indicator} {label}")
        st.caption(f"Affordability score: {axes['Affordability']}/200")
    with ac2:
        st.metric("Est. Monthly Mortgage (20% down)", f"${int(payment):,}")
        st.caption(f"At {d['mortgage_rate']}% rate, 30yr fixed")
    with ac3:
        st.metric("Rent as % of Income", f"{rent_pct}%")
        st.caption(f"Median rent: ${d['rent_median']:,}/mo")

    # Risk summary
    st.markdown('<div class="section-title">Risk Summary</div>', unsafe_allow_html=True)
    rc1, rc2, rc3, rc4 = st.columns(4)
    with rc1:
        st.metric("Disaster Events (5yr)", d["disaster_freq"])
    with rc2:
        st.metric("Flood Zone Coverage", f"{d['flood_zone_pct']}%")
    with rc3:
        ins_label = "Above Avg" if d["insurance_index"] > 110 else "Below Avg" if d["insurance_index"] < 90 else "Average"
        st.metric("Insurance Cost", f"{d['insurance_index']} ({ins_label})")
    with rc4:
        st.metric("Foreclosure Rate", f"{d['foreclosure_rate']}%")


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
    st.markdown("Data sources: Zillow, US Census Bureau (ACS), Bureau of Labor Statistics, FEMA, Bureau of Economic Analysis.")
    st.markdown("Scores are based on realistic 2025 approximations. Lower risk = higher Risk Profile score (inverse scoring).")
