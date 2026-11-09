# Restaurant Tips — Python Data Dashboard

A small data project: load a real public dataset into SQLite, analyse it
with pandas and SQL, and show the results in a simple Flask dashboard
with matplotlib charts.

## Dataset

**Restaurant tips** — 244 rows of restaurant bills: total bill, tip, sex of
the bill payer, smoker/non-smoker, day, time (Lunch/Dinner), party size.

- Source: `tips.csv` from the seaborn example datasets,
  https://github.com/mwaskom/seaborn-data (file `tips.csv`)
- The dataset itself comes from Bryant & Smith (1995), as distributed with
  R's `reshape2` package. A copy is bundled in `data/tips.csv` so the
  project runs offline; `load_data.py` can re-download it with `--download`.

## What it does

- `load_data.py` — loads `data/tips.csv` into SQLite (`dashboard.db`),
  table `tips`, with a derived `tip_pct` column (tip / total_bill * 100)
- `analysis.py` — pandas + SQL analysis: average tip % by day, by time,
  by smoker status, average bill by party size, bill–tip correlation
- `dashboard.py` — Flask app: summary stats and matplotlib charts
  (average tip % by day, average bill by party size, tip vs bill scatter)

## Setup and run

```bash
cd python-data-dashboard
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 load_data.py        # builds dashboard.db from data/tips.csv
python3 -m pytest -q        # tests
python3 dashboard.py        # then open http://127.0.0.1:5000
```

Or run the analysis without the web app:

```bash
python3 analysis.py
```

## Findings (from this dataset — recompute, don't take my word for it)

Running `python3 analysis.py` prints the numbers. In brief: tips average
16.08% of the bill, lunch parties tip a slightly higher percentage than
dinner (16.41% vs 15.95%), and larger parties have larger bills but not
proportionally larger tips. The exact figures are in the dashboard, computed from the
data at runtime — nothing is hardcoded.

## Author

Abel Wolde — https://github.com/abel-wolde
