import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Climate Insights Dashboard",
    layout="wide"
)

st.title("Climate Trends Insights Dashboard")
st.markdown(
"""
Interactive dashboard for exploring climate patterns, trends,
correlations, and anomalies across countries.
"""
)

# -----------------------------
# Placeholder Data Loader
# Replace with real cleaned data later
# -----------------------------
@st.cache_data
def load_data():
    dates = pd.date_range("2015-01-01", "2026-12-31", freq="M")

    countries = ["Ethiopia", "Kenya", "Sudan", "Nigeria", "Tanzania"]

    rows = []

    for country in countries:
        for d in dates:
            rows.append(
                {
                    "Date": d,
                    "Country": country,
                    "Month": d.month,
                    "Year": d.year,
                    "T2M": np.random.normal(24, 3),
                    "PRECTOTCORR": np.random.gamma(2, 20),
                    "RH2M": np.random.normal(65, 8),
                    "WS2M": np.random.normal(3, 1),
                }
            )

    df = pd.DataFrame(rows)
    return df


df = load_data()


# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("Filters")

country = st.sidebar.multiselect(
    "Select Country",
    options=sorted(df["Country"].unique()),
    default=sorted(df["Country"].unique())
)

year_range = st.sidebar.slider(
    "Year Range",
    int(df["Year"].min()),
    int(df["Year"].max()),
    (2015, 2026)
)

variable = st.sidebar.selectbox(
    "Primary Climate Variable",
    ["T2M", "PRECTOTCORR", "RH2M", "WS2M"]
)

filtered = df[
    (df["Country"].isin(country)) &
    (df["Year"].between(year_range[0], year_range[1]))
]


# -----------------------------
# KPI Metrics
# -----------------------------
st.subheader("Key Indicators")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Avg Temperature",
    f"{filtered['T2M'].mean():.2f} °C"
)

c2.metric(
    "Total Precipitation",
    f"{filtered['PRECTOTCORR'].sum():,.0f}"
)

c3.metric(
    "Avg Humidity",
    f"{filtered['RH2M'].mean():.1f}%"
)

c4.metric(
    "Avg Wind Speed",
    f"{filtered['WS2M'].mean():.2f} m/s"
)


# -----------------------------
# Time Series Trend
# -----------------------------
st.subheader("Climate Time Series Trends")

monthly = (
    filtered
    .groupby(["Date","Country"])[variable]
    .mean()
    .reset_index()
)

fig_trend = px.line(
    monthly,
    x="Date",
    y=variable,
    color="Country",
    title=f"{variable} Trend Over Time"
)

st.plotly_chart(fig_trend, use_container_width=True)


# -----------------------------
# Seasonal Analysis
# -----------------------------
st.subheader("Seasonality Analysis")

seasonal = (
    filtered
    .groupby(["Month","Country"])["PRECTOTCORR"]
    .mean()
    .reset_index()
)

fig_season = px.bar(
    seasonal,
    x="Month",
    y="PRECTOTCORR",
    color="Country",
    barmode="group",
    title="Average Monthly Rainfall"
)

st.plotly_chart(fig_season, use_container_width=True)


# -----------------------------
# Correlation Heatmap
# -----------------------------
st.subheader("Correlation Analysis")

corr_cols = [
    "T2M",
    "PRECTOTCORR",
    "RH2M",
    "WS2M"
]

corr = filtered[corr_cols].corr()

fig_corr = go.Figure(
    data=go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.index,
        text=np.round(corr.values,2),
        texttemplate="%{text}",
        hovertemplate=
            "X: %{x}<br>" +
            "Y: %{y}<br>" +
            "Correlation: %{z:.2f}<extra></extra>",
        colorscale="RdBu",
        zmin=-1,
        zmax=1
    )
)

fig_corr.update_layout(
    title="Correlation Matrix of Climate Variables",
    height=600
)

st.plotly_chart(
    fig_corr,
    use_container_width=True
)


# -----------------------------
# Relationship Explorer
# -----------------------------
st.subheader("Relationship Explorer")

colx, coly = st.columns(2)

with colx:
    x_var = st.selectbox(
        "X Variable",
        corr_cols,
        index=0
    )

with coly:
    y_var = st.selectbox(
        "Y Variable",
        corr_cols,
        index=2
    )

fig_scatter = px.scatter(
    filtered,
    x=x_var,
    y=y_var,
    color="Country",
    size="PRECTOTCORR",
    hover_data=["Year"],
    title=f"{x_var} vs {y_var}"
)

st.plotly_chart(fig_scatter, use_container_width=True)


# -----------------------------
# Distribution Analysis
# -----------------------------

st.subheader("Distribution Analysis")

