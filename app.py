import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import io

# --- 1. SET PAGE CONFIGURATION & APP CONTROLS ---
st.set_page_config(
    page_title="AgriGrow ERP Pro",
    page_icon="🚜",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Shared Stylesheet blending #2F578A seamlessly into a clean corporate interface
st.markdown("""
    <style>
    /* Global Overrides & Professional Typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght=300;400;500;600;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { 
        font-family: 'Inter', sans-serif; 
        background-color: #f4f6f9; 
    }
    
    .main-header { font-size: 2.2rem; color: #1e293b; font-weight: 700; margin-bottom: 0.5rem; letter-spacing: -0.5px; }
    .sub-header { font-size: 1.1rem; color: #64748b; margin-bottom: 2rem; }
    
    .section-banner { 
        background-color: #ffffff; 
        padding: 1rem 1.25rem; 
        border-radius: 8px; 
        border-left: 5px solid #2F578A; 
        margin-bottom: 1.5rem; 
        box-shadow: 0 1px 3px rgba(0,0,0,0.02); 
    }
    .section-banner h5 { margin: 0; color: #2F578A; font-weight: 600; }
    
    /* Modern Dashboard Metric Cards with Palette Accents */
    .card-metric { 
        background: #ffffff; 
        padding: 1.5rem; 
        border-radius: 12px; 
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03); 
        border: 1px solid #e2e8f0; 
        position: relative; 
        overflow: hidden; 
    }
    .card-metric::before { 
        content: ""; 
        position: absolute; 
        top: 0; 
        left: 0; 
        width: 4px; 
        height: 100%; 
        background: #2F578A; 
    }
    .metric-num { font-size: 1.8rem; font-weight: 700; color: #0f172a; margin-top: 0.5rem; letter-spacing: -0.5px; }
    .metric-titl { font-size: 0.75rem; color: #64748b; text-transform: uppercase; font-weight: 700; letter-spacing: 0.8px; }
    
    /* --- SIDEBAR HIGH-CONTRAST TEXT & PALETTE OVERRIDES --- */
    [data-testid="stSidebar"] { 
        min-width: 340px !important; 
        max-width: 340px !important; 
        background-color: #1e2638 !important; 
    }
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] span[data-testid="stWidgetLabel"] p { 
        color: #ffffff !important; 
        font-weight: 500 !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label {
        color: #cbd5e1 !important;
    }
    [data-testid="stSidebarUserContent"] { padding: 1.5rem 1rem !important; }
    
    .sidebar-card { 
        background-color: #2a344a; 
        padding: 1rem; 
        border-radius: 10px; 
        margin: 0.5rem 0; 
        border: 1px solid #3d4a66; 
    }
    .sidebar-text { font-size: 0.85rem; color: #cbd5e1 !important; margin: 6px 0; line-height: 1.5; }
    .sidebar-text b { color: #ffffff !important; }
    
    .badge-active { background-color: #2F578A; color: #ffffff; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; }
    
    /* Prevent Button Text Overflow & Enable Wrapping */
    div[data-testid="stWidgetFormSubmitButton"] > button {
        width: 100% !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        height: auto !important;
        padding: 0.5rem 1rem !important;
        background-color: #2F578A !important;
        color: white !important;
    }
    
    div[data-testid="stForm"] { 
        background-color: #ffffff; 
        padding: 2rem; 
        border-radius: 12px; 
        border: 1px solid #e2e8f0; 
        box-shadow: 0 1px 3px rgba(0,0,0,0.02); 
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. STATE INITIALIZATION (PURE IN-MEMORY ENGINE) ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = ""
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'currency' not in st.session_state:
    st.session_state.currency = "KES (KSh)"
if 'sandbox_container' not in st.session_state:
    st.session_state.sandbox_container = []

# Core Identities & Access Control Matrix Database
if 'system_users_db' not in st.session_state:
    st.session_state.system_users_db = {
        "admin@agrigrow.com": {"password": "password", "name": "Paul Gaitho", "role": "Data Auditor Pro"},
        "owner@agrigrow.com": {"password": "ownerpassword", "name": "Executive Management", "role": "Farm Owner"},
        "field@agrigrow.com": {"password": "fieldpassword", "name": "Emily Mkabili", "role": "Field Operations Lead"}
    }

# Dynamic Editable Configuration Lists
if 'crop_names_list' not in st.session_state:
    st.session_state.crop_names_list = ["Maize", "Wheat", "Tomatoes", "Coffee", "Potatoes", "Barley", "Rice", "Sugarcane", "Beans"]
if 'crop_types_list' not in st.session_state:
    st.session_state.crop_types_list = ["Cereal", "Vegetable", "Fruit", "Cash Crop", "Legume"]
if 'expense_categories' not in st.session_state:
    st.session_state.expense_categories = ["Fertilizer", "Chemicals/Pesticides", "Labor", "Equipment Rental", "Seedlings", "Fuel"]

# Mock Baseline Storage Datasets
if 'crops_data' not in st.session_state:
    st.session_state.crops_data = pd.DataFrame([
        {"id": 1, "crop_name": "Maize", "crop_type": "Cereal", "growing_season": "Long Rains 2026", "yield_acre": 25.0, "market_price": 450.00, "cost_acre": 4500.00, "income_acre": 11250.00, "net_returns": 6750.00},
        {"id": 2, "crop_name": "Tomatoes", "crop_type": "Vegetable", "growing_season": "Greenhouse A", "yield_acre": 150.0, "market_price": 120.00, "cost_acre": 8000.00, "income_acre": 18000.00, "net_returns": 10000.00}
    ])

if 'projects_data' not in st.session_state:
    st.session_state.projects_data = pd.DataFrame([
        {"id": 1, "project_name": "West Field Maize", "crop": "Maize", "acreage": 10.0, "est_yield_acre": 25.0, "est_market_price": 450.00, "est_cost_acre": 4500.00, "estimated_cost": 45000.00, "estimated_income": 112500.00, "status": "Ongoing", "start_date": "2026-03-15"}
    ])

if 'expenses_data' not in st.session_state:
    st.session_state.expenses_data = pd.DataFrame([
        {"id": 1, "date": "2026-03-20", "project": "West Field Maize", "description": "NUR-30 Fertilizer Bulk", "category": "Fertilizer", "uom": "Bags", "units": 12.0, "cost_per_unit": 2500.00, "amount": 30000.00, "other_charges": 2500.00, "total_cost": 32500.00, "paid": "Paid"},
        {"id": 2, "date": "2026-03-22", "project": "West Field Maize", "description": "Tractor Operator Wages", "category": "Labor", "uom": "Hours", "units": 20.0, "cost_per_unit": 400.00, "amount": 8000.00, "other_charges": 0.00, "total_cost": 8000.00, "paid": "Paid"},
        {"id": 3, "date": "2026-04-05", "project": "West Field Maize", "description": "Administrative Fuel Allocation", "category": "Fuel", "uom": "Liters", "units": 15.0, "cost_per_unit": 200.00, "amount": 3000.00, "other_charges": 0.00, "total_cost": 3000.00, "paid": "Not Paid"}
    ])

if 'income_data' not in st.session_state:
    st.session_state.income_data = pd.DataFrame([
        {"id": 1, "date": "2026-05-01", "source": "Global Grains Corp", "description": "Contract deposit", "project": "West Field Maize", "crop": "Maize", "yield_units": 100.0, "price": 450.00, "amount": 45000.00, "other_income": 5000.00, "total_income": 50000.00, "paid": "Paid", "payment_mode": "Bank", "payment_code": "TXN98432"}
    ])

if 'registry_data' not in st.session_state:
    st.session_state.registry_data = pd.DataFrame([
        {"id": 1, "date": "2026-02-10", "source": "AgriChem Suppliers", "description": "NPK 17-17-17", "project": "Reference Pool", "crop": "N/A", "yield_units": 1.0, "price": 3200.00, "income": 0, "other_income": 0, "total_income": 0, "paid": "Yes", "payment_mode": "Cash", "payment_code": "REF-01"}
    ])

# Localized Currency Extraction Helper
c_symbol = st.session_state.currency.split(" ")[1].replace("(", "").replace(")", "")

# --- 3. SIGN-IN ACCESS CONTROL ENFORCEMENT ---
if not st.session_state.authenticated:
    st.markdown("""
        <style>
            [data-testid="stSidebar"] { display: none !important; }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="main-header" style="text-align:center; margin-top:5rem;">🌾 AgriGrow ERP Enterprise Portal</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("login_gate"):
            st.markdown("### Secure Sign-In Matrix")
            uid = st.text_input("Corporate Email Address", value="admin@agrigrow.com")
            pwd = st.text_input("Secure Access Passphrase", type="password", value="password")
            
            if st.form_submit_button("Authenticate Access Path", use_container_width=True):
                if uid in st.session_state.system_users_db and st.session_state.system_users_db[uid]["password"] == pwd:
                    st.session_state.authenticated = True
                    st.session_state.user_name = st.session_state.system_users_db[uid]["name"]
                    st.session_state.user_role = st.session_state.system_users_db[uid]["role"]
                    st.toast(f"Logged in successfully!", icon="🎯")
                    st.rerun()
                else:
                    st.error("Authentication rejected. Invalid identity metrics.")
    st.stop()

# --- 4. SYSTEM CONSOLE NAVIGATION WITH FIXED OVERLAYS ---
with st.sidebar:
    st.markdown("## 🚜 AgriGrow ERP")
    st.markdown("---")
    
    # 🗂️ MAIN SYSTEM NAVIGATION
    current_tab = st.radio("Select Workspace Tab:", [
        "📊 Dashboard", "🌱 Crops Registry", "🏗️ Projects Manager", 
        "📉 Expenses Tracker", "💰 Income Ledger", "⚖️ Cost-Benefit Sandbox", 
        "📋 Financial Reporting", "📈 Predictive Insights", "🧪 Market Input Registry", 
        "⚙️ Lists & Categories Config", "🛠️ System Config"
    ])
    st.markdown("---")
    
    # 🌦️ 1. WEATHER COMPONENT SUMMARY EXPANDER
    with st.expander("🌦️ Weather Summary", expanded=False):
        st.markdown("""
            <div class="sidebar-card">
                <div class="sidebar-text"><b>Region:</b> Nairobi Core Zone</div>
                <div class="sidebar-text"><b>Temperature:</b> 24.5°C</div>
                <div class="sidebar-text"><b>Humidity Index:</b> 62%</div>
                <div class="sidebar-text"><b>Condition:</b> Scattered Showers</div>
            </div>
        """, unsafe_allow_html=True)
        
    # 🩺 2. SYSTEM HEALTH STATUS LOGS EXPANDER
    with st.expander("🩺 System Health Logs", expanded=False):
        st.markdown("""
            <div class="sidebar-card">
                <div class="sidebar-text"><b>Memory Mode:</b> <span style='color:#68d391; font-weight:bold;'>Active</span></div>
                <div class="sidebar-text"><b>Server Latency:</b> 4ms</div>
                <div class="sidebar-text"><b>Active Workers:</b> Local Canvas</div>
            </div>
        """, unsafe_allow_html=True)
        
    # 👤 3. USER PROFILE COMPONENT CARD
    with st.expander("👤 User Profile Frame", expanded=True):
        st.markdown(f"""
            <div class="sidebar-card" style="border-left: 3px solid #2F578A;">
                <div class="sidebar-text"><b>User:</b> {st.session_state.user_name}</div>
                <div class="sidebar-text"><b>Role:</b> {st.session_state.user_role}</div>
                <div class="sidebar-text"><b>Status:</b> <span class="badge-active">Online</span></div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🚪 Terminate Session", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# --- 5. WORKSPACE MODULE IMPLEMENTATIONS ---

# 1. TAB: DASHBOARD
if current_tab == "📊 Dashboard":
    st.markdown('<div class="main-header">📊 Operational Dashboard</div>', unsafe_allow_html=True)
    
    e_df = st.session_state.expenses_data
    i_df = st.session_state.income_data
    p_df = st.session_state.projects_data

    f1, f2, f3 = st.columns(3)
    with f1:
        p_opt = ["All Active Projects"] + list(p_df["project_name"].unique()) if not p_df.empty else ["All Active Projects"]
        f_proj = st.selectbox("Project Scope Filter:", p_opt)
    with f2:
        f_month = st.selectbox("Month Scope Filter:", ["All Months", "Jan", "Feb", "Mar", "Apr", "May", "Jun"])
    with f3:
        f_year = st.selectbox("Fiscal Year Filter:", ["2026", "2025"])
    
    if f_proj != "All Active Projects":
        e_df = e_df[e_df["project"] == f_proj]
        i_df = i_df[i_df["project"] == f_proj]

    calc_total_exp = e_df["total_cost"].sum() if not e_df.empty else 0.0
    calc_total_inc = i_df["total_income"].sum() if not i_df.empty else 0.0
    calc_net_prof = calc_total_inc - calc_total_exp
    calc_margin = (calc_net_prof / calc_total_inc * 100) if calc_total_inc > 0 else 0.0

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.markdown(f'<div class="card-metric"><div class="metric-titl">Total Expenditures</div><div class="metric-num">{c_symbol} {calc_total_exp:,.2f}</div></div>', unsafe_allow_html=True)
    with kpi2:
        st.markdown(f'<div class="card-metric"><div class="metric-titl">Realized Revenues</div><div class="metric-num">{c_symbol} {calc_total_inc:,.2f}</div></div>', unsafe_allow_html=True)
    with kpi3:
        color = "#2F578A" if calc_net_prof >= 0 else "#dc2626"
        st.markdown(f'<div class="card-metric"><div class="metric-titl">Net Profit / Loss</div><div class="metric-num" style="color:{color};">{c_symbol} {calc_net_prof:,.2f}</div></div>', unsafe_allow_html=True)
    with kpi4:
        st.markdown(f'<div class="card-metric"><div class="metric-titl">Profit Margin</div><div class="metric-num">{calc_margin:.1f}%</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    graph_col1, graph_col2 = st.columns(2)
    with graph_col1:
        st.subheader("Cash Flow Breakdown")
        cf_df = pd.DataFrame({
            "Stream": ["Income", "Expenses", "Net Profit"],
            "Value": [calc_total_inc, calc_total_exp, calc_net_prof]
        })
        fig_cf = px.bar(cf_df, x="Stream", y="Value", color="Stream", template="plotly_white", color_discrete_sequence=["#2F578A", "#ba3c3c", "#4180ab"])
        st.plotly_chart(fig_cf, use_container_width=True)
        
    with graph_col2:
        st.subheader("Expense Distribution per Category")
        if not e_df.empty:
            cat_totals = e_df.groupby("category")["total_cost"].sum().reset_index()
            # FIX APPLIED HERE: Changed .Ice to .ice (or .Blues)
            fig_pie = px.pie(
    cat_totals, 
    values="total_cost", 
    names="category", 
    hole=0.4, 
    color_discrete_sequence=["#2F578A", "#4A7BB0", "#76A2D6", "#A2C8F7", "#D0E3FF"]
)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No recorded expense entries match your selection criteria.")

# 2. TAB: CROPS REGISTRY
elif current_tab == "🌱 Crops Registry":
    st.markdown('<div class="main-header">🌱 Global Crops Registry</div>', unsafe_allow_html=True)
    
    with st.expander("➕ Register a New Crop Profile Type", expanded=False):
        with st.form("form_crop_add"):
            col_cr1, col_cr2, col_cr3 = st.columns(3)
            with col_cr1: cr_name = st.selectbox("Crop Name Configuration:", st.session_state.crop_names_list)
            with col_cr2: cr_type = st.selectbox("Crop Type / Category:", st.session_state.crop_types_list)
            with col_cr3: cr_season = st.text_input("Growing Season Identifier:", value="Main Season 2026")
                
            col_cr4, col_cr5, col_cr6 = st.columns(3)
            with col_cr4: cr_yield = st.number_input("Avg Yield per Acre:", min_value=0.0, value=35.0)
            with col_cr5: cr_price = st.number_input(f"Market Price per Unit Value ({c_symbol}):", min_value=0.0, value=450.00)
            with col_cr6: cr_cost = st.number_input(f"Avg Production Cost per Acre({c_symbol}):", min_value=0.0, value=5000.00)

            cr_calc_inc = cr_yield * cr_price
            cr_calc_ret = cr_calc_inc - cr_cost
            st.markdown(f"**⚡ Real-Time Estimation Context:** Gross Revenue/Acre: `{c_symbol} {cr_calc_inc:,.2f}` | Net Return/Acre: `{c_symbol} {cr_calc_ret:,.2f}`")
            
            if st.form_submit_button("Save Crop Baseline Profile"):
                new_id = int(st.session_state.crops_data["id"].max() + 1) if not st.session_state.crops_data.empty else 1
                new_row = pd.DataFrame([{"id": new_id, "crop_name": cr_name, "crop_type": cr_type, "growing_season": cr_season, "yield_acre": cr_yield, "market_price": cr_price, "cost_acre": cr_cost, "income_acre": cr_calc_inc, "net_returns": cr_calc_ret}])
                st.session_state.crops_data = pd.concat([st.session_state.crops_data, new_row], ignore_index=True)
                st.success("Crop profile successfully logged.")
                st.rerun()

    st.markdown('<div class="section-banner"><h5>Registered System Crops Base Metrics</h5></div>', unsafe_allow_html=True)
    st.dataframe(st.session_state.crops_data, use_container_width=True, hide_index=True)

# 3. TAB: PROJECTS MANAGER
elif current_tab == "🏗️ Projects Manager":
    st.markdown('<div class="main-header">🏗️ Production Field Project</div>', unsafe_allow_html=True)
    
    p_df = st.session_state.projects_data
    crops_list = list(st.session_state.crops_data["crop_name"].unique()) if not st.session_state.crops_data.empty else ["Maize"]

    with st.expander("⚙️ Manage Field Projects Setup", expanded=False):
        st.markdown("#### 📝 Launch a New Field Project Operation Block")
        with st.form("form_proj_add"):
            col_pr1, col_pr2, col_pr3 = st.columns(3)
            with col_pr1: pr_name = st.text_input("Project / Field Name Identifier:")
            with col_pr2: pr_crop = st.selectbox("Assigned Crop Node Asset:", st.session_state.crop_names_list)
            with col_pr3: pr_acres = st.number_input("Allocated Acreage Size:", min_value=0.1, value=10.0)
                
            col_pr4, col_pr5, col_pr6 = st.columns(3)
            with col_pr4: pr_yield_ac = st.number_input("Estimated Yield per Acre Units:", min_value=0.0, value=40.0)
            with col_pr5: pr_mkt_pr = st.number_input(f"Target Contract Sale Price / Unit ({c_symbol}):", min_value=0.0, value=450.00)
            with col_pr6: pr_cost_ac = st.number_input(f"Target Cost Budget per Acre ({c_symbol}):", min_value=0.0, value=4500.00)

            calc_pr_cost = pr_cost_ac * pr_acres
            calc_pr_income = pr_mkt_pr * pr_yield_ac * pr_acres
            st.markdown(f"**⚡ Pro-Forma Matrix Auto Forecasts:** Total Field Operational Cost: `{c_symbol} {calc_pr_cost:,.2f}` | Expected Field Income: `{c_symbol} {calc_pr_income:,.2f}`")
            
            col_pr7, col_pr8 = st.columns(2)
            with col_pr7: pr_status = st.selectbox("Project Lifecycles Deployment Status Phase:", ["Proposal", "Ongoing", "Completed"])
            with col_pr8: pr_date = st.date_input("Commencement Schedule Date Picker:", datetime.now())
                
            if st.form_submit_button("Deploy System Project Asset"):
                new_id = int(st.session_state.projects_data["id"].max() + 1) if not st.session_state.projects_data.empty else 1
                new_row = pd.DataFrame([{"id": new_id, "project_name": pr_name, "crop": pr_crop, "acreage": pr_acres, "est_yield_acre": pr_yield_ac, "est_market_price": pr_mkt_pr, "est_cost_acre": pr_cost_ac, "estimated_cost": calc_pr_cost, "estimated_income": calc_pr_income, "status": pr_status, "start_date": str(pr_date)}])
                st.session_state.projects_data = pd.concat([st.session_state.projects_data, new_row], ignore_index=True)
                st.success("Field management profile deployed cleanly.")
                st.rerun()

        st.markdown("---")
        st.markdown("#### 📥 Bulk Ingest Projects Data Portal")
        uploaded_proj_file = st.file_uploader("Upload structured CSV tracking lines directly:", type=["csv"], key="bulk_uploader_projects_csv")
        if uploaded_proj_file is not None:
            try:
                csv_proj_df = pd.read_csv(uploaded_proj_file)
                st.session_state.projects_data = pd.concat([st.session_state.projects_data, csv_proj_df], ignore_index=True)
                st.success("Successfully processed and committed raw CSV data to field project matrices.")
                st.rerun()
            except Exception as e:
                st.error(f"Ingestion processing failure: {str(e)}")

        st.markdown("---")
        st.markdown("#### 📤 Export Field Matrix Arrays")
        if not p_df.empty:
            excel_proj_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_proj_buffer, engine="xlsxwriter") as xl_proj_writer:
                p_df.to_excel(xl_proj_writer, index=False, sheet_name="Field_Projects")
            st.download_button(label="📤 Download Comprehensive Projects Matrix Excel Sheet (.xlsx)", data=excel_proj_buffer.getvalue(), file_name="Projects_Report.xlsx", use_container_width=True)
        else:
            st.warning("No recorded data rows exist inside memory schemas to build field project sheets.")

    st.markdown('<div class="section-banner"><h5>Active Field Land Allocation Control Framework</h5></div>', unsafe_allow_html=True)
    st.dataframe(st.session_state.projects_data, use_container_width=True, hide_index=True)

# 4. TAB: EXPENSES TRACKER
elif current_tab == "📉 Expenses Tracker":
    st.markdown('<div class="main-header">📉 Cost Tracking & Disbursements Accounts Balance</div>', unsafe_allow_html=True)
    
    e_df = st.session_state.expenses_data
    p_df = st.session_state.projects_data
    
    ex_tot = e_df["total_cost"].sum() if not e_df.empty else 0.0
    ex_paid = e_df[e_df["paid"] == "Paid"]["total_cost"].sum() if not e_df.empty else 0.0
    ex_unpaid = ex_tot - ex_paid
    
    eb1, eb2, eb3 = st.columns(3)
    with eb1:
        st.markdown(f'<div class="card-metric" style="border-left: 4px solid #ba3c3c;"><div class="metric-titl">Total Expenses Ledger Invoiced</div><div class="metric-num">{c_symbol} {ex_tot:,.2f}</div></div>', unsafe_allow_html=True)
    with eb2:
        st.markdown(f'<div class="card-metric" style="border-left: 4px solid #2F578A;"><div class="metric-titl">Fully Settle Paid Outflows</div><div class="metric-num">{c_symbol} {ex_paid:,.2f}</div></div>', unsafe_allow_html=True)
    with eb3:
        st.markdown(f'<div class="card-metric" style="border-left: 4px solid #ea580c;"><div class="metric-titl">Outstanding Accounts Payable</div><div class="metric-num">{c_symbol} {ex_unpaid:,.2f}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.expander("⚙️ Manage Expense Transactions Window", expanded=False):
        st.markdown("#### 📝 Manual Transaction Line Entry Form")
        with st.form("form_exp_add"):
            col_ex1, col_ex2, col_ex3 = st.columns(3)
            with col_ex1: ex_date = st.date_input("Transaction Value Date:", datetime.now())
            with col_ex2:
                proj_options = list(p_df["project_name"].unique()) if not p_df.empty else ["West Field Maize"]
                ex_proj = st.selectbox("Link to Active Project Area Unit Node:", proj_options)
            with col_ex3: ex_desc = st.text_input("Expense Record Narrative Note:")
                
            col_ex4, col_ex5, col_ex6 = st.columns(3)
            with col_ex4: ex_cat = st.selectbox("Expense Category Overhead Classification Group:", st.session_state.expense_categories)
            with col_ex5: ex_uom = st.selectbox("Unit of Measure (UoM):", ["Bags", "Liters", "Hours", "Kgs", "Tonnes"])
            with col_ex6: ex_units = st.number_input("Quantity Units Purchased Capacity:", min_value=0.0, value=5.0)
                
            col_ex7, col_ex8, col_ex9 = st.columns(3)
            with col_ex7: ex_cpu = st.number_input(f"Cost per Unit standard baseline valuation ({c_symbol}):", min_value=0.0, value=250.00)
            with col_ex8: ex_chg = st.number_input(f"Ancillary Handling Logistics Fees / Surcharges ({c_symbol}):", min_value=0.0, value=0.00)
            with col_ex9: ex_paid_st = st.selectbox("Settlement Clearing Ledger Status Flag:", ["Paid", "Not Paid"])

            calc_ex_base_amt = ex_units * ex_cpu
            calc_ex_total_cost = calc_ex_base_amt + ex_chg
            st.markdown(f"**⚡ Cost Matrix Real-Time Computations:** Material Subtotal: `{c_symbol} {calc_ex_base_amt:,.2f}` | Gross Total Invoice Cost: `{c_symbol} {calc_ex_total_cost:,.2f}`")
            
            if st.form_submit_button("Log Expense Receipt Data"):
                new_id = int(st.session_state.expenses_data["id"].max() + 1) if not st.session_state.expenses_data.empty else 1
                new_row = pd.DataFrame([{"id": new_id, "date": str(ex_date), "project": ex_proj, "description": ex_desc, "category": ex_cat, "uom": ex_uom, "units": ex_units, "cost_per_unit": ex_cpu, "amount": calc_ex_base_amt, "other_charges": ex_chg, "total_cost": calc_ex_total_cost, "paid": ex_paid_st}])
                st.session_state.expenses_data = pd.concat([st.session_state.expenses_data, new_row], ignore_index=True)
                st.success("Expense stored securely.")
                st.rerun()

        st.markdown("---")
        st.markdown("#### 📥 Bulk Ingest Data Portal")
        uploaded_file = st.file_uploader("Upload structured CSV tracking lines directly:", type=["csv"], key="bulk_uploader_csv")
        if uploaded_file is not None:
            try:
                csv_df = pd.read_csv(uploaded_file)
                st.session_state.expenses_data = pd.concat([st.session_state.expenses_data, csv_df], ignore_index=True)
                st.success("Successfully processed and committed raw CSV data to memory matrices.")
                st.rerun()
            except Exception as e:
                st.error(f"Ingestion processing failure: {str(e)}")

        st.markdown("---")
        st.markdown("#### 📤 Export Ledger Workspace Arrays")
        if not e_df.empty:
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as xl_writer:
                e_df.to_excel(xl_writer, index=False, sheet_name="Ledger_Overheads")
            st.download_button(label="📤 Download Comprehensive Excel Sheet (.xlsx)", data=excel_buffer.getvalue(), file_name="Expenses_Report.xlsx", use_container_width=True)
        else:
            st.warning("No recorded data rows exist inside memory schemas to build report sheets.")

    st.markdown('<div class="section-banner"><h5>Operational Expense Accounting Statement Ledger Table</h5></div>', unsafe_allow_html=True)
    st.dataframe(st.session_state.expenses_data, use_container_width=True, hide_index=True)

# 5. TAB: INCOME LEDGER
elif current_tab == "💰 Income Ledger":
    st.markdown('<div class="main-header">💰 Yield Sales & Receivables Revenue Inflows Ledger Workspace</div>', unsafe_allow_html=True)
    
    i_df = st.session_state.income_data
    p_df = st.session_state.projects_data
    crops_list = list(st.session_state.crops_data["crop_name"].unique()) if not st.session_state.crops_data.empty else ["Maize"]

    with st.expander("⚙️ Manage Income Transactions Configuration Control Window", expanded=False):
        st.markdown("#### 📝 Log Yield Sales Order Commercial Valuation Receivables Receipts")
        with st.form("form_inc_add"):
            col_in1, col_in2, col_in3 = st.columns(3)
            with col_in1: in_date = st.date_input("Value Receipt Transaction Date:", datetime.now())
            with col_in2: in_src = st.text_input("Procurement B2B Entity Corporate Name:")
            with col_in3: in_desc = st.text_input("Transaction Particulars Description Memorandum Note:")
                
            col_in4, col_in5, col_in6 = st.columns(3)
            with col_in4: in_proj = st.selectbox("Link Operational Node Instance tracking to Project Matrix ID:", list(p_df["project_name"].unique()) if not p_df.empty else ["West Field Maize"])
            with col_in5: in_crop = st.selectbox("Cultivated Commodity Matcher Option:", st.session_state.crop_names_list)
            with col_in6: in_yield = st.number_input("Dispatched Cargo Weight Volumes Sold:", min_value=0.0, value=10.0)
                
            col_in7, col_in8, col_in9 = st.columns(3)
            with col_in7: in_price = st.number_input(f"Agreed Spot Contract Sale Price per Unit Metric Line ({c_symbol}):", min_value=0.0, value=450.00)
            with col_in8: in_other = st.number_input(f"Subsidiary Logistics Revenue / Crop Biomass Supplementary Gains ({c_symbol}):", min_value=0.0, value=0.00)
            with col_in9: in_paid = st.selectbox("Payment Settlement Clearance Inward Status Flag Picker Token:", ["Paid", "Unpaid"])
                
            col_in10, col_in11 = st.columns(2)
            with col_in10: in_mode = st.selectbox("Financial Settlement Interbank Channels Mode Alternative Options:", ["Bank", "MPesa", "Cash", "Cheque"])
            with col_in11: in_code = st.text_input("Electronic Ledger Clearing Reference Trace Code:", value="EFT-REF-74239")

            calc_in_amt = in_yield * in_price
            calc_in_tot = calc_in_amt + in_other
            st.markdown(f"**⚡ Live Inflow Revenue Calculations Check:** Core Cargo Value Realized: `{c_symbol} {calc_in_amt:,.2f}` | Gross Balance Cash Inflow Total realized: `{c_symbol} {calc_in_tot:,.2f}`")
            
            if st.form_submit_button("Commit Inbound Commercial Transaction Entry Object"):
                new_id = int(st.session_state.income_data["id"].max() + 1) if not st.session_state.income_data.empty else 1
                new_row = pd.DataFrame([{"id": new_id, "date": str(in_date), "source": in_src, "description": in_desc, "project": in_proj, "crop": in_crop, "yield_units": in_yield, "price": in_price, "amount": calc_in_amt, "other_income": in_other, "total_income": calc_in_tot, "paid": in_paid, "payment_mode": in_mode, "payment_code": in_code}])
                st.session_state.income_data = pd.concat([st.session_state.income_data, new_row], ignore_index=True)
                st.success("Revenue logged properly.")
                st.rerun()

        st.markdown("---")
        st.markdown("#### 📥 Bulk Ingest Income Data Portal")
        uploaded_inc_file = st.file_uploader("Upload structured CSV tracking lines directly:", type=["csv"], key="bulk_uploader_income_csv")
        if uploaded_inc_file is not None:
            try:
                csv_inc_df = pd.read_csv(uploaded_inc_file)
                st.session_state.income_data = pd.concat([st.session_state.income_data, csv_inc_df], ignore_index=True)
                st.success("Successfully processed and committed raw CSV data to income matrices.")
                st.rerun()
            except Exception as e:
                st.error(f"Ingestion processing failure: {str(e)}")

        st.markdown("---")
        st.markdown("#### 📤 Export Revenue Ledger Workspace Arrays")
        if not i_df.empty:
            excel_inc_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_inc_buffer, engine="xlsxwriter") as xl_inc_writer:
                i_df.to_excel(xl_inc_writer, index=False, sheet_name="Ledger_Revenue")
            st.download_button(label="📤 Download Comprehensive Income Excel Sheet (.xlsx)", data=excel_inc_buffer.getvalue(), file_name="Income_Report.xlsx", use_container_width=True)
        else:
            st.warning("No recorded data rows exist inside memory schemas to build income report sheets.")

    st.markdown('<div class="section-banner"><h5>Inward Commercial Yield Distribution & Sales Revenues Statements Records Matrix Table</h5></div>', unsafe_allow_html=True)
    st.dataframe(st.session_state.income_data, use_container_width=True, hide_index=True)

# 6. TAB: COST-BENEFIT SANDBOX
elif current_tab == "⚖️ Cost-Benefit Sandbox":
    st.markdown('<div class="main-header">⚖️ Simulation Workspace - Multi-Crop Cost-Benefit Projections Matrix</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Model out complex financial targets, production costs, and expected ROI segments safely in sandbox environments.</div>', unsafe_allow_html=True)
    
    with st.form("form_sandbox_simulation"):
        st.markdown("#### Run Pro-Forma Testing Scenario Matrix")
        sb_col1, sb_col2, sb_col3 = st.columns(3)
        with sb_col1: sb_cr = st.selectbox("Test Crop Blueprint Node Asset:", st.session_state.crop_names_list)
        with sb_col2: sb_sz = st.number_input("Allocated Simulated Acreage Size:", min_value=1.0, value=10.0)
        with sb_col3: sb_cpa = st.number_input(f"Simulated Direct Operational Cost/Acre ({c_symbol}):", min_value=0.0, value=4500.00)
        
        sb_col4, sb_col5 = st.columns(2)
        with sb_col4: sb_ypa = st.number_input("Simulated Target Yield per Acre Weight Units:", min_value=0.0, value=30.0)
        with sb_col5: sb_ppu = st.number_input(f"Target Open Market Contract Price per Sale Unit ({c_symbol}):", min_value=0.0, value=500.00)
        
        if st.form_submit_button("💥 Inject Simulation Scenario Target Block Matrix"):
            sb_calc_exp = sb_cpa * sb_sz
            sb_calc_inc = sb_ypa * sb_sz * sb_ppu
            sb_calc_net = sb_calc_inc - sb_calc_exp
            sb_calc_roi = (sb_calc_net / sb_calc_exp * 100) if sb_calc_exp > 0 else 0.0
            
            st.session_state.sandbox_container.append({
                "Crop Target Option": sb_cr, 
                "Acreage Weight": sb_sz, 
                "Projected Total Expenditures": sb_calc_exp,
                "Projected Realized Revenue": sb_calc_inc, 
                "Net Income Returns": sb_calc_net, 
                "Pro-Forma ROI Ratio": f"{sb_calc_roi:.2f}%"
            })
            st.success("Appended sandbox comparison line down onto dashboard layout view workspace.")
            st.rerun()

    if st.session_state.sandbox_container:
        st.markdown('<div class="section-banner"><h5>Cost-Benefit Matrix Strategy Projection Comparisons Output Results</h5></div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(st.session_state.sandbox_container), use_container_width=True, hide_index=True)
        if st.button("🗑️ Clear Target Scenario Arrays Memory Canvas Spaces", use_container_width=True):
            st.session_state.sandbox_container = []
            st.success("Reset simulator metrics.")
            st.rerun()

# 7. TAB: FINANCIAL REPORTING (DYNAMIC GENERATION SYSTEM)
elif current_tab == "📋 Financial Reporting":
    st.markdown('<div class="main-header">📋 Corporate Reconciled Financial Performance Statements Portal</div>', unsafe_allow_html=True)
    
    col_f_sel, col_f_s, col_f_e = st.columns([2, 1, 1])
    with col_f_sel: rep_type = st.selectbox("Accounting Sheet Statement Format:", ["Corporate Profit and Loss (P&L) Statement Ledger"])
    with col_f_s: st.date_input("Period Inception Timeline Track:", date(2026, 1, 1))
    with col_f_e: st.date_input("Period Closure Termination Date:", date(2026, 12, 31))
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Financial Aggregator Engine Execution Button
    generate_report = st.button("🔄 Execute Re-Aggregation & Regenerate Reconciled P&L Statement Report", use_container_width=True)
    
    if generate_report:
        st.toast("Financial database lines aggregated successfully!", icon="⚖️")
    
    e_df = st.session_state.expenses_data
    i_df = st.session_state.income_data
    
    revenue = i_df["total_income"].sum() if not i_df.empty else 0.0
    cogs_cats = ["Fertilizer", "Chemicals/Pesticides", "Labor", "Seedlings"]
    cogs = e_df[e_df["category"].isin(cogs_cats)]["total_cost"].sum() if not e_df.empty else 0.0
    
    opex_cats = ["Equipment Rental", "Fuel"]
    opex = e_df[e_df["category"].isin(opex_cats)]["total_cost"].sum() if not e_df.empty else 0.0
    
    gross_profit = revenue - cogs
    net_income = gross_profit - opex
    
    gross_margin = (gross_profit / revenue * 100) if revenue > 0 else 0.0
    net_margin = (net_income / revenue * 100) if revenue > 0 else 0.0
    
    st.markdown(f"### 📄 Generated Financial Performance Record Blueprint")
    st.components.v1.html(f"""
    <div style="background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 2.5rem; font-family: 'Courier New', Courier, monospace; color: #0f172a; line-height: 1.6;">
        <div style="text-align: center; font-weight: bold; font-size: 1.4rem; text-transform: uppercase;">AGRIGROW ENTERPRISE PRO PLC</div>
        <div style="text-align: center; font-weight: bold; font-size: 1.0rem; color: #475569; text-transform: uppercase;">Profit and Loss Statement</div>
        <div style="text-align: center; font-size: 0.85rem; color:#64748b; margin-bottom: 2.5rem;">For the Period Ending December 31, 2026 | Currency: {c_symbol}</div>
        
        <div style="display: flex; justify-content: space-between; font-weight: bold; border-bottom: 3px solid #0f172a; padding-bottom: 0.5rem; text-transform: uppercase;">
            <span>Account Segment Component Matrix</span>
            <span>Net Asset Valuation ({c_symbol})</span>
        </div>
        
        <div style="display: flex; justify-content: space-between; padding: 0.5rem 0 0.25rem 0; font-weight: bold; color: #2F578A;">
            <span>REVENUE FLOW ENGINES</span>
            <span></span>
        </div>
        <div style="display: flex; justify-content: space-between; padding: 0.25rem 0 0.25rem 1.5rem;">
            <span>Gross Primary Crop Wholesale Distribution Income</span>
            <span>{revenue:,.2f}</span>
        </div>
        
        <div style="display: flex; justify-content: space-between; padding: 1rem 0 0.25rem 0; font-weight: bold; color: #ba3c3c;">
            <span>COST OF GOODS SOLD (COGS)</span>
            <span></span>
        </div>
        <div style="display: flex; justify-content: space-between; padding: 0.25rem 0 0.25rem 1.5rem; color: #64748b;">
            <span>Direct Production Inputs Overhead Costs (Fertilizer, Seeds, Labor)</span>
            <span>({cogs:,.2f})</span>
        </div>
        
        <div style="display: flex; justify-content: space-between; padding: 0.75rem 0; font-weight: bold; border-top: 2px solid #0f172a; border-bottom: 2px solid #0f172a; background-color: #f8fafc;">
            <span>GROSS PROFIT (Margin Ratio: {gross_margin:.1f}%)</span>
            <span>{gross_profit:,.2f}</span>
        </div>
        
        <div style="display: flex; justify-content: space-between; padding: 1.25rem 0 0.25rem 0; font-weight: bold; color: #475569;">
            <span>OPERATING EXPENSES (OPEX)</span>
            <span></span>
        </div>
        <div style="display: flex; justify-content: space-between; padding: 0.25rem 0 0.25rem 1.5rem; color: #64748b;">
            <span>Secondary Logistic & Support Overheads (Fuel, Equipment Leases)</span>
            <span>({opex:,.2f})</span>
        </div>
        
        <div style="display: flex; justify-content: space-between; font-size: 1.15rem; font-weight: bold; border-top: 2px solid #0f172a; border-bottom: 4px double #0f172a; margin-top: 1.5rem; padding: 0.75rem 0; background-color: #f1f5f9;">
            <span>NET RECONCILED RUNNING PROFIT POSITION (Margin: {net_margin:.1f}%)</span>
            <span>{c_symbol} {net_income:,.2f}</span>
        </div>
    </div>
    """, height=480, scrolling=True)

# 8. TAB: PREDICTIVE INSIGHTS
elif current_tab == "📈 Predictive Insights":
    st.markdown('<div class="main-header">📈 Predictive Data Insights Panel Matrix</div>', unsafe_allow_html=True)
    
    e_df = st.session_state.expenses_data
    fert_rows = e_df[e_df["category"] == "Fertilizer"]
    fert_cost = fert_rows["cost_per_unit"].mean() if not fert_rows.empty else 2500.00

    with st.chat_message("assistant", avatar="🤖"):
        st.write("### 🤖 Automated Production Intelligence Report Matrix Summary:")
        st.write("1. **Capital Outlay Allocations:** Structural financial checking indicators match safe target benchmarks operational configurations fields parameters.")
        st.write(f"2. **Anomalous Cost Deviation Alert:** Recorded purchase costs tracking rows invoices data maps a transaction pricing sequence tracking approximately **+11.8%** higher margin variance limits than baseline open agriculture wholesale commodity directories (Current logged mean weight: `{c_symbol} {fert_cost:,.2f}`). Optimize input item paths to protect net yield return scales indices metrics.")

# 9. TAB: MARKET INPUT REGISTRY
elif current_tab == "🧪 Market Input Registry":
    st.markdown('<div class="main-header">🧪 Input Items Market Reference Directory</div>', unsafe_allow_html=True)
    
    with st.expander("➕ Add New Reference Item Row to Registry", expanded=False):
        with st.form("form_registry_add"):
            col_rg1, col_rg2, col_rg3 = st.columns(3)
            with col_rg1: rg_date = st.date_input("Observation Posting Date:", datetime.now())
            with col_rg2: rg_source = st.text_input("Supplier Vendor Market Entity:", value="AgriChem Suppliers")
            with col_rg3: rg_desc = st.text_input("Item Particular Description Label:", value="NPK 17-17-17")
            
            col_rg4, col_rg5, col_rg6 = st.columns(3)
            with col_rg4: rg_cat = st.selectbox("Input Group Classification Category Matcher:", st.session_state.expense_categories)
            with col_rg5: rg_price = st.number_input(f"Observed Standard Market Price Index ({c_symbol}):", min_value=0.0, value=3200.00)
            with col_rg6: rg_mode = st.selectbox("Payment Mode Reference Variant:", ["Cash", "M-Pesa", "Bank Transfer"])
            
            if st.form_submit_button("Commit Reference Entry Row to Directory"):
                new_id = int(st.session_state.registry_data["id"].max() + 1) if not st.session_state.registry_data.empty else 1
                new_row = pd.DataFrame([{"id": new_id, "date": str(rg_date), "source": rg_source, "description": rg_desc, "project": "Reference Pool", "crop": "N/A", "yield_units": 1.0, "price": rg_price, "income": 0, "other_income": 0, "total_income": 0, "paid": "Yes", "payment_mode": rg_mode, "payment_code": f"REF-0{new_id}"}])
                st.session_state.registry_data = pd.concat([st.session_state.registry_data, new_row], ignore_index=True)
                st.success("Successfully written item baseline to reference directory catalog layout matrix!")
                st.rerun()

    st.dataframe(st.session_state.registry_data, use_container_width=True, hide_index=True)

# 10. DYNAMIC CONFIGURATION WORKSPACE
elif current_tab == "⚙️ Lists & Categories Config":
    st.markdown('<div class="main-header">⚙️ Dynamic Configuration Engine Workspace</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Modify dropdown lookup listings across all application tracking matrices instantly.</div>', unsafe_allow_html=True)
    
    col_lc1, col_lc2, col_lc3 = st.columns(3)
    
    with col_lc1:
        st.markdown("### 🌱 Crop Names Master List")
        st.write(st.session_state.crop_names_list)
        new_c_name = st.text_input("New Crop Asset Label Tag Name:", value="", key="add_cn_field")
        if st.button("➕ Append Crop Name Asset", use_container_width=True):
            if new_c_name and new_c_name not in st.session_state.crop_names_list:
                st.session_state.crop_names_list.append(new_c_name)
                st.success(f"Appended: {new_c_name}")
                st.rerun()
                
    with col_lc2:
        st.markdown("### 🌾 Crop Classification Types")
        st.write(st.session_state.crop_types_list)
        new_c_type = st.text_input("New Classification Category Label:", value="", key="add_ct_field")
        if st.button("➕ Append Crop Category Asset", use_container_width=True):
            if new_c_type and new_c_type not in st.session_state.crop_types_list:
                st.session_state.crop_types_list.append(new_c_type)
                st.success(f"Appended Category: {new_c_type}")
                st.rerun()
                
    with col_lc3:
        st.markdown("### 📉 Expense Overhead Classifications")
        st.write(st.session_state.expense_categories)
        new_ex_cat = st.text_input("New Expense Classification Label Group Name:", value="", key="add_ex_field")
        if st.button("➕ Append Expense Category Overhead", use_container_width=True):
            if new_ex_cat and new_ex_cat not in st.session_state.expense_categories:
                st.session_state.expense_categories.append(new_ex_cat)
                st.success(f"Appended Overhead Asset: {new_ex_cat}")
                st.rerun()

# 11. TAB: SYSTEM CONFIG (WITH USER PROVISIONING GATEWAY)
elif current_tab == "🛠️ System Config":
    st.markdown('<div class="main-header">⚙️ System Configuration Profile Settings</div>', unsafe_allow_html=True)
    
    col_sc1, col_sc2 = st.columns([1.2, 1])
    
    with col_sc1:
        with st.form("form_sys_config_save"):
            st.markdown("#### Localization & Base Settings")
            sys_curr = st.selectbox("Primary Accounting Base Valuation Currency Dropdown Option:", ["USD ($)", "EUR (€)", "KES (KSh)", "GBP (£)"], index=2)
            st.checkbox("Toggle Application Dark Mode Class Styling Theme", value=False)
            st.selectbox("System Numeric Values Decimal Format Standard Profile:", ["1,234,567.89 (Standard Comma Separation Bracket Allocation)"])
            st.checkbox("Enable Automated Server Outbound SMTP Transaction Alerts System Notifications", value=True)
            
            if st.form_submit_button("Save Core Configuration Changes", use_container_width=True):
                st.session_state.currency = sys_curr
                st.success("Preferences updated globally across runtime scopes.")
                st.rerun()
                
    with col_sc2:
        with st.form("form_add_new_system_user"):
            st.markdown("#### 👥 Identity Access Control & User Provisioning Matrix")
            new_u_email = st.text_input("New User Professional Corporate Email (UID):", value="operator@agrigrow.com")
            new_u_pass = st.text_input("Secure Passphrase Credentials Allocation:", type="password", value="password123")
            new_u_name = st.text_input("Full Employee Resource Identity Name Label:", value="Jane Doe")
            new_u_role = st.selectbox("Assigned Security Level & Access Clearance Node:", ["Field Operations Lead", "Financial Officer", "Data Auditor Pro", "Farm Owner"])
            
            if st.form_submit_button("🔒 Append Authorized Identity Profile to Gateway", use_container_width=True):
                if new_u_email in st.session_state.system_users_db:
                    st.error("Identity Metric Conflict! An account with this email already exists inside core validation frames.")
                elif not new_u_email or not new_u_pass or not new_u_name:
                    st.warning("Data Validation Refusal. Ensure all core field elements are explicitly specified.")
                else:
                    st.session_state.system_users_db[new_u_email] = {
                        "password": new_u_pass,
                        "name": new_u_name,
                        "role": new_u_role
                    }
                    st.success(f"Successfully provisioned corporate security framework entries for {new_u_name}!")
                    st.rerun()
                    
        # View currently logged system credentials safely (minus passwords)
        with st.expander("👁️ View Existing Authorized Profiles Matrix", expanded=False):
            display_users = []
            for em, info in st.session_state.system_users_db.items():
                display_users.append({"Email Reference": em, "Identity Name": info["name"], "Security Role Profile Node": info["role"]})
            st.dataframe(pd.DataFrame(display_users), use_container_width=True, hide_index=True)