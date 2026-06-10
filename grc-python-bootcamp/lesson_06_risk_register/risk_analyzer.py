"""Lesson 6 - Risk Register Analyzer (pandas).

A GRC tool that loads your risk register, computes inherent and residual risk
scores, assigns severity bands, and produces the views leadership actually asks
for: the top risks, the risk reduction from treatments, and a breakdown by
category. This supports risk assessment controls (ISO 27001 Clause 6.1 / A.5.x,
NIST RA, SOC 2 CC3.x).

Concepts taught: `pandas` DataFrames, creating computed columns vectorized,
`apply` with a helper, `sort_values`, `groupby`/aggregation, and saving an
enriched CSV.

Run it:
    python risk_analyzer.py
    python risk_analyzer.py --top 3
    python risk_analyzer.py --by-category
    python risk_analyzer.py --out scored_risks.csv
"""

import argparse

import pandas as pd


def severity_band(score):
    """Map a 1-25 risk score to a qualitative band (a common 5x5 matrix)."""
    if score >= 15:
        return "Critical"
    if score >= 10:
        return "High"
    if score >= 5:
        return "Medium"
    return "Low"


def load_and_score(path):
    """Load the register and add computed risk columns."""
    df = pd.read_csv(path)

    # Vectorized math: pandas multiplies whole columns at once - no loop needed.
    df["inherent_score"] = df["likelihood"] * df["impact"]
    df["residual_score"] = df["residual_likelihood"] * df["residual_impact"]
    df["risk_reduction"] = df["inherent_score"] - df["residual_score"]

    # apply() runs our helper on every value in the column.
    df["inherent_band"] = df["inherent_score"].apply(severity_band)
    df["residual_band"] = df["residual_score"].apply(severity_band)
    return df


def show_top(df, n):
    print(f"Top {n} risks by RESIDUAL score:\n")
    cols = ["risk_id", "category", "residual_score", "residual_band", "owner", "description"]
    top = df.sort_values("residual_score", ascending=False).head(n)
    print(top[cols].to_string(index=False))


def show_by_category(df):
    print("Risk by category (count and average residual score):\n")
    summary = (
        df.groupby("category")
        .agg(risks=("risk_id", "count"),
             avg_residual=("residual_score", "mean"),
             max_residual=("residual_score", "max"))
        .sort_values("avg_residual", ascending=False)
        .round(1)
    )
    print(summary.to_string())


def show_overview(df):
    total = len(df)
    bands = df["residual_band"].value_counts()
    reduced = df["risk_reduction"].sum()
    print(f"Register overview: {total} risks")
    for band in ("Critical", "High", "Medium", "Low"):
        print(f"  {band:<9}: {int(bands.get(band, 0))}")
    print(f"Total risk-score reduction from treatments: {int(reduced)}")


def main():
    parser = argparse.ArgumentParser(description="Score and analyze a GRC risk register.")
    parser.add_argument("--file", default="risk_register.csv", help="Risk register CSV.")
    parser.add_argument("--top", type=int, default=5, help="How many top risks to show.")
    parser.add_argument("--by-category", action="store_true", help="Show the per-category breakdown.")
    parser.add_argument("--out", default=None, help="Write the scored register to a CSV.")
    args = parser.parse_args()

    df = load_and_score(args.file)

    show_overview(df)
    print()
    show_top(df, args.top)
    if args.by_category:
        print()
        show_by_category(df)

    if args.out:
        df.to_csv(args.out, index=False)
        print(f"\nScored register written to {args.out}")


if __name__ == "__main__":
    main()
