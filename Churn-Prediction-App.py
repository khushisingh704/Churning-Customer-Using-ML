# ==========================================================
# CUSTOMER CHURN ANALYTICS DASHBOARD + PREDICTION APP
# Professional Style with Business POV
# ==========================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import pickle

# ----------------------------------------------------------
# PAGE CONFIGURATION
# ----------------------------------------------------------
st.set_page_config(
    page_title="Customer Churn Analytics",
    page_icon="📊",
    layout="wide"
)

# ----------------------------------------------------------
# LOAD FILES
# ----------------------------------------------------------
model = pickle.load(open("model.sav", "rb"))

raw_df = pd.read_csv("CustChurn.csv")
raw_df.columns = raw_df.columns.str.strip()   # remove hidden spaces

dummy_df = pd.read_csv("tel_churn.csv")

# remove unwanted column if exists
if "Unnamed: 0" in dummy_df.columns:
    dummy_df = dummy_df.drop("Unnamed: 0", axis=1)

# ----------------------------------------------------------
# TITLE
# ----------------------------------------------------------
st.title("📊 Customer Churn Analytics Dashboard")
st.markdown("### Business Retention Intelligence & Customer Risk Prediction")

# ==========================================================
# KPI SECTION (FIXED)
# ==========================================================
total_customers = len(raw_df)

# safer churn rate calculation
churn_rate = round(
    (
        raw_df["Churn"]
        .astype(str)
        .str.strip()
        .str.lower()
        .eq("yes")
        .sum()
        / total_customers
    ) * 100,
    2
)

avg_monthly = round(raw_df["MonthlyCharges"].mean(), 2)
avg_tenure = round(raw_df["tenure"].mean(), 1)

k1, k2, k3, k4 = st.columns(4)

k1.metric("👥 Total Customers", total_customers)
k2.metric("⚠️ Churn Rate", f"{churn_rate}%")
k3.metric("💰 Avg Monthly Charges", f"${avg_monthly}")
k4.metric("📅 Avg Tenure", avg_tenure)

st.markdown("---")

# ==========================================================
# BUSINESS CHARTS
# ==========================================================
c1, c2, c3 = st.columns(3)

# Contract vs Churn
with c1:
    fig1 = px.histogram(
        raw_df,
        x="Contract",
        color="Churn",
        barmode="group",
        title="Churn by Contract Type"
    )
    st.plotly_chart(fig1, use_container_width=True)

# Payment Method
with c2:
    fig2 = px.histogram(
        raw_df,
        x="PaymentMethod",
        color="Churn",
        title="Churn by Payment Method"
    )
    fig2.update_layout(xaxis_tickangle=-30)
    st.plotly_chart(fig2, use_container_width=True)

# Internet Service
with c3:
    fig3 = px.histogram(
        raw_df,
        x="InternetService",
        color="Churn",
        title="Churn by Internet Service"
    )
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# ==========================================================
# ADD THIS SECTION AFTER BUSINESS CHARTS
# (place below: st.markdown("---") after charts)
# ==========================================================

st.subheader("Key Business Insights")

st.info("""
• Month-to-month contract customers show the highest churn risk compared to long-term contracts.

• Customers using Electronic Check payment mode are more likely to churn than auto-payment users.

• Higher monthly charge customers tend to leave more frequently, indicating price sensitivity.

• Customers with low tenure are at greater churn risk than long-term loyal customers.

• Two-year contract customers demonstrate the strongest retention and stability.
""")

st.markdown("---")
# ==========================================================
# PREDICTION FORM
# ==========================================================
st.subheader("🔍 Predict Customer Churn Risk")

col1, col2, col3 = st.columns(3)

with col1:
    gender = st.selectbox("Gender", ["Male", "Female"])
    senior = st.selectbox("Senior Citizen", [0, 1])
    partner = st.selectbox("Partner", ["Yes", "No"])
    dependents = st.selectbox("Dependents", ["Yes", "No"])

with col2:
    tenure = st.slider("Tenure (Months)", 1, 72, 12)
    monthly = st.slider("Monthly Charges", 18, 120, 70)
    total = st.number_input("Total Charges", 0.0, 10000.0, 1000.0)

with col3:
    contract = st.selectbox("Contract", ["Month-to-month", "One year", "Two year"])
    paperless = st.selectbox("Paperless Billing", ["Yes", "No"])
    payment = st.selectbox(
        "Payment Method",
        [
            "Electronic check",
            "Mailed check",
            "Bank transfer (automatic)",
            "Credit card (automatic)"
        ]
    )

# ==========================================================
# PREPARE INPUT DATA
# ==========================================================
if st.button("Predict Churn"):

    input_df = pd.DataFrame(columns=dummy_df.drop("Churn", axis=1).columns)
    input_df.loc[0] = 0

    # numerical columns
    input_df["SeniorCitizen"] = senior
    input_df["MonthlyCharges"] = monthly
    input_df["TotalCharges"] = total

    # gender
    if gender == "Male":
        input_df["gender_Male"] = 1
    else:
        input_df["gender_Female"] = 1

    # partner
    if f"Partner_{partner}" in input_df.columns:
        input_df[f"Partner_{partner}"] = 1

    # dependents
    if f"Dependents_{dependents}" in input_df.columns:
        input_df[f"Dependents_{dependents}"] = 1

    # contract
    if f"Contract_{contract}" in input_df.columns:
        input_df[f"Contract_{contract}"] = 1

    # billing
    if f"PaperlessBilling_{paperless}" in input_df.columns:
        input_df[f"PaperlessBilling_{paperless}"] = 1

    # payment
    if f"PaymentMethod_{payment}" in input_df.columns:
        input_df[f"PaymentMethod_{payment}"] = 1

    # tenure groups
    if tenure <= 12 and "tenure_group_1 - 12" in input_df.columns:
        input_df["tenure_group_1 - 12"] = 1
    elif tenure <= 24 and "tenure_group_13 - 24" in input_df.columns:
        input_df["tenure_group_13 - 24"] = 1
    elif tenure <= 36 and "tenure_group_25 - 36" in input_df.columns:
        input_df["tenure_group_25 - 36"] = 1
    elif tenure <= 48 and "tenure_group_37 - 48" in input_df.columns:
        input_df["tenure_group_37 - 48"] = 1
    elif tenure <= 60 and "tenure_group_49 - 60" in input_df.columns:
        input_df["tenure_group_49 - 60"] = 1
    elif "tenure_group_61 - 72" in input_df.columns:
        input_df["tenure_group_61 - 72"] = 1

    # prediction
    pred = model.predict(input_df)[0]

    st.markdown("---")

    if pred == 1:
        st.error("⚠️ High Churn Risk Customer")

        st.markdown("""
        ### Business Retention Action Plan:
        - Offer annual contract discount  
        - Provide loyalty cashback  
        - Assign retention support executive  
        - Reduce billing friction  
        """)

    else:
        st.success(" Low Churn Risk Customer")

        st.markdown("""
        ### Growth Opportunity:
        - Upsell premium plans  
        - Cross-sell OTT bundles  
        - Refer-a-friend offers  
        """)
