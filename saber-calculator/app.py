import streamlit as st
import numpy as np
import numpy_financial as nf
import math
import pandas as pd
import altair as alt

def generate_debt_schedule(amount, rate, tenor):
    """
    Return a list of constant annual debt service payments for given debt terms.
    """
    payment = nf.pmt(rate, tenor, amount)
    return [-payment] * tenor

st.set_page_config(page_title="Solar PPA Calculator MVP", layout="wide")
st.title("🔋 Solar PPA Calculator MVP")

# --- Sidebar: Input Assumptions ---
st.sidebar.header("Project & Financial Assumptions")
epc = st.sidebar.selectbox("EPC (£/kWp)", [750, 1000, 1250], index=0)
# Manual yield input after EPC selection
yield_per_kwp = st.sidebar.number_input("Yield (kWh per kWp per year)", value=1000.0)
self_consumption = st.sidebar.slider("Self consumption (%)", 0.0, 100.0, 100.0) / 100.0
degradation = st.sidebar.number_input("Output degradation (%/yr)", value=0.5) / 100.0
project_life = st.sidebar.number_input("Project life (years)", min_value=1, value=10)

project_size = st.sidebar.number_input("Project Size (kWp)", value=48.0)
project_cost = st.sidebar.number_input("Project cost (£)", value=epc * project_size)

st.sidebar.header("Annual Costs")
billing_1_3 = st.sidebar.number_input("Billing costs (yrs 1-3, £/yr)", value=400.0)
billing_4p = st.sidebar.number_input("Billing costs (yrs 4+, £/yr)", value=100.0)
o_and_m = st.sidebar.number_input("O&M (£/kWp/yr)", value=10.0)
insurance = st.sidebar.number_input("Insurance (£/kWp/yr)", value=3.75)
business_rates = st.sidebar.number_input("Business rates (£/kWp/yr)", value=1.22)
cont1 = st.sidebar.number_input("Contingency 1 (£/kWh/yr)", value=0.0)
cont2 = st.sidebar.number_input("Contingency 2 (£/project/yr)", value=0.0)

st.sidebar.header("Capex & Maintenance Reserves")
commission_pct = st.sidebar.number_input("Commission cost (% of project cost)", value=6.0) / 100.0

st.sidebar.header("Tariffs & Inflation")
subsidy = st.sidebar.number_input("Generation subsidy (p/kWh)", value=0.0)
export_tariff = st.sidebar.number_input("Export tariff (p/kWh)", value=7.0)
onsite_tariff = st.sidebar.number_input("On-site tariff (p/kWh)", value=18.658)
infl_cost = st.sidebar.number_input("Inflation - costs (%)", value=2.5) / 100.0
infl_export = st.sidebar.number_input("Inflation - export tariff (%)", value=2.5) / 100.0
infl_ppa = st.sidebar.number_input("Inflation - PPA (%)", value=2.5) / 100.0

st.sidebar.header("Financial Structuring")
target_irr = st.sidebar.number_input("Equity IRR target (%)", value=11.0) / 100.0
de_btn = st.sidebar.checkbox("Enable Debt Financing", value=False)
if de_btn:
    debt_amt = st.sidebar.number_input("Debt amount (£)", value=0.0)
    debt_rate = st.sidebar.number_input("Debt interest rate (%)", value=0.0) / 100.0
    debt_tenor = st.sidebar.number_input("Debt tenor (years)", min_value=0, value=0)
else:
    debt_amt = debt_rate = debt_tenor = 0.0

def calculate_cashflows(params):
    yrs = int(params['project_life'])
    infl_cost_factors = [(1 + params['infl_cost']) ** (t) for t in range(yrs)]
    infl_ppa_factors = [(1 + params['infl_ppa']) ** (t) for t in range(yrs)]
    infl_export_factors = [(1 + params['infl_export']) ** (t) for t in range(yrs)]

    initial_outflow = params['project_cost'] * (1 + params['commission_pct'])
    cashflows = [-initial_outflow]
    # Compute total annual energy from per-kWp yield
    annual_energy = params['yield_per_kwp'] * params['project_size']

    for y in range(1, yrs + 1):
        factor = (1 - params['degradation']) ** (y - 1)
        energy = annual_energy * factor

        # Revenue
        if 'ppa_price' in params:
            rev_ppa = (energy * params['self_consumption'] * (params['ppa_price'] / 100) * infl_ppa_factors[y-1])
            rev_export = (energy * (1 - params['self_consumption']) * (params['export_tariff'] / 100) * infl_export_factors[y-1])
            rev_subsidy = (energy * (params['subsidy'] / 100) * infl_export_factors[y-1])
            rev_total = rev_ppa + rev_export + rev_subsidy
        else:
            rev_onsite = (energy * params['self_consumption'] * (params['onsite_tariff'] / 100) * infl_ppa_factors[y-1])
            rev_export = (energy * (1 - params['self_consumption']) * (params['export_tariff'] / 100) * infl_export_factors[y-1])
            rev_total = rev_onsite + rev_export + energy * (params['subsidy'] / 100) * infl_export_factors[y-1]

        # Costs
        cost = ((params['o_and_m'] + params['insurance'] + params['business_rates']) * params['project_size'] * infl_cost_factors[y-1])
        cost += (params['billing_1_3'] if y <= 3 else params['billing_4p']) * infl_cost_factors[y-1]
        cost += params['cont1'] * energy * infl_cost_factors[y-1]
        cost += params['cont2'] * infl_cost_factors[y-1]

        net = rev_total - cost
        cashflows.append(net)

    if params.get('debt_enabled') and params.get('debt_tenor', 0) > 0:
        debt_schedule = generate_debt_schedule(params['debt_amt'], params['debt_rate'], params['debt_tenor'])
        for year in range(1, min(len(cashflows), params['debt_tenor'] + 1)):
            cashflows[year] -= debt_schedule[year-1]

    return cashflows

