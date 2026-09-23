"""
IPL Data Analytics Dashboard
=============================
Single-file Streamlit app — backend analytics functions + frontend UI.

Run:
    streamlit run app.py
"""

import os
import warnings
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------------
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "IPL.csv")

# ---------------------------------------------------------------------------
# ==================  BACKEND — DATA LOADING & ANALYTICS  ===================
# ---------------------------------------------------------------------------


@st.cache_data(show_spinner="Loading dataset …")
def load_data(path: str) -> pd.DataFrame:
    """Load the IPL ball-by-ball CSV and return a cleaned DataFrame."""
    df = pd.read_csv(path, low_memory=False)

    # --- date ---------------------------------------------------------------
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # --- season normalise (e.g. '2007/08' → 2008, '2020/21' → 2020) --------
    def _norm_season(val):
        s = str(val)
        if "/" in s:
            return int(s.split("/")[0])
        try:
            return int(float(s))
        except (ValueError, TypeError):
            return np.nan

    df["season_year"] = df["season"].apply(_norm_season).astype("Int64")

    # --- boolean-like columns -----------------------------------------------
    for col in ["runs_not_boundary", "valid_ball", "striker_out"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def data_quality_report(df: pd.DataFrame) -> pd.DataFrame:
    """Return a DataFrame summarising missing values per column."""
    total = len(df)
    missing = df.isnull().sum()
    pct = (missing / total * 100).round(2)
    dtype = df.dtypes.astype(str)
    report = pd.DataFrame(
        {"dtype": dtype, "missing_count": missing, "missing_%": pct}
    )
    report = report[report["missing_count"] > 0].sort_values(
        "missing_count", ascending=False
    )
    return report


# --- Season-level aggregates ------------------------------------------------

def season_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Matches, total runs and sixes per season."""
    g = (
        df.groupby("season_year")
        .agg(
            matches=("match_id", "nunique"),
            total_runs=("runs_total", "sum"),
            total_sixes=("runs_batter", lambda x: (x == 6).sum()),
            total_fours=("runs_batter", lambda x: (x == 4).sum()),
        )
        .reset_index()
        .rename(columns={"season_year": "Season"})
    )
    return g.sort_values("Season")


# --- Top batters ------------------------------------------------------------

def top_batters(df: pd.DataFrame, season_year=None, n: int = 10) -> pd.DataFrame:
    """Aggregate batting stats; optionally filter by season."""
    sub = df if season_year is None else df[df["season_year"] == season_year]
    g = (
        sub.groupby("batter")
        .agg(
            runs=("runs_batter", "sum"),
            balls=("valid_ball", "sum"),
            innings=("match_id", "nunique"),
            fours=("runs_batter", lambda x: (x == 4).sum()),
            sixes=("runs_batter", lambda x: (x == 6).sum()),
        )
        .reset_index()
    )
    g["strike_rate"] = (g["runs"] / g["balls"] * 100).round(2)
    return g.nlargest(n, "runs")


# --- Top bowlers ------------------------------------------------------------

def top_bowlers(df: pd.DataFrame, season_year=None, n: int = 10) -> pd.DataFrame:
    """Aggregate bowling stats; optionally filter by season."""
    sub = df if season_year is None else df[df["season_year"] == season_year]
    g = (
        sub.groupby("bowler")
        .agg(
            wickets=("bowler_wicket", "sum"),
            balls=("valid_ball", "sum"),
            runs_conceded=("runs_bowler", "sum"),
        )
        .reset_index()
    )
    g["economy"] = (g["runs_conceded"] / (g["balls"] / 6)).round(2)
    return g.nlargest(n, "wickets")


# --- Team performance -------------------------------------------------------

def team_wins(df: pd.DataFrame, season_year=None) -> pd.DataFrame:
    """Count of wins per team (one row per match)."""
    sub = df if season_year is None else df[df["season_year"] == season_year]
    matches = sub.drop_duplicates("match_id")[["match_id", "match_won_by"]].copy()
    wins = (
        matches["match_won_by"]
        .value_counts()
        .reset_index()
        .rename(columns={"match_won_by": "Team", "count": "Wins"})
    )
    return wins.head(15)


# --- Venue analysis ---------------------------------------------------------

def venue_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Matches played and avg first-innings score per venue."""
    # first innings batting team per match/innings
    fi = df[df["innings"] == 1].copy()
    per_match = (
        fi.groupby(["match_id", "venue"])
        .agg(total_runs=("runs_total", "sum"))
        .reset_index()
    )
    venue_g = (
        per_match.groupby("venue")
        .agg(
            matches=("match_id", "nunique"),
            avg_first_innings=("total_runs", "mean"),
        )
        .reset_index()
    )
    venue_g["avg_first_innings"] = venue_g["avg_first_innings"].round(1)
    return venue_g.nlargest(15, "matches")


# --- Toss analysis ----------------------------------------------------------

def toss_analysis(df: pd.DataFrame) -> dict:
    """Win % when choosing to bat vs field."""
    matches = df.drop_duplicates("match_id")[
        ["match_id", "toss_decision", "toss_winner", "match_won_by"]
    ].copy()
    matches["toss_match_win"] = matches["toss_winner"] == matches["match_won_by"]
    summary = (
        matches.groupby("toss_decision")["toss_match_win"]
        .agg(["sum", "count"])
        .reset_index()
    )
    summary["win_%"] = (summary["sum"] / summary["count"] * 100).round(1)
    summary.columns = ["Toss Decision", "Wins", "Total", "Win %"]
    return summary


# --- Wicket types -----------------------------------------------------------

def wicket_distribution(df: pd.DataFrame, season_year=None) -> pd.DataFrame:
    sub = df if season_year is None else df[df["season_year"] == season_year]
    wk = (
        sub["wicket_kind"]
        .dropna()
        .value_counts()
        .reset_index()
        .rename(columns={"wicket_kind": "Wicket Type", "count": "Count"})
    )
    return wk


# --- Run distribution per over ----------------------------------------------

def run_rate_by_over(df: pd.DataFrame, team=None) -> pd.DataFrame:
    sub = df if team is None else df[df["batting_team"] == team]
    g = (
        sub.groupby("over")["runs_total"]
        .mean()
        .reset_index()
        .rename(columns={"runs_total": "avg_runs_per_ball"})
    )
    g["avg_runs_per_over"] = (g["avg_runs_per_ball"] * 6).round(2)
    g = g[g["over"] < 20]
    return g


# ---------------------------------------------------------------------------
# ==================  FRONTEND — STREAMLIT UI  ===============================
# ---------------------------------------------------------------------------

def _sidebar_filters(df: pd.DataFrame):
    st.sidebar.image(
        "https://upload.wikimedia.org/wikipedia/en/8/84/Indian_Premier_League_Official_Logo.svg",
        width=120,
    )
    st.sidebar.title("🏏 IPL Analytics")
    st.sidebar.markdown("---")

    seasons = sorted(df["season_year"].dropna().unique().tolist())
    sel_season = st.sidebar.selectbox(
        "Season (All = overall)", ["All"] + [int(s) for s in seasons]
    )
    season_val = None if sel_season == "All" else int(sel_season)

    teams = sorted(df["batting_team"].dropna().unique().tolist())
    sel_team = st.sidebar.selectbox("Team (batting analysis)", ["All"] + teams)
    team_val = None if sel_team == "All" else sel_team

    top_n = st.sidebar.slider("Top N players", 5, 20, 10)

    return season_val, team_val, top_n


def page_overview(df: pd.DataFrame):
    st.title("📊 IPL Data Analytics Dashboard")
    st.markdown(
        "**Ball-by-ball analytics from IPL 2008 – 2025** powered by Streamlit & Plotly."
    )

    # KPI cards
    total_matches = df["match_id"].nunique()
    total_balls = int(df["valid_ball"].sum())
    total_runs = int(df["runs_total"].sum())
    total_wickets = int(df["bowler_wicket"].sum())
    total_sixes = int((df["runs_batter"] == 6).sum())
    seasons_count = df["season_year"].nunique()

    c1, c2, c3 = st.columns(3)
    c4, c5, c6 = st.columns(3)
    c1.metric("🏟️ Total Matches", f"{total_matches:,}")
    c2.metric("🎯 Total Balls", f"{total_balls:,}")
    c3.metric("🏃 Total Runs", f"{total_runs:,}")
    c4.metric("🚀 Total Wickets", f"{total_wickets:,}")
    c5.metric("💥 Total Sixes", f"{total_sixes:,}")
    c6.metric("📅 Seasons", f"{seasons_count}")

    st.markdown("---")

    # Season trend
    ss = season_summary(df)
    fig = go.Figure()
    fig.add_trace(
        go.Bar(x=ss["Season"], y=ss["total_runs"], name="Total Runs", marker_color="#1f77b4")
    )
    fig.add_trace(
        go.Scatter(
            x=ss["Season"], y=ss["matches"], name="Matches",
            yaxis="y2", mode="lines+markers", line=dict(color="orange", width=2),
        )
    )
    fig.update_layout(
        title="Season-wise Total Runs & Matches",
        yaxis=dict(title="Total Runs"),
        yaxis2=dict(title="Matches", overlaying="y", side="right"),
        legend=dict(x=0.01, y=0.99),
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        fig2 = px.line(
            ss, x="Season", y="total_sixes",
            title="Total Sixes Per Season", markers=True,
            color_discrete_sequence=["#e63946"],
        )
        st.plotly_chart(fig2, use_container_width=True)
    with col2:
        fig3 = px.line(
            ss, x="Season", y="total_fours",
            title="Total Fours Per Season", markers=True,
            color_discrete_sequence=["#2a9d8f"],
        )
        st.plotly_chart(fig3, use_container_width=True)


def page_data_quality(df: pd.DataFrame):
    st.header("🔍 Data Quality Report")
    st.markdown(
        "Columns with **missing / null values** detected during loading are shown below."
    )

    report = data_quality_report(df)
    if report.empty:
        st.success("✅ No missing values found!")
    else:
        st.dataframe(report, use_container_width=True)

        fig = px.bar(
            report.reset_index().rename(columns={"index": "Column"}),
            x="Column", y="missing_%",
            title="Missing Value % Per Column",
            color="missing_%",
            color_continuous_scale="Reds",
            height=400,
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("📋 Dataset Sample (first 100 rows)")
    st.dataframe(df.head(100), use_container_width=True)

    st.subheader("📐 Column Dtypes & Non-null Counts")
    info = pd.DataFrame(
        {
            "dtype": df.dtypes.astype(str),
            "non_null": df.notnull().sum(),
            "unique": df.nunique(),
        }
    )
    st.dataframe(info, use_container_width=True)


def page_batting(df: pd.DataFrame, season_val, top_n):
    st.header("🏏 Batting Analysis")

    batters = top_batters(df, season_year=season_val, n=top_n)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            batters, x="batter", y="runs",
            title=f"Top {top_n} Run Scorers",
            color="runs", color_continuous_scale="Blues",
            text="runs",
        )
        fig.update_layout(xaxis_tickangle=-45, height=420)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.bar(
            batters, x="batter", y="strike_rate",
            title=f"Strike Rate – Top {top_n} Batters",
            color="strike_rate", color_continuous_scale="Oranges",
            text="strike_rate",
        )
        fig2.update_layout(xaxis_tickangle=-45, height=420)
        st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.scatter(
        batters, x="balls", y="runs",
        size="sixes", color="strike_rate",
        hover_name="batter", text="batter",
        title="Runs vs Balls Faced (bubble = sixes)",
        color_continuous_scale="Viridis", height=450,
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader(f"Top {top_n} Batters — Detail Table")
    st.dataframe(batters.reset_index(drop=True), use_container_width=True)


def page_bowling(df: pd.DataFrame, season_val, top_n):
    st.header("🎳 Bowling Analysis")

    bowlers = top_bowlers(df, season_year=season_val, n=top_n)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            bowlers, x="bowler", y="wickets",
            title=f"Top {top_n} Wicket Takers",
            color="wickets", color_continuous_scale="Purples",
            text="wickets",
        )
        fig.update_layout(xaxis_tickangle=-45, height=420)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.bar(
            bowlers, x="bowler", y="economy",
            title=f"Economy Rate – Top {top_n} Bowlers",
            color="economy", color_continuous_scale="Reds",
            text="economy",
        )
        fig2.update_layout(xaxis_tickangle=-45, height=420)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Wicket Type Distribution")
    wk = wicket_distribution(df, season_year=season_val)
    fig3 = px.pie(
        wk, names="Wicket Type", values="Count",
        title="How Wickets Fall", hole=0.4,
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader(f"Top {top_n} Bowlers — Detail Table")
    st.dataframe(bowlers.reset_index(drop=True), use_container_width=True)


def page_teams(df: pd.DataFrame, season_val):
    st.header("🏆 Team Performance")

    wins = team_wins(df, season_year=season_val)
    fig = px.bar(
        wins, x="Team", y="Wins",
        title="Wins Per Team",
        color="Wins", color_continuous_scale="Teal",
        text="Wins",
    )
    fig.update_layout(xaxis_tickangle=-45, height=450)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Toss Decision Impact")
    toss = toss_analysis(df)
    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(toss, use_container_width=True)
    with col2:
        fig2 = px.bar(
            toss, x="Toss Decision", y="Win %",
            title="Win % by Toss Decision",
            color="Toss Decision",
            text="Win %",
        )
        st.plotly_chart(fig2, use_container_width=True)


def page_venue(df: pd.DataFrame):
    st.header("🏟️ Venue Analysis")

    venues = venue_analysis(df)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            venues, x="venue", y="matches",
            title="Matches Hosted Per Venue",
            color="matches", color_continuous_scale="Cividis",
        )
        fig.update_layout(xaxis_tickangle=-45, height=430)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.bar(
            venues, x="venue", y="avg_first_innings",
            title="Avg First-Innings Score Per Venue",
            color="avg_first_innings", color_continuous_scale="RdYlGn",
        )
        fig2.update_layout(xaxis_tickangle=-45, height=430)
        st.plotly_chart(fig2, use_container_width=True)


def page_over_analysis(df: pd.DataFrame, team_val):
    st.header("📈 Over-by-Over Run Rate")

    rr = run_rate_by_over(df, team=team_val)
    fig = px.area(
        rr, x="over", y="avg_runs_per_over",
        title="Average Runs per Over" + (f" — {team_val}" if team_val else " (All Teams)"),
        markers=True,
        color_discrete_sequence=["#f4a261"],
    )
    fig.add_vline(x=5.5, line_dash="dash", line_color="red", annotation_text="Powerplay ends")
    fig.add_vline(x=14.5, line_dash="dash", line_color="blue", annotation_text="Death overs start")
    fig.update_layout(xaxis=dict(tickmode="linear", dtick=1), height=420)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Raw Table")
    st.dataframe(rr, use_container_width=True)


# ---------------------------------------------------------------------------
# ==================  MAIN  =================================================
# ---------------------------------------------------------------------------

def main():
    st.set_page_config(
        page_title="IPL Analytics",
        page_icon="🏏",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Load data
    if not os.path.exists(DATA_PATH):
        st.error(
            f"Dataset not found at `{DATA_PATH}`. "
            "Place `IPL.csv` inside the `data/` folder and restart."
        )
        st.stop()

    df = load_data(DATA_PATH)

    # Sidebar filters
    season_val, team_val, top_n = _sidebar_filters(df)

    # Navigation
    page = st.sidebar.radio(
        "Navigate",
        [
            "📊 Overview",
            "🔍 Data Quality",
            "🏏 Batting",
            "🎳 Bowling",
            "🏆 Teams",
            "🏟️ Venues",
            "📈 Over Analysis",
        ],
    )
    st.sidebar.markdown("---")
    st.sidebar.caption("Dataset: IPL ball-by-ball (2008–2025)")

    if page == "📊 Overview":
        page_overview(df)
    elif page == "🔍 Data Quality":
        page_data_quality(df)
    elif page == "🏏 Batting":
        page_batting(df, season_val, top_n)
    elif page == "🎳 Bowling":
        page_bowling(df, season_val, top_n)
    elif page == "🏆 Teams":
        page_teams(df, season_val)
    elif page == "🏟️ Venues":
        page_venue(df)
    elif page == "📈 Over Analysis":
        page_over_analysis(df, team_val)


if __name__ == "__main__":
    main()
