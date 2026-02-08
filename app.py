import streamlit as st
import pandas as pd
from io import BytesIO

from inputs import validate_user_inputs
from assumption_generator import generate_assumptions
from case_constructor import build_cases
from lbo_engine import run_lbo_case
from sensitivity_analysis import sensitivity_analysis

from exporter import convert_to_excel

st.set_page_config(page_title="AI-assisted LBO Model", layout="wide")

st.title("AI-assisted LBO Model")

# SECTION 1: USER INPUTS
st.header("1. Deal Inputs")
st.markdown("Provide the financial and contextual details for the LBO model below.")

with st.form("deal_inputs"):
    col1, col2, col3 = st.columns(3)

    with col1:
        revenue = st.number_input("Revenue", min_value=0.0, value=1200.0, help="Current annual revenue in millions.")
        ebitda = st.number_input("EBITDA", min_value=0.0, value=150.0, help="Earnings before interest, taxes, depreciation, and amortization.")
        da = st.number_input("Depreciation & Amortization", min_value=0.0, value=30.0, help="Annual D&A expense.")

    with col2:
        capex = st.number_input("CapEx", min_value=0.0, value=40.0, help="Annual capital expenditures.")
        tax_rate = st.number_input("Tax Rate (0–1)", min_value=0.0, max_value=1.0, value=0.25, help="Effective corporate tax rate as a decimal.")
        debt_pct = st.number_input("Debt % (0–1)", min_value=0.0, max_value=1.0, value=0.6, help="Percentage of enterprise value financed by debt.")

    with col3:
        interest_rate = st.number_input("Interest Rate (0–1)", min_value=0.0, max_value=1.0, value=0.10, help="Annual interest rate on debt as a decimal.")
        hold_period = st.number_input("Hold Period (Years)", min_value=1, value=5, help="Number of years the investment is held.")
        industry = st.text_input("Industry", value="Healthcare", help="Company's primary industry.")
        geography = st.text_input("Geography", value="India", help="Primary operating region.")

    submitted = st.form_submit_button("Generate LBO")


# RUN MODEL
if submitted:
    user_inputs = {
        "revenue": revenue,
        "ebitda": ebitda,
        "depreciation_amortization": da,
        "capex": capex,
        "tax_rate": tax_rate,
        "debt_percentage": debt_pct,
        "interest_rate": interest_rate,
        "hold_period_years": hold_period,
        "industry": industry,
        "geography": geography,
    }

    # VALIDATE INPUTS
    with st.spinner("Validating inputs..."):
        try:
            validate_user_inputs(user_inputs)
        except ValueError as e:
            st.error(f"Input Error: {str(e)}")
            st.stop()

    st.success("Inputs validated successfully.")

    # SECTION 2: AI ASSUMPTIONS
    st.header("2. AI-Generated Assumptions")

    with st.spinner("Generating AI assumptions..."):
        ai_assumptions = generate_assumptions(user_inputs)

    st.subheader("Assumption Ranges by Case")
    cols = st.columns(3)
    cases_list = ["downside", "base", "upside"]
    for i, case in enumerate(cases_list):
        with cols[i]:
            st.markdown(f"**{case.capitalize()} Case**")
            st.metric("Entry Multiple Range", f"{ai_assumptions['entry_multiple'][case][0]} - {ai_assumptions['entry_multiple'][case][1]}")
            st.metric("Revenue Growth (%) Range", f"{ai_assumptions['revenue_growth'][case][0]} - {ai_assumptions['revenue_growth'][case][1]}")
            st.metric("Exit Multiple Range", f"{ai_assumptions['exit_multiple'][case][0]} - {ai_assumptions['exit_multiple'][case][1]}")
            st.metric("Margin Change (bps)", ai_assumptions["margin_change_bps"][case])

    st.metric("AI Confidence Level", ai_assumptions["confidence"])

    with st.expander("View Raw AI Assumptions (JSON)"):
        st.json(ai_assumptions)

    # CASE CONSTRUCTION
    with st.spinner("Building cases..."):
        cases = build_cases(ai_assumptions)

    # SECTION 3: LBO RESULTS
    st.header("3. LBO Results")
    st.markdown("Key metrics for each scenario based on the LBO engine.")

    all_results = {} # To store for Excel export
    cols = st.columns(3)
    for idx, case_name in enumerate(["downside", "base", "upside"]):
        with st.spinner(f"Running {case_name.capitalize()} case..."):
            results = run_lbo_case(user_inputs, cases[case_name])
            all_results[case_name] = results
        with cols[idx]:
            st.subheader(case_name.capitalize())
            st.metric("IRR (%)", f"{results['irr']}%")
            st.metric("Money Multiple", f"{results['money_multiple']}x")
            with st.expander("Detailed Results"):
                st.write(f"Entry Equity: {results['entry_equity']:.2f}")
                st.write(f"Exit Equity: {results['exit_equity']:.2f}")

    # SECTION 4: SENSITIVITY ANALYSIS
    st.header("4. Sensitivity Analysis (Base Case)")
    st.markdown("One-way sensitivities showing IRR impact from varying key assumptions.")

    with st.spinner("Running sensitivity analysis..."):
        sensitivities = sensitivity_analysis(user_inputs, cases["base"])

    for variable, table in sensitivities.items():
        st.subheader(variable.replace("_", " ").title())
        sorted_table = sorted(table.items(), key=lambda x: x[0])
        st.table([{"Assumption": k, "IRR (%)": v} for k, v in sorted_table])

    
    st.divider()
    st.header("5. Export Model")
    
    with st.spinner("Preparing Excel file..."):
        excel_data = convert_to_excel(user_inputs, ai_assumptions, all_results)
        
    st.download_button(
        label="📥 Download Full LBO Model (Excel)",
        data=excel_data,
        file_name=f"LBO_Model_{industry}_{geography}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        help="Click to download all assumptions and results in a formatted Excel file."
    )