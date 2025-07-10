import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Kitchen Level P&L Dashboard", layout="wide")

import os
st.write("Files in app directory:", os.listdir())

# Load and clean data
@st.cache_data
def load_data():
    df = pd.read_excel("KitchenPNLData.xlsx", header=1)  # or header=0 to test
    st.write("🧾 Original Columns:", df.columns.tolist())  # show real names
    
    # Clean the column names
    df.columns = df.columns.str.strip().str.upper().str.replace(" ", "_")
    st.write("📦 Cleaned Columns:", df.columns.tolist())  # confirm after cleanup

    # Check if 'MONTH' exists after cleanup
    if 'MONTH' not in df.columns:
        st.error("❌ 'MONTH' column not found after cleaning.")
        st.stop()
    
    # Now convert
    df['MONTH'] = pd.to_datetime(df['MONTH'], errors='coerce').dt.strftime('%b %Y')
    return df


df = load_data()

st.title("📊 Kitchen Level P&L Dashboard")

st.slider("Kitchen EBITDA", float(df["KITCHEN_EBITDA"].min()), float(df["KITCHEN_EBITDA"].max()), (float(df["KITCHEN_EBITDA"].min()), float(df["KITCHEN_EBITDA"].max())))

with st.expander("🔍 Filters", expanded=False):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        store = st.multiselect("Store", options=sorted(df["STORE"].dropna().unique()), default=sorted(df["STORE"].dropna().unique()))
    with col2:
        cm_cohort = st.multiselect("CM Cohort", options=df["CM_COHORT"].dropna().unique(), default=df["CM_COHORT"].dropna().unique())
    with col3:
        ebitda_category = st.multiselect("EBITDA Category", options=df["EBITDA_CATEGORY"].dropna().unique(), default=df["EBITDA_CATEGORY"].dropna().unique())
    with col4:
        ebitda_cohort = st.multiselect("EBITDA Cohort", options=df["EBITDA_COHORT"].dropna().unique(), default=df["EBITDA_COHORT"].dropna().unique())

    col5, col6, col7, col8 = st.columns(4)
    with col5:
        revenue_cohort = st.multiselect("Revenue Cohort", options=df["REVENUE_COHORT"].dropna().unique(), default=df["REVENUE_COHORT"].dropna().unique())
    with col6:
        month = st.multiselect("Month", options=sorted(df["MONTH"].dropna().unique()), default=sorted(df["MONTH"].dropna().unique()))
    with col7:
        gm_percent = st.slider("Gross Margin", float(df["GROSS_MARGIN"].min()), float(df["GROSS_MARGIN"].max()), (float(df["GROSS_MARGIN"].min()), float(df["GROSS_MARGIN"].max())))
    with col8:
        net_revenue = st.slider("Net Revenue", float(df["NET_REVENUE"].min()), float(df["NET_REVENUE"].max()), (float(df["NET_REVENUE"].min()), float(df["NET_REVENUE"].max())))

# Apply Filters to Dataset
filtered_df = df[
    (df["STORE"].isin(store)) &
    (df["GROSS_MARGIN"].between(gm_percent[0], gm_percent[1])) &
    (df["NET_REVENUE"].between(net_revenue[0], net_revenue[1])) &
    (df["MONTH"].isin(month)) &
    (df["REVENUE_COHORT"].isin(revenue_cohort)) &
    (df["CM_COHORT"].isin(cm_cohort)) &
    (df["EBITDA_CATEGORY"].isin(ebitda_category)) &
    (df["EBITDA_COHORT"].isin(ebitda_cohort))
]


line_data = filtered_df.groupby("MONTH")[["NET_REVENUE", "GROSS_MARGIN", "KITCHEN_EBITDA"]].sum().reset_index()
fig_line = px.line(line_data, x="MONTH", y=["NET_REVENUE", "GROSS_MARGIN", "KITCHEN_EBITDA"], title="📈 Monthly Trend: Revenue, Margin, EBITDA")
st.plotly_chart(fig_line, use_container_width=True)

fig_pie = px.pie(filtered_df, names="EBITDA_CATEGORY", title="🧩 EBITDA Category Distribution")
st.plotly_chart(fig_pie, use_container_width=True)

store_perf = filtered_df.groupby("STORE")[["NET_REVENUE"]].sum().reset_index()
fig_bar = px.bar(store_perf, x="STORE", y="NET_REVENUE", title="🏪 Store-wise Net Revenue")
st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("### 📋 Filtered Kitchen Snapshot")
st.dataframe(filtered_df[["STORE", "MONTH", "NET_REVENUE", "GROSS_MARGIN", "KITCHEN_EBITDA"]])

st.success("Tada, this is my first dashboard!")
