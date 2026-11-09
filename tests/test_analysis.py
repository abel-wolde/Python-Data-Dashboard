import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import analysis
import load_data


@pytest.fixture
def df(tmp_path):
    db = tmp_path / "test.db"
    csv = Path(__file__).resolve().parents[1] / "data" / "tips.csv"
    load_data.load(db_path=db, csv_path=csv)
    conn_df = pd.read_sql_query("SELECT * FROM tips", __import__("sqlite3").connect(db))
    return conn_df


def test_load_row_count_and_columns(df):
    assert len(df) == 244
    for col in ["total_bill", "tip", "sex", "smoker", "day", "time", "size", "tip_pct"]:
        assert col in df.columns


def test_tip_pct_is_tip_over_bill(df):
    row = df.iloc[0]
    assert row["tip_pct"] == pytest.approx(row["tip"] / row["total_bill"] * 100, abs=0.01)


def test_summary_stats(df):
    stats = analysis.summary_stats(df)
    assert stats["rows"] == 244
    assert 15 < stats["avg_tip_pct"] < 17
    assert stats["avg_bill"] == pytest.approx(df["total_bill"].mean(), abs=0.01)
    assert 0.5 < stats["bill_tip_correlation"] < 1.0


def test_avg_tip_pct_by_day_covers_four_days(df):
    by_day = analysis.avg_tip_pct_by_day(df)
    assert set(by_day.index) == {"Thur", "Fri", "Sat", "Sun"}
    assert all(0 < v < 30 for v in by_day.values)


def test_avg_bill_rises_with_party_size(df):
    by_size = analysis.avg_bill_by_party_size(df)
    # larger parties pay larger bills on average (size 1 vs size 4+)
    assert by_size.loc[1] < by_size.loc[4]


def test_sql_and_pandas_day_figures_agree(tmp_path):
    db = tmp_path / "test.db"
    csv = Path(__file__).resolve().parents[1] / "data" / "tips.csv"
    load_data.load(db_path=db, csv_path=csv)
    df = pd.read_sql_query("SELECT * FROM tips", __import__("sqlite3").connect(db))
    pandas_result = {k: float(v) for k, v in analysis.avg_tip_pct_by_day(df).items()}
    sql_result = analysis.avg_tip_pct_by_day_sql(db_path=db)
    assert set(sql_result) == set(pandas_result)
    for day in pandas_result:
        assert sql_result[day] == pytest.approx(pandas_result[day], abs=0.01)


def test_load_rejects_bad_csv(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("a,b\n1,2\n")
    with pytest.raises(ValueError):
        load_data.load(db_path=tmp_path / "bad.db", csv_path=bad)
