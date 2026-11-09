"""Flask dashboard for the restaurant tips dataset.

Routes:
    /                              summary page with stats and charts
    /chart/tip_pct_by_day.png      bar chart: average tip % by day
    /chart/bill_by_size.png        bar chart: average bill by party size
    /chart/tip_vs_bill.png         scatter: tip vs total bill

Run:  python3 dashboard.py   then open http://127.0.0.1:5000
Requires dashboard.db — build it first with: python3 load_data.py
"""

import io
import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from flask import Flask, render_template, send_file

import analysis

BASE = Path(__file__).resolve().parent

app = Flask(__name__, template_folder=str(BASE / "templates"))


def _png(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return send_file(buf, mimetype="image/png")


@app.route("/")
def index():
    df = analysis.load_frame()
    stats = analysis.summary_stats(df)
    return render_template(
        "index.html",
        stats=stats,
        by_day=analysis.avg_tip_pct_by_day(df).to_dict(),
        by_time=analysis.avg_tip_pct_by_time(df).to_dict(),
        by_smoker=analysis.avg_tip_pct_by_smoker(df).to_dict(),
        by_size=analysis.avg_bill_by_party_size(df).to_dict(),
    )


@app.route("/chart/tip_pct_by_day.png")
def chart_tip_pct_by_day():
    df = analysis.load_frame()
    series = analysis.avg_tip_pct_by_day(df)
    fig, ax = plt.subplots()
    ax.bar(series.index, series.values)
    ax.set_title("Average tip % by day")
    ax.set_ylabel("Tip %")
    return _png(fig)


@app.route("/chart/bill_by_size.png")
def chart_bill_by_size():
    df = analysis.load_frame()
    series = analysis.avg_bill_by_party_size(df)
    fig, ax = plt.subplots()
    ax.bar([str(i) for i in series.index], series.values)
    ax.set_title("Average bill by party size")
    ax.set_xlabel("Party size")
    ax.set_ylabel("Average bill ($)")
    return _png(fig)


@app.route("/chart/tip_vs_bill.png")
def chart_tip_vs_bill():
    df = analysis.load_frame()
    fig, ax = plt.subplots()
    ax.scatter(df["total_bill"], df["tip"], alpha=0.6)
    ax.set_title("Tip vs total bill")
    ax.set_xlabel("Total bill ($)")
    ax.set_ylabel("Tip ($)")
    return _png(fig)


if __name__ == "__main__":
    if not (BASE / "dashboard.db").exists():
        raise SystemExit("dashboard.db not found — run: python3 load_data.py")
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)), debug=False)
