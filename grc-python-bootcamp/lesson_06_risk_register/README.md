# Lesson 6 — Risk Register Analyzer (pandas)

**GRC problem:** A risk register in a spreadsheet is hard to slice. Leadership
wants "the top 5 residual risks" and "which category is worst" on demand. This
tool scores every risk (likelihood × impact), assigns severity bands, and
produces those views in seconds. Supports ISO 27001 Clause 6.1 risk
assessment, NIST RA, and SOC 2 CC3.x.

**Python you'll learn:** your first taste of **pandas** — DataFrames, vectorized
column math (`df["a"] * df["b"]`), `apply` with a helper function,
`sort_values`, and `groupby` aggregation.

> New dependency: `pandas`. Install with `pip install -r ../requirements.txt`.

---

## Run it

```bash
cd lesson_06_risk_register
python risk_analyzer.py
python risk_analyzer.py --top 3
python risk_analyzer.py --by-category
python risk_analyzer.py --out scored_risks.csv
```

Output (abridged):

```
Register overview: 10 risks
  Critical : 2
  High     : 6
  ...
Top 3 risks by RESIDUAL score:
 risk_id  category  residual_score residual_band   owner  description
   R-003      Data              25      Critical  Engineering  Customer PII ...
```

## How it works

- `pd.read_csv()` loads the register into a **DataFrame** (a table).
- **Vectorized math** — `df["likelihood"] * df["impact"]` multiplies entire
  columns at once. No `for` loop. This is why pandas scales to huge registers.
- `df["inherent_score"].apply(severity_band)` runs your banding function on
  every row.
- `groupby("category").agg(...)` is the spreadsheet pivot table, in code.
- `risk_reduction = inherent - residual` quantifies how much your treatments
  actually bought you — a number auditors and boards love.

## Try these exercises

1. Add a `--owner IT` filter (hint: `df[df["owner"] == "IT"]`).
2. Add an `--min-band High` filter that only shows High+Critical residual risks.
3. Produce a category pivot of *counts by residual band* using
   `pd.crosstab(df["category"], df["residual_band"])`.

## What "good" looks like

You reach for vectorized pandas operations instead of looping row by row, and
you can produce a "top N by residual score" table from any register in one
command.
