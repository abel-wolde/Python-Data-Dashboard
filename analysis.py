"""Analysis of the restaurant tips dataset, with pandas and SQL.

All figures are computed from the SQLite database built by load_data.py —
nothing here is hardcoded. Run as a script to print a summary:

    python3 analysis.py
"""

import sqlite3
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent
DB_PATH = BASE / "dashboard.db"


def load_frame(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    try:
        return pd.read_sql_query("SELECT * FROM tips", conn)
    finally:
        conn.close()


def avg_tip_pct_by_day(df):
    """Average tip percentage per day, via SQL-style grouping in pandas."""
    return (
        df.groupby("day", observed=True)["tip_pct"]
        .mean()
        .round(2)
        .reindex(["Thur", "Fri", "Sat", "Sun"])
        .dropna()
    )


def avg_tip_pct_by_time(df):
    return df.groupby("time", observed=True)["tip_pct"].mean().round(2)


def avg_tip_pct_by_smoker(df):
    return df.groupby("smoker", observed=True)["tip_pct"].mean().round(2)


def avg_bill_by_party_size(df):
    return df.groupby("size", observed=True)["total_bill"].mean().round(2)


def bill_tip_correlation(df):
    return round(float(df["total_bill"].corr(df["tip"])), 4)


def summary_stats(df):
    return {
        "rows": int(len(df)),
        "avg_bill": round(float(df["total_bill"].mean()), 2),
        "avg_tip": round(float(df["tip"].mean()), 2),
        "avg_tip_pct": round(float(df["tip_pct"].mean()), 2),
        "bill_tip_correlation": bill_tip_correlation(df),
    }


def avg_tip_pct_by_day_sql(db_path=DB_PATH):
    """Same figure as avg_tip_pct_by_day, computed in SQL instead."""
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            "SELECT day, ROUND(AVG(tip_pct), 2) FROM tips GROUP BY day ORDER BY day"
        ).fetchall()
    finally:
        conn.close()
    return dict(rows)


def main():
    df = load_frame()
    print("Restaurant tips — summary")
    print("=========================")
    for key, value in summary_stats(df).items():
        print(f"{key}: {value}")
    print("\nAverage tip % by day:")
    print(avg_tip_pct_by_day(df).to_string())
    print("\nAverage tip % by time (Lunch/Dinner):")
    print(avg_tip_pct_by_time(df).to_string())
    print("\nAverage tip % by smoker:")
    print(avg_tip_pct_by_smoker(df).to_string())
    print("\nAverage bill by party size:")
    print(avg_bill_by_party_size(df).to_string())
    print("\nAverage tip % by day (computed in SQL):")
    print(avg_tip_pct_by_day_sql())


if __name__ == "__main__":
    main()
