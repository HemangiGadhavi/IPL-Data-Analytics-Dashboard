# 🏏 IPL Data Analytics Dashboard

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?logo=streamlit)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-5.20%2B-3F4F75?logo=plotly)](https://plotly.com/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-150458?logo=pandas)](https://pandas.pydata.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An end-to-end, single-file interactive analytics dashboard built on the **IPL ball-by-ball dataset** (2008 – 2025). It covers data loading, cleaning, aggregation, and seven rich visualisation pages — all inside one `app.py`.

---

## 📸 Dashboard Pages

| Page | What you see |
|------|-------------|
| 📊 **Overview** | Season-wise KPIs, total runs & matches trend, sixes/fours growth |
| 🔍 **Data Quality** | Missing-value analysis, dtype report, raw data preview |
| 🏏 **Batting** | Top-N run scorers, strike rate, runs-vs-balls scatter |
| 🎳 **Bowling** | Top-N wicket takers, economy rate, wicket-type donut |
| 🏆 **Teams** | Wins per franchise, toss-decision impact |
| 🏟️ **Venues** | Matches hosted, avg first-innings score per ground |
| 📈 **Over Analysis** | Run rate by over — powerplay / middle / death overs |

---

## 📂 Project Structure

```
ipl_analytics/
├── app.py               ← combined backend + Streamlit frontend (single file)
├── requirements.txt     ← Python dependencies
├── report.html          ← full project report (open in browser)
├── data/
│   └── IPL.csv          ← ball-by-ball dataset (place here before running)
└── README.md
```

---

## 🗂️ Dataset

**IPL.csv** — ball-by-ball records for every IPL match from 2008 to 2025.

| Attribute | Value |
|-----------|-------|
| Rows | ~295,732 (deliveries) |
| Columns | 64 |
| Seasons | 18 (2008 – 2025) |
| Franchises | 19 (including historical teams) |
| Key columns | `match_id`, `date`, `season`, `batter`, `bowler`, `batting_team`, `bowling_team`, `runs_batter`, `runs_total`, `bowler_wicket`, `wicket_kind`, `venue`, `toss_decision`, `match_won_by` |

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/your-username/ipl-analytics.git
cd ipl-analytics/ipl_analytics
```

### 2. Place the dataset

Copy `IPL.csv` into the `data/` folder:

```
ipl_analytics/data/IPL.csv
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> **Tip:** Use a virtual environment to avoid dependency conflicts.
> ```bash
> python -m venv .venv
> # Windows
> .venv\Scripts\activate
> # macOS/Linux
> source .venv/bin/activate
> pip install -r requirements.txt
> ```

### 4. Run the dashboard

```bash
streamlit run app.py
```

The app opens at **http://localhost:8501** in your default browser.

---

## 🔧 Features

### Backend (data layer — inside `app.py`)

- **`load_data()`** — CSV loading with `@st.cache_data`, date parsing, season normalisation (handles `"2007/08"` and `2009` formats), type coercion
- **`data_quality_report()`** — per-column missing count + percentage
- **`season_summary()`** — matches, runs, sixes, fours per season
- **`top_batters()`** — runs, balls, strike rate, boundaries (season-filterable)
- **`top_bowlers()`** — wickets, economy rate (season-filterable)
- **`team_wins()`** — win count per franchise (season-filterable)
- **`toss_analysis()`** — win % for bat-first vs field-first decisions
- **`venue_analysis()`** — matches and avg first-innings score per ground
- **`wicket_distribution()`** — breakdown of dismissal modes
- **`run_rate_by_over()`** — delivery-level run rate aggregated per over

### Frontend (Streamlit UI — inside `app.py`)

- Sidebar with **season filter**, **team filter**, and **Top-N slider**
- 7 navigation pages via `st.sidebar.radio`
- Plotly charts: bar, line, area, scatter (bubble), donut
- Dual-axis season trend chart (runs + matches on one canvas)
- Phase markers on the over-analysis page (powerplay / death overs)

---

## 📊 Key Findings

- **Virat Kohli** is the all-time IPL top scorer with **9,346 runs**
- **Yuzvendra Chahal** leads with **233 wickets**
- Sixes per season have grown ~3× from 2008 to 2024
- Teams **fielding first** after winning the toss win marginally more often
- **"Caught"** is the dominant dismissal type, as expected in T20 cricket
- Death overs (16–20) generate ~2× the run rate of powerplay overs

---

## 📦 Dependencies

| Package | Min Version | Purpose |
|---------|------------|---------|
| `streamlit` | 1.35.0 | Web UI |
| `pandas` | 2.0.0 | Data processing |
| `plotly` | 5.20.0 | Interactive charts |
| `numpy` | 1.26.0 | Numerical helpers |

---

## 🖥️ System Requirements

- Python **3.9** or later
- ~500 MB RAM (dataset is loaded fully into memory)
- Modern browser (Chrome / Firefox / Edge recommended)

---

## 📄 Report

Open [`report.html`](report.html) in any browser for the full static project report including dataset overview, data quality analysis, analytics module descriptions, and key findings.

---

## 📝 License

This project is licensed under the [MIT License](LICENSE).

---

## 🤝 Contributing

Pull requests are welcome! Please open an issue first to discuss any major changes.

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/my-analysis`
3. Commit your changes: `git commit -m "Add new analysis"`
4. Push: `git push origin feature/my-analysis`
5. Open a Pull Request

---

*Built with Python · Streamlit · Plotly · Pandas*