def build_params():
    return {
        'epc': epc,
        'yield_per_kwp': yield_per_kwp,
        'project_size': project_size,
        'self_consumption': self_consumption,
        'degradation': degradation,
        'project_life': project_life,
        'billing_1_3': billing_1_3,
        'billing_4p': billing_4p,
        'o_and_m': o_and_m,
        'insurance': insurance,
        'business_rates': business_rates,
        'cont1': cont1,
        'cont2': cont2,
        'subsidy': subsidy,
        'export_tariff': export_tariff,
        'onsite_tariff': onsite_tariff,
        'infl_cost': infl_cost,
        'infl_export': infl_export,
        'infl_ppa': infl_ppa,
        'project_cost': project_cost,
        'commission_pct': commission_pct,
        'debt_enabled': de_btn,
        'debt_amt': debt_amt,
        'debt_rate': debt_rate,
        'debt_tenor': debt_tenor,
        'target_irr': target_irr
    }

params = build_params()
cfs = calculate_cashflows(params)
irr = nf.irr(cfs)
npv = nf.npv(0.0, cfs)

def solve_ppa_price(params):
    yrs = int(params['project_life'])
    dp = params['target_irr']

    cost_infl = [(1 + params['infl_cost']) ** (t - 1) for t in range(1, yrs+1)]
    # PPA price is constant nominal, so remove ppa_infl
    exp_infl = [(1 + params['infl_export']) ** (t - 1) for t in range(1, yrs+1)]

    initial_outflow = params['project_cost'] * (1 + params['commission_pct'])
    npv_no_ppa = -initial_outflow
    denom = 0.0

    for t in range(1, yrs+1):
        df = 1 / (1 + dp) ** t
        E = params['yield_per_kwp'] * params['project_size'] * (1 - params['degradation']) ** (t - 1)
        rev_export = E * (1 - params['self_consumption']) * (params['export_tariff'] / 100) * exp_infl[t-1]
        rev_subsidy = E * (params['subsidy'] / 100) * exp_infl[t-1]

        annual_cost = ((params['o_and_m'] + params['insurance'] + params['business_rates']) * params['project_size'] * cost_infl[t-1])
        annual_cost += (params['billing_1_3'] if t <= 3 else params['billing_4p']) * cost_infl[t-1]
        annual_cost += params['cont1'] * E * cost_infl[t-1]
        annual_cost += params['cont2'] * cost_infl[t-1]

        cf_no_ppa = rev_export + rev_subsidy - annual_cost
        npv_no_ppa += cf_no_ppa * df
        # PPA price is constant nominal, no inflation applied
        denom += E * params['self_consumption'] * (1/100) * df

    if denom <= 0:
        return None
    return -npv_no_ppa / denom

try:
    ppa_price = solve_ppa_price(params)
except:
    ppa_price = None

# Main display
col1, col2 = st.columns(2)
with col1:
    st.subheader("Cash Flow Schedule")
    years = list(range(len(cfs)))
    # Build a DataFrame for clearer axis labeling
    df_cf = pd.DataFrame({'Cash Flow (£)': cfs}, index=years)
    df_cf.index.name = 'Year'
    # Compute cumulative cashflows and identify break-even
    df_cf['Cumulative'] = df_cf['Cash Flow (£)'].cumsum()
    be_years = df_cf.index[df_cf['Cumulative'] >= 0]
    if len(be_years) > 0:
        be_year = be_years[0]
        st.markdown(f"**Break-even occurs in Year {be_year}**")
    else:
        st.markdown("**No break-even within project life**")
    # Plot operating cashflows with break-even marker
    df_op = df_cf.iloc[1:].reset_index()
    base = alt.Chart(df_op).mark_line(point=True).encode(
        x='Year:O',
        y=alt.Y('Cash Flow (£):Q', title='Cash Flow (£)')
    )
    if len(be_years) > 0:
        rule = alt.Chart(pd.DataFrame({'Year': [be_year]})).mark_rule(color='red').encode(x='Year:O')
        chart = alt.layer(base, rule).properties(title='Operating Cash Flows with Break-even')
    else:
        chart = base.properties(title='Operating Cash Flows')
    st.altair_chart(chart, use_container_width=True)
    # st.subheader("Operating Cash Flows (Years 1+)")
    # st.line_chart(df_cf.iloc[1:])
    st.subheader("Cumulative Cash Flow")
    st.line_chart(df_cf['Cumulative'])
    # Show full schedule for reference
    st.subheader("Full Cash Flow Schedule")
    st.dataframe(df_cf)
with col2:
    st.subheader("Summary Results")
    st.metric("IRR", f"{irr*100:.2f}%")
    st.metric("NPV", f"£{npv:,.2f}")
    st.metric("PPA Price (p/kWe)", f"{ppa_price:.2f}" if ppa_price is not None else "N/A")

# Term Length Scenario Comparison
st.header("Term Length Scenario Comparison")
scenarios = [10, 15, 20, 25]
results = []
for term in scenarios:
    p = params.copy()
    p['project_life'] = term
    c = calculate_cashflows(p)
    irr_val = nf.irr(c)
    npv_val = nf.npv(0.0, c)
    ppa_val = solve_ppa_price(p)
    results.append({
        "Term (yrs)": term,
        "IRR (%)": f"{irr_val*100:.2f}",
        "NPV (£)": f"£{npv_val:,.2f}",
        "PPA Price (p/kWe)": f"{ppa_val:.2f}" if ppa_val is not None else "N/A"
    })
st.table(results)
