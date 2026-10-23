"""Optional interactive dashboard. Run with: streamlit run dashboard.py"""
import pandas as pd
import streamlit as st
from main import DATA_DIR, IMAGE_DIR, OUTPUT_DIR, add_features, analyze, build_insights, clean_expenses, generate_expenses

st.set_page_config(page_title="Expense Tracker", page_icon="💸", layout="wide")
st.title("💸 Expense Tracker App")
st.caption("Synthetic data demonstration. Do not enter real sensitive financial information.")
budget = st.sidebar.number_input("Monthly budget", min_value=1, value=50000, step=1000)
source = st.sidebar.radio("Data source", ["Generate synthetic data", "Upload CSV"])
if source == "Upload CSV":
    upload = st.sidebar.file_uploader("CSV: date, category, amount, payment_method", type="csv")
    if upload is None:
        st.info("Upload a CSV to explore it, or select synthetic data."); st.stop()
    raw = pd.read_csv(upload)
else:
    months = st.sidebar.slider("Months of history", 3, 24, 12)
    raw = generate_expenses(months=months)
try:
    df = add_features(clean_expenses(raw))
except (ValueError, Exception) as error:
    st.error(f"Could not process this data: {error}"); st.stop()
if df.empty:
    st.warning("No valid transactions found."); st.stop()
results = analyze(df, budget)
col1, col2, col3 = st.columns(3)
col1.metric("Total spend", f"{df.amount.sum():,.0f}")
col2.metric("Transactions", f"{len(df):,}")
col3.metric("Average monthly spend", f"{results['monthly'].total_spend.mean():,.0f}")
left, right = st.columns(2)
with left:
    st.subheader("Monthly trend")
    st.line_chart(results["monthly"].set_index("month")[["total_spend", "budget"]])
with right:
    st.subheader("Category spending")
    st.bar_chart(results["category"].set_index("category")["total_spend"])
st.subheader("Insights")
for insight in build_insights(df, results, budget):
    st.write("• " + insight)
with st.expander("Transaction data"):
    st.dataframe(df, use_container_width=True)