dist_var = st.selectbox(
    "Select Variable Distribution",
    ["T2M","PRECTOTCORR","RH2M","WS2M"]
)
fig = px.histogram(
    filtered,
    x=dist_var,
    color="Country",
    marginal="box",
    histnorm="probability density",
    opacity=0.6,
    nbins=40,
    title=f"{dist_var} Density Distribution"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# -----------------------------
# Extreme Events / Outliers
# -----------------------------
st.subheader("Extreme Climate Events")

threshold = st.slider(
    "Temperature Alert Threshold",
    20,
    40,
    32
)

extremes = filtered[
    filtered["T2M"] > threshold
]

fig_extreme = px.scatter(
    extremes,
    x="Date",
    y="T2M",
    color="Country",
    title="Extreme Heat Events"
)

st.plotly_chart(fig_extreme, use_container_width=True)


# -----------------------------
# Country Comparison
# -----------------------------
st.subheader("Country Comparison")

compare_var = st.selectbox(
    "Compare Variable",
    corr_cols,
    key="compare"
)

compare_df = (
    filtered
    .groupby("Country")[compare_var]
    .mean()
    .reset_index()
)

fig_compare = px.bar(
    compare_df,
    x="Country",
    y=compare_var,
    title=f"Average {compare_var} by Country"
)

st.plotly_chart(fig_compare, use_container_width=True)

# -----------------------------
# Climate Risk Indicators
# -----------------------------
st.subheader("Climate Risk Indicators")

risk_df = filtered.copy()


# ==================================
# Extreme Heat Days
# ==================================

st.subheader("Extreme Heat Days Per Year")

heat_threshold = st.slider(
    "Extreme Heat Threshold (°C)",
    25,
    45,
    35
)

risk_df["Extreme_Heat_Day"] = (
    risk_df["T2M"] > heat_threshold
).astype(int)


# Count extreme heat days per year
heat_yearly = (
    risk_df
    .groupby(["Year","Country"])["Extreme_Heat_Day"]
    .sum()
    .reset_index()
)


# Grouped Bar Chart
fig_heat = px.bar(
    heat_yearly,
    x="Year",
    y="Extreme_Heat_Day",
    color="Country",
    barmode="group",
    text="Extreme_Heat_Day",
    title=f"Extreme Heat Days per Year (T2M > {heat_threshold}°C)"
)

fig_heat.update_traces(
    textposition="outside"
)

fig_heat.update_layout(
    xaxis_title="Year",
    yaxis_title="Number of Extreme Heat Days",
    bargap=0.15,
    bargroupgap=0.05,
    height=650
)

st.plotly_chart(
    fig_heat,
    use_container_width=True
)



# ==========================================
# Longest Consecutive Dry Days Per Year
# Grouped Cross-Country Bar Chart
# ==========================================

st.subheader(
    "Longest Consecutive Dry Days Per Year"
)

dry_threshold = st.slider(
    "Dry Day Threshold (mm rainfall)",
    0.0,
    5.0,
    1.0
)


risk_df["Dry_Day"] = (
    risk_df["PRECTOTCORR"] < dry_threshold
).astype(int)


# ---------------------------------
# Compute consecutive dry streaks
# ---------------------------------
def compute_streak(series):
    streak = 0
    out = []

    for v in series:
        if v == 1:
            streak += 1
        else:
            streak = 0

        out.append(streak)

    return out


risk_df = risk_df.sort_values(
    ["Country","Date"]
)

risk_df["Dry_Streak"] = (
    risk_df
    .groupby("Country")["Dry_Day"]
    .transform(compute_streak)
)


# ---------------------------------
# Longest dry streak per year
# ---------------------------------
dry_yearly = (
    risk_df
    .groupby(["Year","Country"])["Dry_Streak"]
    .max()
    .reset_index()
)


# ---------------------------------
# Grouped Bar Chart
# ---------------------------------
fig_dry = px.bar(
    dry_yearly,
    x="Year",
    y="Dry_Streak",
    color="Country",
    barmode="group",
    text="Dry_Streak",
    title=f"Longest Consecutive Dry Days per Year (PRECTOTCORR < {dry_threshold} mm)"
)

fig_dry.update_traces(
    textposition="outside"
)

fig_dry.update_layout(
    xaxis_title="Year",
    yaxis_title="Days",
    bargap=0.15,
    bargroupgap=0.05,
    height=650,
    legend_title="Country"
)

st.plotly_chart(
    fig_dry,
    use_container_width=True
)
# -----------------------------
# Optional Raw Data Preview
# -----------------------------
with st.expander("View Filtered Data"):
    st.dataframe(filtered)


st.markdown("---")
st.caption(
    "Climate Insights Dashboard | Streamlit Prototype"
)