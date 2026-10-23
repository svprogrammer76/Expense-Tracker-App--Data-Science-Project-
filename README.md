# Expense Tracker App using Data Science

A beginner-friendly, portfolio-ready Python project that creates (or accepts) expense transactions, cleans them, summarizes spending patterns, flags months over a chosen budget, and produces charts and CSV reports. The default data is synthetic and reproducible; it is not real financial data and should not be used to make actual financial decisions.

## Problem and solution

People and small teams often record expenses across notes, statements, and spreadsheets, making it hard to see where money goes or whether spending is changing. This project demonstrates a compact analysis workflow: input → validation and cleaning → feature engineering → aggregation → visualization → plain-language insights. Individuals can use the pattern for personal budgeting; businesses can adapt it for expense monitoring, cost control, and planning (with appropriate privacy and accounting controls).

**Simple explanation:** Enter or generate expenses, then see which categories and months account for spending.

**Technical explanation:** A pandas pipeline parses dates and amounts, removes unusable/duplicate/non-positive records, derives month and weekday features, groups values by category/month/payment method, and exports Matplotlib/Seaborn visualizations and summary tables.

## Features

- Reproducible synthetic transactions (`--seed`), including a recurring monthly rent item
- CSV input support with schema validation and data cleaning
- Category, monthly, payment-method, and weekday summaries
- Configurable monthly budget comparison and generated insight text
- Saved charts and CSV outputs
- Optional Streamlit dashboard with upload and synthetic-data modes

## Architecture and data flow

```text
CSV upload or synthetic generator
              ↓
       pandas validation
              ↓
 cleaning → date/month/weekday features
              ↓
 category / month / payment aggregations
              ↓
 CSV reports + charts + insight text
              ↓
       CLI or Streamlit view
```

Input fields: `date`, `category`, `amount`, `payment_method` (optional `description`). The current rule-based category analysis uses the category supplied in the row; it does not claim to infer categories automatically.

## Tech stack choices

| Option | Tools | App/dashboard | Difficulty |
| --- | --- | --- | --- |
| A: Easy | Python, pandas, Matplotlib | No, command-line reports | Beginner |
| B: Recommended | Python, pandas, NumPy, Seaborn, Streamlit | Yes, interactive dashboard | Beginner to intermediate |
| C: Advanced | FastAPI, PostgreSQL, Docker, cloud deployment, forecasting | Web app and API | Intermediate to advanced |

This repository implements Option B, with a CLI analysis path that works independently of the dashboard. The dashboard is optional.

## Project structure

