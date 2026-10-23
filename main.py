"""Expense Tracker App using Data Science.

Generate synthetic transactions, clean them, analyze spending, and save reports/charts.
Run: python main.py
"""

from pathlib import Path
import argparse
import os
os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parent / ".matplotlib"))
import numpy as np
import pandas as pd
import matplotlib

# Charts are written to files, so use a headless backend (no Tk/Tcl required).
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "outputs"
IMAGE_DIR = ROOT / "images"
CATEGORIES = ["Food", "Transport", "Rent", "Utilities", "Shopping", "Healthcare", "Entertainment", "Education"]
PAYMENT_METHODS = ["UPI", "Card", "Cash", "Bank Transfer"]


def generate_expenses(months: int = 12, seed: int = 42, transactions_per_month: int = 65) -> pd.DataFrame:
    """Create a reproducible, realistic-looking (but entirely synthetic) dataset."""
    rng = np.random.default_rng(seed)
    end = pd.Timestamp.today().normalize()
    start = (end - pd.DateOffset(months=months)).normalize()
    days = (end - start).days + 1
    dates = start + pd.to_timedelta(rng.integers(0, max(days, 1), transactions_per_month * months), unit="D")
    weights = [0.24, 0.13, 0.09, 0.12, 0.16, 0.06, 0.13, 0.07]
    category = rng.choice(CATEGORIES, len(dates), p=weights)
    typical = {"Food": 320, "Transport": 450, "Rent": 14000, "Utilities": 1100,
               "Shopping": 1600, "Healthcare": 900, "Entertainment": 700, "Education": 1200}
    amounts = np.array([rng.lognormal(np.log(typical[c]), 0.48) for c in category]).round(2)
    # Add a predictable rent transaction each month to make recurring costs visible.
    rent_rows = pd.DataFrame({"date": pd.date_range(start=start, end=end, freq="MS"),
                              "category": "Rent", "amount": 14000.0,
                              "payment_method": "Bank Transfer", "description": "Monthly rent"})
    data = pd.DataFrame({"date": dates, "category": category, "amount": amounts,
                         "payment_method": rng.choice(PAYMENT_METHODS, len(dates)),
                         "description": [f"{c} purchase" for c in category]})
    data = pd.concat([data, rent_rows], ignore_index=True)
    return data.sort_values("date").reset_index(drop=True)


