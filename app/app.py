import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="UAC Care Pipeline Analytics",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

/* ── Background ── */
.stApp {
    background-color: #0d1117;
    color: #e6edf3;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #161b22;
    border-right: 1px solid #30363d;
}
[data-testid="stSidebar"] * {
    color: #e6edf3 !important;
}

/* ── KPI Cards ── */
.kpi-card {
    background: linear-gradient(135deg, #1c2128 0%, #21262d 100%);
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 8px;
    transition: border-color 0.2s;
}
.kpi-card:hover { border-color: #58a6ff; }
.kpi-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #8b949e;
    margin-bottom: 6px;
}
.kpi-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 28px;
    font-weight: 600;
    color: #e6edf3;
    line-height: 1;
}
.kpi-delta {
    font-size: 12px;
    margin-top: 6px;
    color: #3fb950;
}
.kpi-delta.bad { color: #f85149; }
.kpi-delta.warn { color: #d29922; }

/* ── Section headers ── */
.section-header {
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #58a6ff;
    border-bottom: 1px solid #21262d;
    padding-bottom: 8px;
    margin: 28px 0 16px 0;
}

/* ── Alert boxes ── */
.alert-red {
    background: rgba(248,81,73,0.08);
    border: 1px solid rgba(248,81,73,0.4);
    border-left: 4px solid #f85149;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 12px;
    font-size: 14px;
    color: #ffa198;
}
.alert-yellow {
    background: rgba(210,153,34,0.08);
    border: 1px solid rgba(210,153,34,0.4);
    border-left: 4px solid #d29922;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 12px;
    font-size: 14px;
    color: #e3b341;
}
.alert-green {
    background: rgba(63,185,80,0.08);
    border: 1px solid rgba(63,185,80,0.4);
    border-left: 4px solid #3fb950;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 12px;
    font-size: 14px;
    color: #56d364;
}

/* ── Plotly chart backgrounds ── */
.js-plotly-plot, .plot-container { background: transparent !important; }

/* ── Hide default streamlit menu ── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

/* ── Divider ── */
hr { border-color: #21262d; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PLOTLY THEME DEFAULTS
# ─────────────────────────────────────────────
CHART_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="IBM Plex Sans", color="#8b949e", size=12),
    xaxis=dict(gridcolor="#21262d", linecolor="#30363d", zerolinecolor="#21262d"),
    yaxis=dict(gridcolor="#21262d", linecolor="#30363d", zerolinecolor="#21262d"),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#30363d"),
    margin=dict(l=40, r=20, t=40, b=40),
)
COLOR_BLUE   = "#58a6ff"
COLOR_ORANGE = "#f0883e"
COLOR_GREEN  = "#3fb950"
COLOR_RED    = "#f85149"
COLOR_PURPLE = "#bc8cff"
COLOR_TEAL   = "#39d353"

# ─────────────────────────────────────────────
# DATA LOADER
# ─────────────────────────────────────────────
@st.cache_data
def load_data(uploaded_file=None):
    """Load and clean the UAC dataset."""
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, parse_dates=["Date"])
    else:
        return None

    df = df.drop_duplicates().dropna()
    df = df.sort_values("Date").reset_index(drop=True)

    # Fix HHS Care comma-separated values
    df["Children in HHS Care"] = df["Children in HHS Care"].astype(str).str.replace(",", "").astype(float)

    # Rename
    df = df.rename(columns={
        "Children apprehended and placed in CBP custody*": "cbp_apprehended",
        "Children in CBP custody": "cbp_custody",
        "Children transferred out of CBP custody": "cbp_transferred",
        "Children in HHS Care": "hhs_care",
        "Children discharged from HHS Care": "hhs_discharged",
    })

    # Force all numeric columns to float64 (fixes Arrow dtype issues on Streamlit Cloud)
    for col in ["cbp_apprehended", "cbp_custody", "cbp_transferred", "hhs_care", "hhs_discharged"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("float64")

    # KPIs
    df["transfer_efficiency_ratio"] = np.where(df["cbp_custody"] != 0, df["cbp_transferred"] / df["cbp_custody"], np.nan)
    df["discharge_effectiveness"]   = np.where(df["hhs_care"] != 0, df["hhs_discharged"] / df["hhs_care"], np.nan)
    df["daily_throughput_rate"]      = np.where(
        df["cbp_apprehended"] != 0,
        df["hhs_discharged"] / df["cbp_apprehended"], np.nan
    )
    df["backlog"]                    = df["cbp_apprehended"] - df["hhs_discharged"]
    df["cumulative_backlog"]         = df["backlog"].cumsum()
    df["rolling_discharge"]          = df["discharge_effectiveness"].rolling(7).mean()
    df["outcome_stability_score"]    = df["discharge_effectiveness"].rolling(7).std()
    df["discharge_change"]           = df["discharge_effectiveness"].diff()

    # Temporal
    df["weekday"]  = df["Date"].dt.day_name()
    df["is_weekend"] = df["weekday"].isin(["Saturday", "Sunday"])
    df["day_type"] = df["is_weekend"].map({True: "Weekend", False: "Weekday"})
    df["month"]    = df["Date"].dt.to_period("M")
    df["year"]     = df["Date"].dt.year

    # Stagnation flag
    threshold = df["rolling_discharge"].quantile(0.25)
    df["stagnation_period"] = df["rolling_discharge"] < threshold

    return df

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏛️ UAC Analytics")
    st.markdown("**Care Pipeline Dashboard**")
    st.markdown("---")

    st.markdown("### 📂 Data Source")
    uploaded = st.file_uploader(
        "Upload CSV Dataset",
        type=["csv"],
        help="Upload HHS_Unaccompanied_Alien_Children_Program.csv"
    )

    st.markdown("---")
    st.markdown("### 🗓️ Date Range")

df = load_data(uploaded)

if df is None:
    st.markdown("""
    <div style='text-align:center; padding: 80px 40px;'>
        <div style='font-size:48px; margin-bottom:20px;'>🏛️</div>
        <h2 style='color:#e6edf3; margin-bottom:12px;'>UAC Care Pipeline Analytics</h2>
        <p style='color:#8b949e; font-size:15px; max-width:480px; margin:0 auto 24px;'>
            Upload the <code>HHS_Unaccompanied_Alien_Children_Program.csv</code>
            file from the sidebar to begin analysis.
        </p>
        <div style='background:#161b22; border:1px solid #30363d; border-radius:8px;
                    padding:20px; display:inline-block; text-align:left; font-size:13px; color:#8b949e;'>
            <div style='margin-bottom:8px;'><span style='color:#58a6ff;'>→</span> Transfer Efficiency Ratio</div>
            <div style='margin-bottom:8px;'><span style='color:#58a6ff;'>→</span> Discharge Effectiveness Index</div>
            <div style='margin-bottom:8px;'><span style='color:#58a6ff;'>→</span> Pipeline Throughput Rate</div>
            <div style='margin-bottom:8px;'><span style='color:#58a6ff;'>→</span> Backlog Accumulation Analysis</div>
            <div><span style='color:#58a6ff;'>→</span> Outcome Stability Score</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Date filter ──
with st.sidebar:
    min_date = df["Date"].min().date()
    max_date = df["Date"].max().date()
    date_range = st.date_input(
        "Select range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    if len(date_range) == 2:
        start, end = date_range
        df_f = df[(df["Date"].dt.date >= start) & (df["Date"].dt.date <= end)].copy()
    else:
        df_f = df.copy()

    st.markdown("---")
    st.markdown("### ⚙️ Alert Thresholds")
    discharge_alert = st.slider(
        "Discharge Alert Threshold",
        min_value=0.005, max_value=0.10,
        value=0.015, step=0.005,
        format="%.3f",
        help="Trigger alert when discharge effectiveness falls below this"
    )
    transfer_alert = st.slider(
        "Transfer Alert Threshold",
        min_value=0.30, max_value=0.90,
        value=0.50, step=0.05,
        format="%.2f"
    )

    st.markdown("---")
    st.markdown("### 📌 Navigation")
    page = st.radio(
        "Go to",
        ["📊 Overview", "🔄 Pipeline Flow", "📉 KPI Trends",
         "🚨 Bottleneck", "📅 Temporal", "⚖️ Stability"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.caption("U.S. HHS — Unified Mentor Program")

# ─────────────────────────────────────────────
# COMPUTE SUMMARY STATS
# ─────────────────────────────────────────────
avg_transfer    = df_f["transfer_efficiency_ratio"].mean()
avg_discharge   = df_f["discharge_effectiveness"].mean()
avg_throughput  = df_f["daily_throughput_rate"].mean()
avg_backlog     = df_f["backlog"].mean()
avg_stability   = df_f["outcome_stability_score"].mean()
total_apprehend = int(df_f["cbp_apprehended"].sum())
total_discharge = int(df_f["hhs_discharged"].sum())
stagnation_pct  = df_f["stagnation_period"].mean() * 100

# ─────────────────────────────────────────────
# HELPER: KPI CARD
# ─────────────────────────────────────────────
def kpi_card(label, value, note="", note_class=""):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {"<div class='kpi-delta " + note_class + "'>" + note + "</div>" if note else ""}
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PAGES
# ─────────────────────────────────────────────

# ══════════════════════════════════════════════
# PAGE 1: OVERVIEW
# ══════════════════════════════════════════════
if page == "📊 Overview":
    st.markdown("## 📊 Executive Overview")
    st.markdown(f"<div style='color:#8b949e;font-size:13px;margin-top:-8px;margin-bottom:24px;'>Period: {df_f['Date'].min().strftime('%b %d, %Y')} — {df_f['Date'].max().strftime('%b %d, %Y')}</div>", unsafe_allow_html=True)

    # ── Alerts ──
    if avg_discharge < discharge_alert:
        st.markdown(f"<div class='alert-red'>🚨 <strong>Critical:</strong> Discharge effectiveness ({avg_discharge:.1%}) is below threshold ({discharge_alert:.1%}). Sponsor placement pipeline requires immediate intervention.</div>", unsafe_allow_html=True)
    if avg_transfer < transfer_alert:
        st.markdown(f"<div class='alert-yellow'>⚠️ <strong>Warning:</strong> Transfer efficiency ({avg_transfer:.1%}) is below threshold ({transfer_alert:.1%}). CBP → HHS movement is slowing.</div>", unsafe_allow_html=True)
    if avg_discharge >= discharge_alert and avg_transfer >= transfer_alert:
        st.markdown("<div class='alert-green'>✅ All monitored KPIs are within acceptable thresholds for the selected period.</div>", unsafe_allow_html=True)

    # ── KPI Row ──
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        kpi_card("Transfer Efficiency", f"{avg_transfer:.1%}",
                 "CBP → HHS movement", "warn" if avg_transfer < transfer_alert else "")
    with c2:
        kpi_card("Discharge Effectiveness", f"{avg_discharge:.2%}",
                 "⚠ Primary bottleneck", "bad")
    with c3:
        kpi_card("Pipeline Throughput", f"{avg_throughput:.3f}",
                 "Exits per entry")
    with c4:
        kpi_card("Avg Daily Backlog", f"{avg_backlog:+.0f}",
                 "Apprehensions − Discharges", "bad" if avg_backlog > 0 else "")
    with c5:
        kpi_card("Stagnation Days", f"{stagnation_pct:.1f}%",
                 "Of period below P25", "bad" if stagnation_pct > 50 else "warn")

    st.markdown("---")

    # ── Two charts ──
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='section-header'>Care Load Over Time</div>", unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_f["Date"], y=df_f["cbp_custody"],
                                  name="CBP Custody", line=dict(color=COLOR_ORANGE, width=2)))
        fig.add_trace(go.Scatter(x=df_f["Date"], y=df_f["hhs_care"],
                                  name="HHS Care", line=dict(color=COLOR_BLUE, width=2)))
        fig.update_layout(**CHART_THEME, height=300,
                          title=dict(text="Active Care Load", font=dict(color="#e6edf3", size=14)))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<div class='section-header'>Inflow vs Outflow</div>", unsafe_allow_html=True)
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df_f["Date"], y=df_f["cbp_apprehended"],
                                   name="Inflow (Apprehended)", line=dict(color=COLOR_RED, width=1.5)))
        fig2.add_trace(go.Scatter(x=df_f["Date"], y=df_f["hhs_discharged"],
                                   name="Outflow (Discharged)", line=dict(color=COLOR_GREEN, width=1.5)))
        fig2.update_layout(**CHART_THEME, height=300,
                           title=dict(text="Daily Inflow vs Outflow", font=dict(color="#e6edf3", size=14)))
        st.plotly_chart(fig2, use_container_width=True)

    # ── Summary table ──
    st.markdown("<div class='section-header'>KPI Summary Table</div>", unsafe_allow_html=True)
    summary_df = pd.DataFrame({
        "KPI": ["Transfer Efficiency Ratio", "Discharge Effectiveness",
                "Avg Daily Throughput Rate", "Avg Daily Backlog", "Outcome Stability Score"],
        "Formula": ["Transfers ÷ CBP Custody", "Discharges ÷ HHS Care",
                    "Discharges ÷ Apprehensions", "Apprehensions − Discharges",
                    "7-day Rolling Std Dev"],
        "Value": [f"{avg_transfer:.4f}", f"{avg_discharge:.4f}",
                  f"{avg_throughput:.4f}", f"{avg_backlog:.2f}", f"{avg_stability:.4f}"],
        "Status": [
            "⚠️ Moderate" if avg_transfer < 0.7 else "✅ Good",
            "🚨 Critical",
            "⚠️ Variable",
            "✅ Negative (improving)" if avg_backlog < 0 else "🚨 Positive (accumulating)",
            "⚠️ High Volatility",
        ]
    })
    st.dataframe(summary_df, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════
# PAGE 2: PIPELINE FLOW
# ══════════════════════════════════════════════
elif page == "🔄 Pipeline Flow":
    st.markdown("## 🔄 Care Pipeline Flow Visualization")

    # ── Sankey ──
    st.markdown("<div class='section-header'>Pipeline Stage Flow (Aggregate)</div>", unsafe_allow_html=True)

    total_cbp_in      = int(df_f["cbp_apprehended"].sum())
    total_transferred = int(df_f["cbp_transferred"].sum())
    total_cbp_held    = int(df_f["cbp_custody"].sum())
    total_hhs_in      = total_transferred
    total_discharged  = int(df_f["hhs_discharged"].sum())
    total_hhs_held    = total_hhs_in - total_discharged

    fig_sankey = go.Figure(go.Sankey(
        node=dict(
            pad=20, thickness=24,
            label=["Apprehension", "CBP Custody", "CBP Released", "HHS Care",
                   "Sponsor Placement", "HHS Backlog"],
            color=[COLOR_ORANGE, COLOR_ORANGE, "#30363d",
                   COLOR_BLUE, COLOR_GREEN, COLOR_RED],
            line=dict(color="#30363d", width=0.5),
        ),
        link=dict(
            source=[0, 1, 1, 3, 3],
            target=[1, 2, 3, 4, 5],
            value=[total_cbp_in,
                   max(1, total_cbp_held - total_transferred),
                   total_transferred,
                   total_discharged,
                   max(1, total_hhs_in - total_discharged)],
            color=["rgba(240,136,62,0.35)", "rgba(48,54,61,0.5)",
                   "rgba(88,166,255,0.35)", "rgba(63,185,80,0.35)",
                   "rgba(248,81,73,0.35)"],
        )
    ))
    fig_sankey.update_layout(
        **CHART_THEME, height=420,
        title=dict(text="Aggregate Flow Through UAC Care Pipeline",
                   font=dict(color="#e6edf3", size=15))
    )
    st.plotly_chart(fig_sankey, use_container_width=True)

    # ── Pipeline stage metrics ──
    st.markdown("<div class='section-header'>Stage-Level Totals</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Total Apprehended", f"{total_cbp_in:,}", "CBP intake")
    with c2:
        kpi_card("CBP → HHS Transfers", f"{total_transferred:,}", "Stage 1 exits")
    with c3:
        kpi_card("Sponsor Placements", f"{total_discharged:,}", "Final exits")
    with c4:
        overall_rate = total_discharged / total_cbp_in if total_cbp_in > 0 else 0
        kpi_card("End-to-End Rate", f"{overall_rate:.2%}", "Apprehension → Sponsor")

    # ── Cumulative backlog ──
    st.markdown("<div class='section-header'>Cumulative Backlog</div>", unsafe_allow_html=True)
    fig_bl = go.Figure()
    fig_bl.add_trace(go.Scatter(
        x=df_f["Date"], y=df_f["cumulative_backlog"],
        fill="tozeroy",
        fillcolor="rgba(248,81,73,0.12)",
        line=dict(color=COLOR_RED, width=2),
        name="Cumulative Backlog"
    ))
    fig_bl.update_layout(**CHART_THEME, height=320,
                         title=dict(text="Cumulative Backlog Over Time",
                                    font=dict(color="#e6edf3", size=14)))
    st.plotly_chart(fig_bl, use_container_width=True)


# ══════════════════════════════════════════════
# PAGE 3: KPI TRENDS
# ══════════════════════════════════════════════
elif page == "📉 KPI Trends":
    st.markdown("## 📉 KPI Trend Analysis")

    kpi_choice = st.selectbox(
        "Select KPI",
        ["Transfer Efficiency Ratio", "Discharge Effectiveness",
         "Pipeline Throughput Rate", "Daily Backlog", "Outcome Stability Score"],
    )

    kpi_map = {
        "Transfer Efficiency Ratio":  ("transfer_efficiency_ratio", COLOR_BLUE,   "Ratio"),
        "Discharge Effectiveness":    ("discharge_effectiveness",   COLOR_ORANGE, "Ratio"),
        "Pipeline Throughput Rate":   ("daily_throughput_rate",     COLOR_GREEN,  "Rate"),
        "Daily Backlog":              ("backlog",                   COLOR_RED,    "Count"),
        "Outcome Stability Score":    ("outcome_stability_score",   COLOR_PURPLE, "Std Dev"),
    }

    col_name, color, unit = kpi_map[kpi_choice]

    # Threshold line for discharge / transfer
    alert_val = None
    if kpi_choice == "Discharge Effectiveness":
        alert_val = discharge_alert
    elif kpi_choice == "Transfer Efficiency Ratio":
        alert_val = transfer_alert

    fig_kpi = go.Figure()
    fig_kpi.add_trace(go.Scatter(
        x=df_f["Date"], y=df_f[col_name],
        line=dict(color=color, width=1.5),
        name=kpi_choice, opacity=0.85
    ))
    # 30-day rolling avg overlay
    rolling = df_f[col_name].rolling(30).mean()
    fig_kpi.add_trace(go.Scatter(
        x=df_f["Date"], y=rolling,
        line=dict(color="#ffffff", width=2, dash="dot"),
        name="30-day avg", opacity=0.6
    ))
    if alert_val is not None:
        fig_kpi.add_hline(
            y=alert_val, line_dash="dash",
            line_color=COLOR_RED, opacity=0.7,
            annotation_text=f"Alert: {alert_val:.3f}",
            annotation_font_color=COLOR_RED
        )
    fig_kpi.update_layout(
        **CHART_THEME, height=420,
        title=dict(text=kpi_choice, font=dict(color="#e6edf3", size=15)),
        yaxis_title=unit,
    )
    st.plotly_chart(fig_kpi, use_container_width=True)

    # Stats
    series = df_f[col_name].dropna()
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("Mean",   f"{series.mean():.4f}")
    with c2: kpi_card("Median", f"{series.median():.4f}")
    with c3: kpi_card("Std Dev", f"{series.std():.4f}")
    with c4: kpi_card("Latest", f"{series.iloc[-1]:.4f}")

    # Monthly bar
    st.markdown("<div class='section-header'>Monthly Average</div>", unsafe_allow_html=True)
    monthly = df_f.groupby("month")[col_name].mean().reset_index()
    monthly["month_str"] = monthly["month"].astype(str)
    fig_m = px.bar(monthly, x="month_str", y=col_name,
                   color_discrete_sequence=[color])
    fig_m.update_layout(**CHART_THEME, height=300,
                        xaxis_title="Month", yaxis_title=unit,
                        title=dict(text=f"Monthly {kpi_choice}",
                                   font=dict(color="#e6edf3", size=14)))
    fig_m.update_xaxes(tickangle=45)
    st.plotly_chart(fig_m, use_container_width=True)


# ══════════════════════════════════════════════
# PAGE 4: BOTTLENECK
# ══════════════════════════════════════════════
elif page == "🚨 Bottleneck":
    st.markdown("## 🚨 Bottleneck Detection")

    # ── Transfer vs Discharge comparison ──
    st.markdown("<div class='section-header'>Transfer Efficiency vs Discharge Effectiveness</div>", unsafe_allow_html=True)

    fig_b = go.Figure()
    fig_b.add_trace(go.Scatter(
        x=df_f["Date"], y=df_f["transfer_efficiency_ratio"],
        line=dict(color=COLOR_BLUE, width=1.8),
        name="Transfer Efficiency (~69%)", fill="tozeroy",
        fillcolor="rgba(88,166,255,0.07)"
    ))
    fig_b.add_trace(go.Scatter(
        x=df_f["Date"], y=df_f["discharge_effectiveness"],
        line=dict(color=COLOR_RED, width=1.8),
        name="Discharge Effectiveness (~2%)", fill="tozeroy",
        fillcolor="rgba(248,81,73,0.07)"
    ))
    fig_b.update_layout(
        **CHART_THEME, height=380,
        title=dict(text="The Gap — Why the Pipeline Stalls",
                   font=dict(color="#e6edf3", size=15))
    )
    st.plotly_chart(fig_b, use_container_width=True)

    # ── Bar comparison ──
    col1, col2 = st.columns([2, 1])
    with col1:
        fig_bar = go.Figure(go.Bar(
            x=["Transfer Efficiency\n(CBP → HHS)", "Discharge Effectiveness\n(HHS → Sponsor)"],
            y=[avg_transfer, avg_discharge],
            marker_color=[COLOR_BLUE, COLOR_RED],
            text=[f"{avg_transfer:.1%}", f"{avg_discharge:.2%}"],
            textposition="outside",
            textfont=dict(color="#e6edf3", size=14)
        ))
        fig_bar.update_layout(
            **CHART_THEME, height=350,
            title=dict(text="Efficiency Gap at a Glance",
                       font=dict(color="#e6edf3", size=14)),
            yaxis=dict(tickformat=".0%", **CHART_THEME["yaxis"])
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        gap = avg_transfer - avg_discharge
        kpi_card("Efficiency Gap", f"{gap:.1%}", "Transfer − Discharge", "bad")
        kpi_card("Bottleneck Stage", "HHS Discharge", "Sponsor placement delay", "bad")
        kpi_card("Transfer Efficiency", f"{avg_transfer:.1%}", "Moderate performance", "warn")
        kpi_card("Discharge Effectiveness", f"{avg_discharge:.2%}", "Critical bottleneck", "bad")

    # ── Interpretation ──
    st.markdown("""
    <div style='background:#161b22;border:1px solid #30363d;border-radius:10px;padding:20px 24px;margin-top:12px;'>
        <div style='font-size:13px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;
                    color:#f85149;margin-bottom:12px;'>🔎 Bottleneck Analysis</div>
        <p style='color:#8b949e;font-size:14px;line-height:1.7;margin:0;'>
        While the system transfers children from CBP to HHS at a <strong style='color:#58a6ff;'>~69% efficiency rate</strong>,
        the discharge stage operates at only <strong style='color:#f85149;'>~2% effectiveness</strong> —
        a <strong style='color:#e6edf3;'>35× gap</strong>. Children enter HHS care at a reasonable pace
        but are not exiting to sponsors efficiently, pointing to systemic issues in
        <em>sponsor vetting delays</em>, <em>case management capacity</em>, and
        <em>policy/legal barriers</em> at the final placement stage.
        </p>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
# PAGE 5: TEMPORAL
# ══════════════════════════════════════════════
elif page == "📅 Temporal":
    st.markdown("## 📅 Temporal & Pattern Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='section-header'>Weekday vs Weekend Throughput</div>", unsafe_allow_html=True)
        week_data = df_f.groupby("day_type")["daily_throughput_rate"].mean().reset_index()
        fig_w = px.bar(week_data, x="day_type", y="daily_throughput_rate",
                       color="day_type",
                       color_discrete_map={"Weekday": COLOR_BLUE, "Weekend": COLOR_GREEN},
                       text=week_data["daily_throughput_rate"].apply(lambda x: f"{x:.4f}"))
        fig_w.update_layout(**CHART_THEME, height=320, showlegend=False,
                            title=dict(text="Avg Throughput Rate by Day Type",
                                       font=dict(color="#e6edf3", size=14)))
        fig_w.update_traces(textposition="outside", textfont_color="#e6edf3")
        st.plotly_chart(fig_w, use_container_width=True)

    with col2:
        st.markdown("<div class='section-header'>Throughput by Day of Week</div>", unsafe_allow_html=True)
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        dow = df_f.groupby("weekday")["daily_throughput_rate"].mean().reindex(day_order).reset_index()
        fig_dow = px.bar(dow, x="weekday", y="daily_throughput_rate",
                         color_discrete_sequence=[COLOR_PURPLE])
        fig_dow.update_layout(**CHART_THEME, height=320,
                              title=dict(text="By Day of Week",
                                         font=dict(color="#e6edf3", size=14)))
        st.plotly_chart(fig_dow, use_container_width=True)

    # Monthly discharge trend
    st.markdown("<div class='section-header'>Monthly Discharge Effectiveness Trend</div>", unsafe_allow_html=True)
    monthly_de = df_f.groupby("month")["discharge_effectiveness"].mean().reset_index()
    monthly_de["month_str"] = monthly_de["month"].astype(str)

    fig_mde = go.Figure()
    fig_mde.add_trace(go.Scatter(
        x=monthly_de["month_str"], y=monthly_de["discharge_effectiveness"],
        mode="lines+markers",
        line=dict(color=COLOR_ORANGE, width=2),
        marker=dict(size=6, color=COLOR_ORANGE),
        fill="tozeroy", fillcolor="rgba(240,136,62,0.08)",
        name="Discharge Effectiveness"
    ))
    fig_mde.update_layout(
        **CHART_THEME, height=340,
        title=dict(text="Month-over-Month Discharge Effectiveness",
                   font=dict(color="#e6edf3", size=14)),
        xaxis=dict(tickangle=45, **CHART_THEME["xaxis"])
    )
    st.plotly_chart(fig_mde, use_container_width=True)

    # Yearly heatmap
    if df_f["year"].nunique() > 1:
        st.markdown("<div class='section-header'>Annual Comparison</div>", unsafe_allow_html=True)
        yearly = df_f.groupby("year")[
            ["transfer_efficiency_ratio", "discharge_effectiveness", "daily_throughput_rate"]
        ].mean().round(4).reset_index()
        yearly.columns = ["Year", "Transfer Efficiency", "Discharge Effectiveness", "Throughput Rate"]
        fig_yr = go.Figure(data=go.Heatmap(
            z=yearly[["Transfer Efficiency", "Discharge Effectiveness", "Throughput Rate"]].values.T,
            x=yearly["Year"].astype(str),
            y=["Transfer Efficiency", "Discharge Effectiveness", "Throughput Rate"],
            colorscale=[[0, "#f85149"], [0.5, "#d29922"], [1, "#3fb950"]],
            text=yearly[["Transfer Efficiency", "Discharge Effectiveness", "Throughput Rate"]].values.T,
            texttemplate="%{text:.4f}",
            textfont_color="white",
        ))
        fig_yr.update_layout(**CHART_THEME, height=250,
                             title=dict(text="KPI Heatmap by Year",
                                        font=dict(color="#e6edf3", size=14)))
        st.plotly_chart(fig_yr, use_container_width=True)


# ══════════════════════════════════════════════
# PAGE 6: STABILITY
# ══════════════════════════════════════════════
elif page == "⚖️ Stability":
    st.markdown("## ⚖️ Outcome Stability Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='section-header'>7-Day Rolling Discharge Effectiveness</div>", unsafe_allow_html=True)
        fig_roll = go.Figure()
        # Stagnation shading
        stag = df_f[df_f["stagnation_period"]]
        if not stag.empty:
            for _, group in stag.groupby((stag.index.to_series().diff() > 1).cumsum()):
                fig_roll.add_vrect(
                    x0=group["Date"].iloc[0], x1=group["Date"].iloc[-1],
                    fillcolor="rgba(248,81,73,0.07)", layer="below", line_width=0
                )
        fig_roll.add_trace(go.Scatter(
            x=df_f["Date"], y=df_f["rolling_discharge"],
            line=dict(color=COLOR_BLUE, width=2), name="7-day Rolling Avg"
        ))
        fig_roll.update_layout(**CHART_THEME, height=320,
                               title=dict(text="Rolling Discharge — Red = Stagnation Zones",
                                          font=dict(color="#e6edf3", size=14)))
        st.plotly_chart(fig_roll, use_container_width=True)

    with col2:
        st.markdown("<div class='section-header'>Outcome Stability Score</div>", unsafe_allow_html=True)
        fig_oss = go.Figure()
        fig_oss.add_trace(go.Scatter(
            x=df_f["Date"], y=df_f["outcome_stability_score"],
            fill="tozeroy", fillcolor="rgba(188,140,255,0.1)",
            line=dict(color=COLOR_PURPLE, width=1.5),
            name="Stability Score (Rolling Std Dev)"
        ))
        fig_oss.update_layout(**CHART_THEME, height=320,
                              title=dict(text="7-day Rolling Std Dev of Discharge Effectiveness",
                                         font=dict(color="#e6edf3", size=14)))
        st.plotly_chart(fig_oss, use_container_width=True)

    # Sudden drops
    st.markdown("<div class='section-header'>Sudden Drops in Discharge Effectiveness</div>", unsafe_allow_html=True)
    drop_threshold = df_f["discharge_change"].quantile(0.10)
    df_f["sudden_drop"] = df_f["discharge_change"] < drop_threshold

    fig_drop = go.Figure()
    fig_drop.add_trace(go.Scatter(
        x=df_f["Date"], y=df_f["discharge_change"],
        line=dict(color=COLOR_TEAL, width=1.2),
        name="Daily Change"
    ))
    drops = df_f[df_f["sudden_drop"]]
    fig_drop.add_trace(go.Scatter(
        x=drops["Date"], y=drops["discharge_change"],
        mode="markers", marker=dict(color=COLOR_RED, size=7, symbol="circle"),
        name="Sudden Drop"
    ))
    fig_drop.add_hline(y=drop_threshold, line_dash="dash",
                       line_color=COLOR_RED, opacity=0.6,
                       annotation_text="Drop threshold (P10)",
                       annotation_font_color=COLOR_RED)
    fig_drop.update_layout(**CHART_THEME, height=340,
                           title=dict(text="Daily Change in Discharge Effectiveness",
                                      font=dict(color="#e6edf3", size=14)))
    st.plotly_chart(fig_drop, use_container_width=True)

    # Stability summary cards
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("Avg Stability Score", f"{avg_stability:.4f}", "Rolling 7-day Std Dev")
    with c2:
        n_drops = int(df_f["sudden_drop"].sum())
        kpi_card("Sudden Drop Events", str(n_drops), "Days below P10 change", "bad" if n_drops > 20 else "warn")
    with c3: kpi_card("Stagnation Days", f"{stagnation_pct:.1f}%", "Below P25 rolling avg", "bad")
    with c4:
        latest_roll = df_f["rolling_discharge"].dropna().iloc[-1]
        kpi_card("Latest Rolling Avg", f"{latest_roll:.4f}", "Most recent 7-day avg",
                 "bad" if latest_roll < discharge_alert else "")