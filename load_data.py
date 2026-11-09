"""Load the restaurant tips dataset into SQLite.

Source: tips.csv from https://github.com/mwaskom/seaborn-data
(a copy is bundled in data/tips.csv; use --download to re-fetch it).

Usage:
    python3 load_data.py               # load bundled CSV into dashboard.db
    python3 load_data.py --download    # re-download the CSV first, then load
"""

import argparse
import sqlite3
import sys
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA_CSV = BASE / "data" / "tips.csv"
DB_PATH = BASE / "dashboard.db"
SOURCE_URL = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/tips.csv"

EXPECTED_COLUMNS = ["total_bill", "tip", "sex", "smoker", "day", "time", "size"]


def load(db_path=DB_PATH, csv_path=DATA_CSV):
    import pandas as pd

    df = pd.read_csv(csv_path)
    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"CSV is missing columns: {missing}")
    df = df[EXPECTED_COLUMNS].copy()
    df["tip_pct"] = (df["tip"] / df["total_bill"] * 100).round(2)
    if (df["total_bill"] <= 0).any() or (df["tip"] < 0).any():
        raise ValueError("CSV contains non-positive bills or negative tips")

    conn = sqlite3.connect(db_path)
    try:
        conn.execute("DROP TABLE IF EXISTS tips")
        df.to_sql("tips", conn, index=False)
        conn.commit()
        count = conn.execute("SELECT COUNT(*) FROM tips").fetchone()[0]
    finally:
        conn.close()
    return count


def main(argv=None):
    parser = argparse.ArgumentParser(description="Load tips dataset into SQLite")
    parser.add_argument("--download", action="store_true",
                        help="re-download tips.csv from the seaborn-data repo first")
    args = parser.parse_args(argv)
    if args.download:
        print(f"Downloading {SOURCE_URL} ...")
        urllib.request.urlretrieve(SOURCE_URL, DATA_CSV)
    count = load()
    print(f"Loaded {count} rows into {DB_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
