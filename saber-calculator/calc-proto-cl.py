import streamlit as st
import pandas as pd
import numpy as np
import numpy_financial as npf
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import io
from io import BytesIO
import hashlib
import base64

# Page config
st.set_page_config(
    page_title="Saber PPA Calculator | Saber Renewable Energy",
    page_icon="💚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Function to render Saber logo
def render_saber_logo():
    logo_svg = '''<svg id="Layer_1" data-name="Layer 1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="60" height="60">
  <defs>
    <style>
      .cls-1 {
        fill: #7dbf61;
      }
      .cls-2 {
        fill: #fff;
      }
    </style>
  </defs>
  <path class="cls-2" d="M9.03,8.34c-2.01-1.18-4.59-.48-5.77,1.53-1.18,2.01-.48,4.59,1.53,5.77,1.66.96,3.76.7,5.11-.66l5.29-5.29c1.14-.92,2.75-.92,3.89.04l-7.17,7.17c-2.75,2.71-7.17,2.71-9.88,0-2.71-2.75-2.71-7.17,0-9.88,2.36-2.45,6.21-2.75,8.96-.7l-2.01,2.01h.04Z"/>
  <path class="cls-1" d="M14.89,15.59c2.01,1.18,4.59.48,5.77-1.53s.48-4.59-1.53-5.77c-1.66-.96-3.76-.7-5.11.66l-5.29,5.29c-1.14.92-2.75.92-3.89-.04l7.26-7.17c2.75-2.71,7.17-2.71,9.88,0,2.71,2.75,2.71,7.17,0,9.88s-6.3,2.71-9.05.7l2.01-2.01h-.04Z"/>
</svg>'''
    return logo_svg

# Saber Brand CSS - Dark theme matching screenshot
st.markdown("""
<style>
    /* Import brand fonts */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@600;800&family=Source+Sans+Pro:wght@400;600&display=swap');
    
    /* Root variables */
    :root {
        --saber-blue: #044D73;
        --saber-green: #7CC061;
        --saber-dark-blue: #091922;
        --saber-dark-fade: #0d1138;
        --saber-dark-green: #0A2515;
        --saber-text-light: #FFFFFF;
        --saber-text-gray: #B0B0B0;
        --dark-input-bg: #1E1E1E;
        --dark-card-bg: #2A2A2A;
    }
    
    /* Dark theme background */
    .stApp {
        background: linear-gradient(135deg, #091922 0%, #0d1138 100%);
        color: white;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Header section */
    .header-section {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
    }
    
    .logo-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    
    .company-name {
        font-family: 'Montserrat', sans-serif;
        font-size: 36px;
        font-weight: 800;
        color: white;
        letter-spacing: -0.5px;
    }
    
    /* Tagline */
    .tagline {
        font-family: 'Source Sans Pro', sans-serif;
        font-size: 14px;
        font-weight: 400;
        color: var(--saber-green);
        text-align: center;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }
    
    /* Main header */
    .main-header {
        font-family: 'Montserrat', sans-serif;
        font-size: 32px;
        font-weight: 600;
        color: white;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .sub-text {
        font-family: 'Source Sans Pro', sans-serif;
        font-size: 16px;
        color: var(--saber-text-gray);
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Project Configuration Section */
    .project-config-section {
        background: linear-gradient(135deg, var(--saber-blue) 0%, var(--saber-dark-fade) 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .section-title {
        font-family: 'Montserrat', sans-serif;
        font-size: 24px;
        font-weight: 600;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Input styling for dark theme */
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        background-color: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
        border-radius: 6px;
    }
    
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: var(--saber-green);
        box-shadow: 0 0 0 2px rgba(124, 192, 97, 0.3);
    }
    
    /* Labels */
    .stNumberInput > label,
    .stSelectbox > label,
    .stCheckbox > label {
        color: white !important;
        font-family: 'Source Sans Pro', sans-serif;
        font-weight: 600;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: var(--saber-green);
        color: white;
        font-family: 'Montserrat', sans-serif;
        font-weight: 600;
        border-radius: 6px;
        border: none;
        padding: 0.75rem 2rem;
        font-size: 16px;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        background-color: #6BAF50;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(124, 192, 97, 0.4);
    }
    
    /* Metrics styling */
    [data-testid="metric-container"] {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    
    [data-testid="metric-container"] [data-testid="metric-label"] {
        color: var(--saber-text-gray) !important;
        font-family: 'Source Sans Pro', sans-serif;
        font-size: 14px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: white !important;
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        font-size: 28px;
    }
    
    [data-testid="metric-container"] [data-testid="metric-delta"] {
        color: var(--saber-green) !important;
    }
    
    /* Info boxes */
    .stAlert {
        background-color: rgba(124, 192, 97, 0.1);
        border: 1px solid rgba(124, 192, 97, 0.3);
        color: white;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent;
        gap: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.05);
        color: white;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-family: 'Montserrat', sans-serif;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--saber-green);
        color: white;
    }
    
    /* Access badge */
    .access-badge {
        display: inline-block;
        padding: 0.5rem 1.5rem;
        border-radius: 20px;
        font-family: 'Source Sans Pro', sans-serif;
        font-weight: 600;
        font-size: 14px;
        text-align: center;
        margin: 1rem auto;
        letter-spacing: 0.5px;
    }
    
    .partner-badge {
        background-color: rgba(124, 192, 97, 0.2);
        color: var(--saber-green);
        border: 1px solid var(--saber-green);
    }
    
    .internal-badge {
        background-color: rgba(68, 77, 115, 0.2);
        color: #A0A0FF;
        border: 1px solid #A0A0FF;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.05);
        color: white;
        border-radius: 8px;
        font-family: 'Montserrat', sans-serif;
        font-weight: 600;
    }
    
    /* Results section */
    .results-header {
        font-family: 'Montserrat', sans-serif;
        font-size: 28px;
        font-weight: 600;
        color: white;
        margin: 2rem 0 1rem 0;
    }
    
    /* Plot backgrounds */
    .js-plotly-plot {
        background-color: transparent !important;
    }
    
    /* Checkbox */
    .stCheckbox > div > label {
        color: white !important;
    }
    
    /* Help text */
    .stNumberInput > div > div > div > small,
    .stSelectbox > div > div > small {
        color: var(--saber-text-gray) !important;
    }
    
    /* Column gaps */
    [data-testid="column"] {
        padding: 0 0.5rem;
    }
    
    /* Generation info boxes */
    .generation-info {
        background-color: rgba(124, 192, 97, 0.1);
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid rgba(124, 192, 97, 0.3);
        margin-top: 1rem;
        text-align: center;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'calculated' not in st.session_state:
    st.session_state.calculated = False
    st.session_state.results = {}
    st.session_state.access_mode = 'partner'
    st.session_state.authenticated = False
    st.session_state.use_kw = False

# Simple authentication
def check_password(password):
    # correct_password_hash = hashlib.sha256("SaberInternal2025".encode()).hexdigest()
    # entered_password_hash = hashlib.sha256(password.encode()).hexdigest()
    # return entered_password_hash == correct_password_hash
    return password == ""

# Header section
st.markdown('<div class="header-section">', unsafe_allow_html=True)

# Logo and company name
st.markdown(f'''
<div class="logo-container">
    {render_saber_logo()}
    <span class="company-name">SABER</span>
</div>
''', unsafe_allow_html=True)

# Tagline
st.markdown('<p class="tagline">Powerfully Engineered. Clearly Explained.</p>', unsafe_allow_html=True)

# Main header
st.markdown('<h1 class="main-header">Solar PPA Calculator</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">Your Path to Sustainable Profitability</p>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Access mode toggle
col1, col2, col3 = st.columns([5, 1, 1])
with col3:
    if st.button("🔐", help="Internal access", key="login_btn"):
        st.session_state.show_login = not getattr(st.session_state, 'show_login', False)

# Login dialog
if getattr(st.session_state, 'show_login', False):
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### Internal Access")
            password = st.text_input("Password", type="password", key="password_input")
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Login", type="primary", width="stretch"):
                    if check_password(password):
                        st.session_state.access_mode = 'internal'
                        st.session_state.authenticated = True
                        st.session_state.show_login = False
                        st.rerun()
                    else:
                        st.error("Incorrect password")
            with col_b:
                if st.button("Cancel", width="stretch"):
                    st.session_state.show_login = False
                    st.rerun()

# Access mode badge
if st.session_state.access_mode == 'partner':
    st.markdown('<div style="text-align: center;"><span class="access-badge partner-badge">🤝 PARTNER ACCESS</span></div>', unsafe_allow_html=True)
else:
    st.markdown('<div style="text-align: center;"><span class="access-badge internal-badge">🔓 INTERNAL ACCESS</span></div>', unsafe_allow_html=True)

# Project Configuration Section
st.markdown('<div class="project-config-section">', unsafe_allow_html=True)
st.markdown('<h2 class="section-title">Project Configuration</h2>', unsafe_allow_html=True)

# Primary inputs
col1, col2, col3, col4 = st.columns(4)

with col1:
    # Unit toggle
    st.session_state.use_kw = st.checkbox("Use kW instead of MW", value=st.session_state.use_kw, help="Check for smaller projects")
    
    if st.session_state.use_kw:
        capacity_kw = st.number_input(
            "System Capacity (kW DC)",
            min_value=1.0,
            max_value=50000.0,
            value=100.0,
            step=1.0,
            help="Total DC capacity of the solar installation"
        )
        capacity_mw = capacity_kw / 1000
    else:
        capacity_mw = st.number_input(
            "System Capacity (MW DC)",
            min_value=0.001,
            max_value=50.0,
            value=5.0,
            step=0.01,
            help="Total DC capacity of the solar installation"
        )

with col2:
    annual_yield = st.number_input(
        "Annual Yield (kWh/kWp)",
        min_value=700,
        max_value=1200,
        value=950,
        step=10,
        help="Expected annual energy yield per kWp installed"
    )

with col3:
    project_life = st.selectbox(
        "PPA Term (years)",
        options=[10, 15, 20, 25, 30],
        index=2,
        help="Length of the Power Purchase Agreement"
    )

with col4:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⚡ Calculate PPA Price", type="primary", width="stretch"):
        st.session_state.calculated = True

# Generation info
annual_generation_mwh = capacity_mw * annual_yield
annual_generation_kwh = annual_generation_mwh * 1000
capacity_factor = annual_generation_mwh/(capacity_mw*8760)*100

col1, col2 = st.columns(2)
with col1:
    if st.session_state.use_kw:
        st.markdown(f'<div class="generation-info">📊 Annual Generation: {annual_generation_kwh:,.0f} kWh</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="generation-info">📊 Annual Generation: {annual_generation_mwh:,.0f} MWh</div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="generation-info">⚙️ Capacity Factor: {capacity_factor:.1f}%</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Advanced settings
if st.session_state.access_mode == 'internal':
    st.markdown('<h2 style="color: white; font-family: \'Montserrat\', sans-serif; font-weight: 600; margin-top: 2rem;">Financial Parameters</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Capital Costs**")
        if st.session_state.use_kw:
            epc_cost_per_kw = st.number_input(
                "EPC Cost (£/kW)",
                min_value=100,
                max_value=2000,
                value=750,
                step=10,
                format="%d"
            )
            epc_cost = epc_cost_per_kw * 1000
        else:
            epc_cost = st.number_input(
                "EPC Cost (£/MW)",
                min_value=100000,
                max_value=1000000,
                value=750000,
                step=10000,
                format="%d"
            )
        
        st.markdown("**Operating Costs**")
        if st.session_state.use_kw:
            om_cost_per_kw = st.number_input(
                "O&M Cost (£/kW/year)",
                min_value=5,
                max_value=50,
                value=10,
                step=1,
                format="%d"
            )
            om_cost = om_cost_per_kw * 1000
        else:
            om_cost = st.number_input(
                "O&M Cost (£/MW/year)",
                min_value=5000,
                max_value=20000,
                value=10000,
                step=1000,
                format="%d"
            )
        
        insurance_rate = st.number_input(
            "Insurance (% of CAPEX/year)",
            min_value=0.1,
            max_value=1.0,
            value=0.25,
            step=0.05,
            format="%.2f"
        )
        
        if st.session_state.use_kw:
            business_rates_per_kw = st.number_input(
                "Business Rates (£/kW/year)",
                min_value=0,
                max_value=20,
                value=3,
                step=1,
                format="%d"
            )
            business_rates = business_rates_per_kw * 1000
        else:
            business_rates = st.number_input(
                "Business Rates (£/MW/year)",
                min_value=0,
                max_value=10000,
                value=3000,
                step=500,
                format="%d"
            )
    
    with col2:
        st.markdown("**Financial Metrics**")
        discount_rate = st.number_input(
            "Discount Rate (%)",
            min_value=5.0,
            max_value=15.0,
            value=8.0,
            step=0.5,
            format="%.1f"
        )
        
        degradation = st.number_input(
            "Annual Degradation (%)",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.1,
            format="%.1f"
        )
        
        st.markdown("**Inflation Assumptions**")
        revenue_inflation = st.number_input(
            "PPA Escalation (%/year)",
            min_value=0.0,
            max_value=5.0,
            value=0.0,
            step=0.5,
            format="%.1f"
        )
        
        cost_inflation = st.number_input(
            "Cost Inflation (%/year)",
            min_value=0.0,
            max_value=5.0,
            value=2.5,
            step=0.5,
            format="%.1f"
        )
    
    with col3:
        st.markdown("**Project Finance**")
        use_debt = st.checkbox("Enable Debt Financing", value=True)
        
        if use_debt:
            debt_percentage = st.slider(
                "Debt Percentage (%)",
                min_value=0,
                max_value=80,
                value=70,
                step=5,
                format="%d%%"
            )
            
            debt_rate = st.number_input(
                "Debt Interest Rate (%)",
                min_value=3.0,
                max_value=10.0,
                value=5.5,
                step=0.5,
                format="%.1f"
            )
            
            debt_term = st.number_input(
                "Debt Term (years)",
                min_value=5,
                max_value=20,
                value=15,
                step=1,
                format="%d"
            )
        else:
            debt_percentage = 0
            debt_rate = 0
            debt_term = 0

else:
    # Partner mode
    with st.expander("⚙️ Advanced Settings"):
        col1, col2 = st.columns(2)
        
        with col1:
            discount_rate = st.number_input(
                "Target Return (%)",
                min_value=6.0,
                max_value=12.0,
                value=8.0,
                step=0.5,
                format="%.1f",
                help="Your required rate of return"
            )
            
            revenue_inflation = st.number_input(
                "PPA Annual Escalation (%)",
                min_value=0.0,
                max_value=3.0,
                value=0.0,
                step=0.5,
                format="%.1f",
                help="Annual PPA price increase"
            )
        
        with col2:
            use_debt = st.checkbox("Include Project Finance", value=True)
            if use_debt:
                debt_percentage = st.slider(
                    "Debt Percentage (%)",
                    min_value=50,
                    max_value=80,
                    value=70,
                    step=5,
                    format="%d%%"
                )
            else:
                debt_percentage = 0
    
    # Fixed defaults
    epc_cost = 750000
    om_cost = 10000
    insurance_rate = 0.25
    business_rates = 3000
    degradation = 0.5
    cost_inflation = 2.5
    debt_rate = 5.5
    debt_term = 15

# Calculation function
def calculate_ppa_price():
    degradation_rate = degradation / 100
    discount_rate_decimal = discount_rate / 100
    insurance_rate_decimal = insurance_rate / 100
    revenue_inflation_decimal = revenue_inflation / 100
    cost_inflation_decimal = cost_inflation / 100
    debt_percentage_decimal = debt_percentage / 100
    debt_rate_decimal = debt_rate / 100
    
    total_capex = capacity_mw * epc_cost
    
    if use_debt and debt_percentage > 0:
        debt_amount = total_capex * debt_percentage_decimal
        equity_amount = total_capex * (1 - debt_percentage_decimal)
    else:
        debt_amount = 0
        equity_amount = total_capex
    
    annual_generation_year1 = capacity_mw * annual_yield * 1000
    
    years = np.arange(0, project_life + 1)
    generation_profile = np.zeros(project_life + 1)
    operating_costs = np.zeros(project_life + 1)
    debt_service = np.zeros(project_life + 1)
    
    capex_flow = np.zeros(project_life + 1)
    capex_flow[0] = -equity_amount
    
    for year in range(1, project_life + 1):
        generation_profile[year] = annual_generation_year1 * ((1 - degradation_rate) ** (year - 1)) / 1000
        
        annual_om = om_cost * capacity_mw * ((1 + cost_inflation_decimal) ** (year - 1))
        annual_insurance = total_capex * insurance_rate_decimal * ((1 + cost_inflation_decimal) ** (year - 1))
        annual_business_rates = business_rates * capacity_mw * ((1 + cost_inflation_decimal) ** (year - 1))
        
        operating_costs[year] = annual_om + annual_insurance + annual_business_rates
        
        if use_debt and debt_amount > 0 and year <= debt_term:
            if debt_rate_decimal > 0:
                debt_service[year] = debt_amount * (debt_rate_decimal * (1 + debt_rate_decimal) ** debt_term) / \
                                   ((1 + debt_rate_decimal) ** debt_term - 1)
            else:
                debt_service[year] = debt_amount / debt_term
    
    npv_costs = equity_amount
    npv_generation = 0
    
    for year in range(1, project_life + 1):
        discount_factor = (1 + discount_rate_decimal) ** year
        npv_costs += (operating_costs[year] + debt_service[year]) / discount_factor
        npv_generation += generation_profile[year] / discount_factor
    
    required_ppa_price = npv_costs / npv_generation if npv_generation > 0 else 0
    
    cash_flows = capex_flow.copy()
    revenues = np.zeros(project_life + 1)
    
    for year in range(1, project_life + 1):
        ppa_price_year = required_ppa_price * ((1 + revenue_inflation_decimal) ** (year - 1))
        revenues[year] = generation_profile[year] * ppa_price_year
        cash_flows[year] = revenues[year] - operating_costs[year] - debt_service[year]
    
    equity_cash_flows = cash_flows.copy()
    project_irr = npf.irr(equity_cash_flows) * 100 if len(equity_cash_flows) > 0 else 0
    equity_npv = npf.npv(discount_rate_decimal, equity_cash_flows)
    
    project_cash_flows = capex_flow.copy()
    project_cash_flows[0] = -total_capex
    for year in range(1, project_life + 1):
        project_cash_flows[year] = revenues[year] - operating_costs[year]
    
    project_level_irr = npf.irr(project_cash_flows) * 100
    
    cumulative_cf = np.cumsum(cash_flows)
    payback_idx = np.where(cumulative_cf > 0)[0]
    if len(payback_idx) > 0:
        payback_period = payback_idx[0]
        if payback_period > 0:
            payback_period = payback_period - 1 + abs(cumulative_cf[payback_period-1]) / cash_flows[payback_period]
    else:
        payback_period = project_life + 1
    
    total_costs_npv = total_capex
    for year in range(1, project_life + 1):
        total_costs_npv += operating_costs[year] / ((1 + discount_rate_decimal) ** year)
    
    lcoe = total_costs_npv / npv_generation if npv_generation > 0 else 0
    
    return {
        'ppa_price': required_ppa_price,
        'ppa_price_pence': required_ppa_price / 10,
        'equity_irr': project_irr,
        'project_irr': project_level_irr,
        'npv': equity_npv,
        'payback': payback_period,
        'lcoe': lcoe,
        'total_capex': total_capex,
        'debt_amount': debt_amount,
        'equity_amount': equity_amount,
        'year1_generation': generation_profile[1],
        'year1_revenue': revenues[1],
        'cash_flows': cash_flows,
        'revenues': revenues,
        'operating_costs': operating_costs,
        'debt_service': debt_service,
        'generation_profile': generation_profile,
        'cumulative_cf': cumulative_cf,
        'years': years
    }

# Results section
if st.session_state.calculated:
    results = calculate_ppa_price()
    st.session_state.results = results
    
    # Results header
    st.markdown("---")
    st.markdown('<h2 class="results-header">Calculation Results</h2>', unsafe_allow_html=True)
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Required PPA Price",
            f"£{results['ppa_price']:.2f}/MWh",
            f"{results['ppa_price_pence']:.2f}p/kWh",
            help="Minimum PPA price required to achieve target returns"
        )
    
    with col2:
        if st.session_state.access_mode == 'internal':
            st.metric(
                "Equity IRR",
                f"{results['equity_irr']:.1f}%",
                f"{results['equity_irr'] - discount_rate:.1f}% vs target"
            )
        else:
            st.metric(
                "Project Returns",
                f"{results['equity_irr']:.1f}%",
                "IRR"
            )
    
    with col3:
        st.metric(
            "Payback Period",
            f"{results['payback']:.1f} years",
            f"of {project_life} year term"
        )
    
    with col4:
        if st.session_state.access_mode == 'internal':
            st.metric(
                "LCOE",
                f"£{results['lcoe']:.2f}/MWh",
                "Levelised Cost"
            )
        else:
            st.metric(
                "Annual Revenue",
                f"£{results['year1_revenue']/1000000:.2f}M",
                "Year 1"
            )
    
    # Additional metrics for internal mode
    if st.session_state.access_mode == 'internal':
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total CAPEX", f"£{results['total_capex']/1000000:.2f}M")
        with col2:
            st.metric("Debt Financing", f"£{results['debt_amount']/1000000:.2f}M")
        with col3:
            st.metric("Equity Required", f"£{results['equity_amount']/1000000:.2f}M")
        with col4:
            st.metric("Project IRR", f"{results['project_irr']:.1f}%", "(unlevered)")
    
    # Visualizations
    tab1, tab2, tab3 = st.tabs(["📈 Cash Flow Analysis", "📊 Sensitivity Analysis", "💾 Export Results"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Annual cash flow
            fig_annual = go.Figure()
            
            operational_years = results['years'][1:]
            operational_cf = results['cash_flows'][1:]
            
            colors = ['#FF6B6B' if x < 0 else '#7CC061' for x in operational_cf]
            
            fig_annual.add_trace(go.Bar(
                x=operational_years,
                y=operational_cf,
                name='Net Cash Flow',
                marker_color=colors
            ))
            
            fig_annual.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.5)
            
            fig_annual.update_layout(
                title="Annual Cash Flow Projection",
                xaxis_title="Year",
                yaxis_title="Cash Flow (£)",
                height=400,
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', family="Source Sans Pro, sans-serif"),
                xaxis=dict(gridcolor='rgba(255,255,255,0.1)', zerolinecolor='rgba(255,255,255,0.1)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.1)', zerolinecolor='rgba(255,255,255,0.1)')
            )
            
            st.plotly_chart(fig_annual, width="stretch")
        
        with col2:
            # Cumulative cash flow
            fig_cumulative = go.Figure()
            
            fig_cumulative.add_trace(go.Scatter(
                x=results['years'],
                y=results['cumulative_cf'],
                mode='lines+markers',
                name='Cumulative Cash Flow',
                line=dict(width=3, color='#7CC061'),
                marker=dict(size=6, color='#7CC061'),
                fill='tonexty',
                fillcolor='rgba(124, 192, 97, 0.2)'
            ))
            
            fig_cumulative.add_hline(y=0, line_dash="dash", line_color="#FF6B6B", opacity=0.8)
            
            # Add payback point
            if results['payback'] <= project_life:
                fig_cumulative.add_annotation(
                    x=results['payback'],
                    y=0,
                    text=f"Payback: {results['payback']:.1f} years",
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=2,
                    arrowcolor="#7CC061",
                    font=dict(color='white', size=12)
                )
            
            fig_cumulative.update_layout(
                title="Cumulative Cash Flow",
                xaxis_title="Year",
                yaxis_title="Cumulative Cash Flow (£)",
                height=400,
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', family="Source Sans Pro, sans-serif"),
                xaxis=dict(gridcolor='rgba(255,255,255,0.1)', zerolinecolor='rgba(255,255,255,0.1)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.1)', zerolinecolor='rgba(255,255,255,0.1)')
            )
            
            st.plotly_chart(fig_cumulative, width="stretch")
        
        # Revenue breakdown (internal mode only)
        if st.session_state.access_mode == 'internal':
            fig_breakdown = go.Figure()
            
            years_operational = results['years'][1:]
            
            fig_breakdown.add_trace(go.Scatter(
                x=years_operational,
                y=results['revenues'][1:],
                name='Revenue',
                line=dict(width=3, color='#7CC061'),
                stackgroup='one'
            ))
            
            fig_breakdown.add_trace(go.Scatter(
                x=years_operational,
                y=-results['operating_costs'][1:],
                name='Operating Costs',
                line=dict(width=3, color='#FF6B6B'),
                stackgroup='two'
            ))
            
            if use_debt and any(results['debt_service'][1:] > 0):
                fig_breakdown.add_trace(go.Scatter(
                    x=years_operational,
                    y=-results['debt_service'][1:],
                    name='Debt Service',
                    line=dict(width=3, color='#FFA500'),
                    stackgroup='two'
                ))
            
            fig_breakdown.update_layout(
                title="Revenue and Cost Breakdown",
                xaxis_title="Year",
                yaxis_title="Amount (£)",
                height=400,
                hovermode='x unified',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', family="Source Sans Pro, sans-serif"),
                xaxis=dict(gridcolor='rgba(255,255,255,0.1)', zerolinecolor='rgba(255,255,255,0.1)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.1)', zerolinecolor='rgba(255,255,255,0.1)'),
                legend=dict(bgcolor='rgba(0,0,0,0)')
            )
            
            st.plotly_chart(fig_breakdown, width="stretch")
    
    with tab2:
        st.markdown("### PPA Price Sensitivity Analysis")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            sensitivity_range = st.slider(
                "Analysis Range",
                min_value=10,
                max_value=50,
                value=30,
                step=5,
                format="%d%%",
                help="Percentage variation from calculated PPA price"
            ) / 100
        
        # Calculate sensitivity
        ppa_variations = np.linspace(
            results['ppa_price'] * (1 - sensitivity_range),
            results['ppa_price'] * (1 + sensitivity_range),
            21
        )
        
        irr_results = []
        npv_results = []
        
        for test_ppa in ppa_variations:
            test_cf = np.zeros(project_life + 1)
            test_cf[0] = -results['equity_amount']
            
            for year in range(1, project_life + 1):
                test_revenue = results['generation_profile'][year] * test_ppa * ((1 + revenue_inflation / 100) ** (year - 1))
                test_cf[year] = test_revenue - results['operating_costs'][year] - results['debt_service'][year]
            
            test_irr = npf.irr(test_cf) * 100
            test_npv = npf.npv(discount_rate / 100, test_cf)
            
            irr_results.append(test_irr)
            npv_results.append(test_npv)
        
        # Create sensitivity charts
        col1, col2 = st.columns(2)
        
        with col1:
            fig_irr_sens = go.Figure()
            
            fig_irr_sens.add_trace(go.Scatter(
                x=ppa_variations,
                y=irr_results,
                mode='lines+markers',
                name='IRR',
                line=dict(width=3, color='#7CC061'),
                marker=dict(size=8, color='#7CC061')
            ))
            
            fig_irr_sens.add_vline(
                x=results['ppa_price'], 
                line_dash="dash", 
                line_color="#FF6B6B",
                opacity=0.8,
                annotation_text=f"Required: £{results['ppa_price']:.2f}",
                annotation_font=dict(color='white', size=10)
            )
            
            fig_irr_sens.add_hline(
                y=discount_rate, 
                line_dash="dash", 
                line_color="#FFA500",
                opacity=0.8,
                annotation_text=f"Target: {discount_rate}%",
                annotation_font=dict(color='white', size=10)
            )
            
            fig_irr_sens.update_layout(
                title="IRR Sensitivity to PPA Price",
                xaxis_title="PPA Price (£/MWh)",
                yaxis_title="IRR (%)",
                height=400,
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', family="Source Sans Pro, sans-serif"),
                xaxis=dict(gridcolor='rgba(255,255,255,0.1)', zerolinecolor='rgba(255,255,255,0.1)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.1)', zerolinecolor='rgba(255,255,255,0.1)')
            )
            
            st.plotly_chart(fig_irr_sens, width="stretch")
        
        with col2:
            fig_npv_sens = go.Figure()
            
            fig_npv_sens.add_trace(go.Scatter(
                x=ppa_variations,
                y=[npv/1000000 for npv in npv_results],
                mode='lines+markers',
                name='NPV',
                line=dict(width=3, color='#7CC061'),
                marker=dict(size=8, color='#7CC061')
            ))
            
            fig_npv_sens.add_vline(
                x=results['ppa_price'], 
                line_dash="dash", 
                line_color="#FF6B6B",
                opacity=0.8,
                annotation_text=f"Required: £{results['ppa_price']:.2f}",
                annotation_font=dict(color='white', size=10)
            )
            
            fig_npv_sens.add_hline(
                y=0, 
                line_dash="dash", 
                line_color="white",
                opacity=0.5
            )
            
            fig_npv_sens.update_layout(
                title="NPV Sensitivity to PPA Price",
                xaxis_title="PPA Price (£/MWh)",
                yaxis_title="NPV (£M)",
                height=400,
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', family="Source Sans Pro, sans-serif"),
                xaxis=dict(gridcolor='rgba(255,255,255,0.1)', zerolinecolor='rgba(255,255,255,0.1)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.1)', zerolinecolor='rgba(255,255,255,0.1)')
            )
            
            st.plotly_chart(fig_npv_sens, width="stretch")
        
        # Sensitivity table
        st.markdown("### Sensitivity Summary Table")
        
        key_points = [0.9, 0.95, 1.0, 1.05, 1.1]
        summary_data = []
        
        for multiplier in key_points:
            idx = int((multiplier - (1 - sensitivity_range)) / (2 * sensitivity_range) * 20)
            if 0 <= idx < len(ppa_variations):
                summary_data.append({
                    'Scenario': f"{int((multiplier-1)*100):+d}%",
                    'PPA Price (£/MWh)': f"{ppa_variations[idx]:.2f}",
                    'IRR (%)': f"{irr_results[idx]:.1f}",
                    'NPV (£M)': f"{npv_results[idx]/1000000:.2f}"
                })
        
        summary_df = pd.DataFrame(summary_data)
        
        # Style the dataframe for dark theme
        styled_df = summary_df.style.set_properties(**{
            'background-color': 'rgba(255,255,255,0.05)',
            'color': 'white',
            'border': '1px solid rgba(255,255,255,0.2)'
        }).set_table_styles([{
            'selector': 'th',
            'props': [('background-color', 'rgba(124,192,97,0.3)'), ('color', 'white')]
        }])
        
        st.dataframe(styled_df, width="stretch", hide_index=True)
    
    with tab3:
        st.markdown("### Export Results")
        
        # Prepare export data
        export_summary = pd.DataFrame({
            'Metric': [
                'System Capacity',
                'Annual Yield (kWh/kWp)',
                'Year 1 Generation',
                'PPA Term (years)',
                'Total CAPEX',
                'Required PPA Price (£/MWh)',
                'Equity IRR (%)',
                'Project IRR (%)',
                'NPV',
                'Payback Period (years)',
                'LCOE (£/MWh)'
            ],
            'Value': [
                f"{capacity_mw:.3f} MW" if not st.session_state.use_kw else f"{capacity_mw*1000:.0f} kW",
                annual_yield,
                f"{results['year1_generation']:.0f} MWh",
                project_life,
                f"£{results['total_capex']:,.0f}",
                f"{results['ppa_price']:.2f}",
                f"{results['equity_irr']:.1f}",
                f"{results['project_irr']:.1f}",
                f"£{results['npv']:,.0f}",
                f"{results['payback']:.1f}",
                f"{results['lcoe']:.2f}"
            ]
        })
        
        # Cash flow table
        cash_flow_df = pd.DataFrame({
            'Year': results['years'],
            'Generation (MWh)': results['generation_profile'],
            'Revenue (£)': results['revenues'],
            'Operating Costs (£)': results['operating_costs'],
            'Debt Service (£)': results['debt_service'],
            'Net Cash Flow (£)': results['cash_flows'],
            'Cumulative CF (£)': results['cumulative_cf']
        })
        
        # Export buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            # Excel export
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:  # type: ignore
                export_summary.to_excel(writer, sheet_name='Summary', index=False)
                cash_flow_df.to_excel(writer, sheet_name='Cash Flow', index=False)
                
                if 'sensitivity_df' in locals():
                    summary_df.to_excel(writer, sheet_name='Sensitivity', index=False)
            
            buffer.seek(0)
            
            st.download_button(
                label="📥 Download Excel Report",
                data=buffer,
                file_name=f"Saber_PPA_Analysis_{capacity_mw*1000:.0f}kW_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width="stretch"
            )
            
            # CSV export
            csv = cash_flow_df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV Data",
                data=csv,
                file_name=f"Saber_PPA_CashFlow_{capacity_mw*1000:.0f}kW_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                width="stretch"
            )

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #B0B0B0; padding: 2rem 0;'>
        <p style='margin-bottom: 0.5rem;'>© 2025 Saber Renewable Energy Ltd | saberrenewables.com</p>
        <p style='font-size: 14px;'>Infinite Power in Partnership</p>
    </div>
    """,
    unsafe_allow_html=True
)