def clean_expenses(raw: pd.DataFrame) -> pd.DataFrame:
    """Normalize fields and discard rows that cannot represent a valid expense."""
    df = raw.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    required = {"date", "category", "amount", "payment_method"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["category"] = df["category"].astype("string").str.strip().str.title()
    df["payment_method"] = df["payment_method"].astype("string").str.strip().str.title()
    df = df.dropna(subset=["date", "amount", "category", "payment_method"])
    df = df[df["amount"] > 0].drop_duplicates()
    if "description" not in df:
        df["description"] = ""
    return df.sort_values("date").reset_index(drop=True)


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["month"] = out["date"].dt.to_period("M").astype(str)
    out["weekday"] = out["date"].dt.day_name()
    out["year"] = out["date"].dt.year
    return out


def analyze(df: pd.DataFrame, monthly_budget: float = 50000) -> dict[str, pd.DataFrame]:
    monthly = df.groupby("month", as_index=False).agg(total_spend=("amount", "sum"), transactions=("amount", "size"))
    monthly["budget"] = monthly_budget
    monthly["over_budget"] = monthly["total_spend"] > monthly_budget
    category = df.groupby("category", as_index=False).agg(total_spend=("amount", "sum"), transactions=("amount", "size"))
    category["share_pct"] = category["total_spend"] / category["total_spend"].sum() * 100
    payment = df.groupby("payment_method", as_index=False).agg(total_spend=("amount", "sum"), transactions=("amount", "size"))
    weekday = df.groupby("weekday", as_index=False).agg(total_spend=("amount", "sum"), transactions=("amount", "size"))
    return {"monthly": monthly, "category": category.sort_values("total_spend", ascending=False),
            "payment": payment.sort_values("total_spend", ascending=False), "weekday": weekday}


def create_charts(df: pd.DataFrame, results: dict[str, pd.DataFrame]) -> None:
    IMAGE_DIR.mkdir(exist_ok=True)
    sns.set_theme(style="whitegrid", palette="viridis")
    fig, ax = plt.subplots(figsize=(11, 5))
    sns.barplot(data=results["category"], x="category", y="total_spend", ax=ax)
    ax.set(title="Total Spend by Category", xlabel="Category", ylabel="Amount")
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout(); fig.savefig(IMAGE_DIR / "category_spending.png", dpi=160); plt.close(fig)

    fig, ax = plt.subplots(figsize=(11, 5))
    sns.lineplot(data=results["monthly"], x="month", y="total_spend", marker="o", ax=ax, label="Spend")
    ax.plot(results["monthly"]["month"], results["monthly"]["budget"], linestyle="--", color="red", label="Budget")
    ax.set(title="Monthly Spending vs Budget", xlabel="Month", ylabel="Amount")
    ax.tick_params(axis="x", rotation=45); ax.legend(); fig.tight_layout()
    fig.savefig(IMAGE_DIR / "monthly_trend.png", dpi=160); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(results["category"]["total_spend"], labels=results["category"]["category"], autopct="%1.1f%%", startangle=90)
    ax.set_title("Share of Spending by Category"); fig.tight_layout()
    fig.savefig(IMAGE_DIR / "category_share.png", dpi=160); plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(data=results["payment"], x="payment_method", y="total_spend", ax=ax)
    ax.set(title="Spend by Payment Method", xlabel="Payment method", ylabel="Amount")
    fig.tight_layout(); fig.savefig(IMAGE_DIR / "payment_methods.png", dpi=160); plt.close(fig)


def build_insights(df: pd.DataFrame, results: dict[str, pd.DataFrame], budget: float) -> list[str]:
    category = results["category"]
    monthly = results["monthly"]
    if df.empty:
        return ["No valid expenses found. Add transactions and run the analysis again."]
    peak = monthly.loc[monthly["total_spend"].idxmax()]
    lines = [f"Total recorded spend: {df.amount.sum():,.2f} across {len(df):,} transactions.",
             f"Largest category: {category.iloc[0].category} ({category.iloc[0].total_spend:,.2f}, {category.iloc[0].share_pct:.1f}% of spend).",
             f"Highest-spend month: {peak.month} ({peak.total_spend:,.2f}).",
             f"Average monthly spend: {monthly.total_spend.mean():,.2f}; comparison budget: {budget:,.2f}."]
    over = monthly[monthly["over_budget"]]
    lines.append(f"Months above budget: {', '.join(over.month.astype(str))}." if len(over) else "No months exceeded the selected budget.")
    return lines


def run(input_file: Path | None, months: int, seed: int, budget: float) -> None:
    DATA_DIR.mkdir(exist_ok=True); OUTPUT_DIR.mkdir(exist_ok=True); IMAGE_DIR.mkdir(exist_ok=True)
    if input_file:
        raw = pd.read_csv(input_file)
    else:
        raw = generate_expenses(months=months, seed=seed)
        raw.to_csv(DATA_DIR / "synthetic_expenses.csv", index=False)
    df = add_features(clean_expenses(raw))
    results = analyze(df, budget)
    df.to_csv(OUTPUT_DIR / "cleaned_expenses.csv", index=False)
    for name, table in results.items():
        table.to_csv(OUTPUT_DIR / f"{name}_summary.csv", index=False)
    create_charts(df, results)
    insights = build_insights(df, results, budget)
    (OUTPUT_DIR / "insights.txt").write_text("\n".join(f"- {line}" for line in insights), encoding="utf-8")
    print(f"Analyzed {len(df):,} valid transactions.")
    print("\n".join(f"• {line}" for line in insights))
    print(f"\nReports: {OUTPUT_DIR}\nCharts: {IMAGE_DIR}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create and analyze synthetic expense data.")
    parser.add_argument("--input", type=Path, help="Optional CSV with date, category, amount, payment_method columns")
    parser.add_argument("--months", type=int, default=12, help="Synthetic history length (default: 12)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--budget", type=float, default=50000, help="Monthly comparison budget")
    args = parser.parse_args()
    run(args.input, args.months, args.seed, args.budget)
