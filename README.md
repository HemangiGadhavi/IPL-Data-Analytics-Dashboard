# 🏏 IPL Data Analytics Dashboard

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-5.20%2B-3F4F75?logo=plotly&logoColor=white)](https://plotly.com/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e.svg)](LICENSE)

An interactive, single-file data analytics dashboard for the **IPL ball-by-ball dataset (2008 – 2025)**. The entire project — data loading, cleaning, all analytics logic, and the Streamlit frontend — lives in one file: `app.py`.

---

## 📸 Dashboard Pages

| # | Page | What you get |
|---|------|-------------|
| 1 | 📊 **Overview** | 6 KPI cards, season-wise runs & matches dual-axis chart, sixes & fours trend lines |
| 2 | 🔍 **Data Quality** | Missing-value table + bar chart, raw dataset preview (100 rows), dtype/unique report |
| 3 | 🏏 **Batting** | Top-N run scorers, strike rate bars, runs-vs-balls scatter (bubble = sixes), detail table |
| 4 | 🎳 **Bowling** | Top-N wicket takers, economy rate bars, wicket-type donut chart, detail table |
| 5 | 🏆 **Teams** | Win count per franchise, toss-decision win % table + chart |
| 6 | 🏟️ **Venues** | Matches hosted per ground, avg first-innings score per ground |
| 7 | 📈 **Over Analysis** | Area chart of avg runs per over with powerplay & death-over phase markers |

All pages respect three sidebar filters: **Season**, **Team**, and **Top-N** slider.

---

## 📂 Project Structure

```
ipl_analytics/
├── app.py                           ← combined backend + Streamlit frontend
├── requirements.txt                 ← Python dependencies
├── IPL_Analytics_Presentation.pptx ← 10-slide project presentation
├── data/
│   └── IPL.csv                      ← ball-by-ball dataset (place here)
└── README.md
```

---

## 🗂️ Dataset

**IPL.csv** — ball-by-ball records for every IPL match from 2008 to 2025.

| Attribute | Detail |
|-----------|--------|
| Rows | 295,732 (one per delivery) |
| Columns | 64 |
| Seasons | 18 (2008 – 2025) |
| Franchises | 19 (including historical teams) |

### Key columns

| Column | Type | Description |
|--------|------|-------------|
| `match_id` | int | Unique match identifier |
| `date` | date | Match date (YYYY-MM-DD) |
| `season` | str | IPL season label (`2007/08`, `2023`, etc.) |
| `batting_team` / `bowling_team` | str | Franchise names |
| `batter` / `bowler` | str | Player names |
| `over` / `ball` | int | Over (0-indexed) and ball number |
| `runs_batter` | int | Runs scored off the bat |
| `runs_total` | int | Total runs on the delivery (bat + extras) |
| `bowler_wicket` | int | `1` = wicket, `0` = not |
| `wicket_kind` | str | Dismissal type (caught, bowled, …) |
| `valid_ball` | int | `1` = legal delivery |
| `venue` / `city` | str | Ground name and city |
| `toss_decision` | str | `bat` or `field` |
| `match_won_by` | str | Winning team |

---

## 🚀 Quick Start

### 1 — Clone the repository

```bash
git clone https://github.com/your-username/ipl-analytics.git
cd ipl-analytics/ipl_analytics
```

### 2 — Place the dataset

```
ipl_analytics/data/IPL.csv
```

### 3 — Install dependencies

```bash
pip install -r requirements.txt
```

> **Recommended:** use a virtual environment.
> ```bash
> python -m venv .venv
> # Windows
> .venv\Scripts\activate
> # macOS / Linux
> source .venv/bin/activate
>
> pip install -r requirements.txt
> ```

### 4 — Run the dashboard

```bash
# Preferred (always works)
python -m streamlit run app.py

# Or, if streamlit is on your PATH
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

> **Windows PATH note:** if `streamlit` is not recognised, run via
> `python -m streamlit run app.py`. To fix permanently, add your Python
> Scripts folder (e.g. `%APPDATA%\Python\Python312\Scripts`) to your
> user PATH.

---

## 🔧 Backend Analytics Functions

All analytics live in `app.py` as plain Python functions, cached with `@st.cache_data`.

| Function | Description |
|----------|-------------|
| `load_data(path)` | Load CSV, parse dates, normalise `season_year`, coerce flag columns |
| `data_quality_report(df)` | Per-column missing count and % |
| `season_summary(df)` | Matches, total runs, sixes, fours per season |
| `top_batters(df, season_year, n)` | Runs, balls, strike rate, 4s, 6s — season-filterable |
| `top_bowlers(df, season_year, n)` | Wickets, economy rate — season-filterable |
| `team_wins(df, season_year)` | Win count per franchise — season-filterable |
| `toss_analysis(df)` | Win % for bat-first vs field-first |
| `venue_analysis(df)` | Matches hosted + avg first-innings score per ground |
| `wicket_distribution(df, season_year)` | Breakdown of dismissal modes |
| `run_rate_by_over(df, team)` | Avg runs per over, filterable by team |

---

## 📊 Key Findings

| Finding | Value |
|---------|-------|
| All-time top scorer | **V Kohli** — 9,346 runs |
| All-time leading wicket-taker | **YS Chahal** — 233 wickets |
| Most franchise wins | **Mumbai Indians** — 148 wins |
| Toss: field-first win % | **53.7%** vs 44.3% batting first |
| Most common dismissal | **Caught** (~57% of all wickets) |
| Highest-scoring ground | **Wankhede Stadium** (avg 178.9 first-innings) |
| Death overs avg RPO | **~10.3** vs ~7.5 in middle overs |

---

## 📦 Dependencies

| Package | Min version | Purpose |
|---------|-------------|---------|
| `streamlit` | 1.35.0 | Web UI |
| `pandas` | 2.0.0 | Data loading, cleaning, aggregation |
| `plotly` | 5.20.0 | Interactive charts |
| `numpy` | 1.26.0 | Numerical helpers |

Install all at once:

```bash
pip install -r requirements.txt
```

---

## 🖥️ System Requirements

- Python **3.9** or later
- ~500 MB RAM (dataset fully loaded into memory)
- Modern browser: Chrome, Firefox, or Edge

---

## 📑 Presentation

A 10-slide PowerPoint presentation (`IPL_Analytics_Presentation.pptx`) is included, covering:

1. Title
2. Project Overview
3. Dataset Structure
4. Data Quality Analysis
5. Batting Analysis
6. Bowling Analysis
7. Team & Toss Analysis
8. Venue Analysis
9. Over-by-Over Run Rate
10. Key Takeaways

---

## 🤝 Contributing

Pull requests are welcome. Please open an issue first to discuss major changes.

```bash
git checkout -b feature/my-analysis
git commit -m "Add new analysis"
git push origin feature/my-analysis
# then open a Pull Request
```

---

## 📝 License

This project is licensed under the [MIT License](LICENSE).

---

*Built with Python · Streamlit · Plotly · Pandas*