```text
Expense-Tracker-App/
├── data/                 # Sample CSV and generated synthetic input
├── notebooks/            # Space for exploratory notebooks
├── src/                  # Space for future modular source code
├── outputs/              # Cleaned data, summaries, insights (generated)
├── images/               # Charts (generated)
├── main.py               # End-to-end data pipeline and CLI
├── dashboard.py          # Optional Streamlit dashboard
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup and run

Requires Python 3.10 or newer.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then activate again. You can also run `.venv\Scripts\python.exe main.py` without activating.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

CLI options:

```bash
python main.py --months 18 --seed 7 --budget 45000
python main.py --input data/sample_expenses.csv --budget 1000
```

A custom CSV needs these exact fields (case and surrounding spaces are normalized): `date`, `category`, `amount`, `payment_method`. Invalid dates, missing required values, duplicate rows, and zero/negative amounts are removed. The supplied sample has two illustrative rows.

### Run the dashboard

After installing requirements, run `streamlit run dashboard.py` and open the local URL printed in the terminal. Select synthetic data or upload your CSV, set a monthly comparison budget, inspect charts/insights, and expand the table. The dashboard does not persist uploaded data.

## Expected outputs

`python main.py` creates or refreshes:

- `data/synthetic_expenses.csv` — generated input (not created when `--input` is used)
- `outputs/cleaned_expenses.csv`
- `outputs/monthly_summary.csv`, `category_summary.csv`, `payment_summary.csv`, `weekday_summary.csv`
- `outputs/insights.txt`
- `images/category_spending.png`, `monthly_trend.png`, `category_share.png`, `payment_methods.png`

The random seed makes the synthetic sampling reproducible, while generated dates are anchored to the run date. Outputs are excluded from version control only if you choose to add them to `.gitignore`; currently they can be committed as portfolio proof after reviewing them.

## Analysis and simulation walkthrough

1. Generate about 65 random transactions per month across food, transport, rent, utilities, shopping, healthcare, entertainment, and education; synthetic distributions make amounts vary by category.
2. Add a fixed recurring rent transaction for each month.
3. Normalize columns and types, remove invalid records, then derive month, year, and weekday.
4. Aggregate total and transaction count by month, category, payment method, and weekday.
5. Compare monthly totals with the chosen budget. A month over budget is flagged; this is a simple threshold, not a financial recommendation.
6. Save reports, charts, and readable insight statements.

## GitHub upload

Suggested repository name: `expense-tracker-data-science`. Description: `Synthetic expense analysis pipeline and Streamlit dashboard built with Python, pandas, NumPy, and Seaborn.` Suggested topics: `python`, `data-science`, `pandas`, `streamlit`, `data-visualization`, `expense-tracker`.

Create an empty GitHub repository, then from this folder:

```bash
git init
git add .
git commit -m "Build synthetic expense analysis pipeline"
git branch -M main
git remote add origin https://github.com/<YOUR_USERNAME>/expense-tracker-data-science.git
git push -u origin main
```

Follow-up commit examples: `Add budget comparison and monthly insights`, `Add Streamlit dashboard`, `Document setup and sample data`. Do not put credentials or real financial records in Git.


## Interview preparation

1. **What problem does this solve?** It turns individual expense rows into category and time summaries so users can understand spending patterns and compare them with a budget.
2. **Why synthetic data?** It makes the project reproducible without exposing private data. Its patterns are demonstrations and cannot support claims about real populations.
3. **How did you clean the data?** I normalized column names, parsed dates and numeric amounts, removed invalid/missing required values, excluded non-positive spending, and dropped duplicate rows.
4. **Why group by month?** Monthly aggregation reveals changes over time and supports comparison against a monthly budget.
5. **What features did you engineer?** Month, year, and weekday derived from the transaction date.
6. **How is overspending detected?** A monthly total is compared with a user-selected threshold; the result is a flag, not a forecast or financial recommendation.
7. **How would you improve categorization?** Add a reviewed merchant/category mapping first, then consider a supervised classifier only with labeled, representative, privacy-safe data.
8. **What are the limitations?** Synthetic distributions, no income/debt/tax context, simple budget threshold, and no authentication or persistent database.
9. **How would you scale it?** Separate ingestion, validation, storage, analytics, and UI; use a database, access controls, tests, logging, and deployment monitoring.
10. **What would you measure?** Data validity, category coverage, analysis correctness, dashboard usability, and user-relevant outcomes; never claim behavior change without user evidence.

**HR explanation:** “I built a Python expense analysis project that generates privacy-safe synthetic transactions, cleans them, and shows category and monthly spending patterns. It produces reports and a small dashboard, and helped me practice turning raw records into clear business insights.”

**Technical explanation:** “The pipeline uses NumPy for seeded synthetic sampling and pandas for schema validation, cleaning, feature engineering, and groupby aggregations. Matplotlib and Seaborn produce report charts; Streamlit presents the same analysis interactively. Budget comparison is a configurable rule, not a predictive model.”

## Future improvements

- Mobile-friendly entry form and real-time tracking
- Budget alerts and financial goal tracking
- Merchant rules and reviewed category suggestions
- A privacy-conscious database and user authentication
- Forecasting with uncertainty intervals, evaluated on suitable real or carefully simulated data
- Deployment, automated quality checks, and accessibility improvements

## Troubleshooting

- **`ModuleNotFoundError`:** activate `.venv` and run `pip install -r requirements.txt` with that environment's Python.
- **`python` not found on Windows:** try `py main.py`; verify Python is installed and on PATH.
- **PowerShell activation blocked:** use the process-scoped execution policy command above or call `.venv\Scripts\python.exe` directly.
- **Missing CSV columns:** include `date`, `category`, `amount`, and `payment_method`.
- **No valid rows:** inspect dates and amounts; zero or negative amounts are filtered out.
- **Charts do not appear:** they are saved as PNGs in `images/`; open those files or rerun `python main.py`.
- **Streamlit command not found:** activate the virtual environment, install requirements, then use `python -m streamlit run dashboard.py`.

## Scope and responsible use

This is an educational portfolio project, not accounting software or financial advice. It has no authentication, encryption, backup, or production data controls. Use synthetic/example data in public repositories. Before handling real financial records, design and review security, privacy, retention, and consent controls.
