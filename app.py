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

# Shared Stylesheet for an Elegant, Modern Corporate Design
st.markdown("""
    <style>
    /* Global Overrides */
    .main-header { font-size: 2rem; color: #1e3a1e; font-weight: 700; margin-bottom: 1.5rem; }
    .section-banner { background-color: #f8fafc; padding: 0.75rem 1.25rem; border-radius: 6px; border-left: 4px solid #1e3a1e; margin-bottom: 1.25rem; }
    
    /* Modern Dashboard Metric Cards */
    .card-metric { background-color: #ffffff; padding: 1.2rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; }
    .metric-num { font-size: 1.6rem; font-weight: 700; color: #0f172a; margin-top: 0.25rem; }
    .metric-titl { font-size: 0.8rem; color: #64748b; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; }
    
    /* Sidebar Overhaul Fixes - Removing Narrow Overflows */
    [data-testid="stSidebar"] {
        min-width: 340px !important;
        max-width: 340px !important;
    }
    [data-testid="stSidebarUserContent"] {
        padding: 1.5rem 1rem !important;
    }
    .sidebar-card { 
        background-color: #ffffff; 
        padding: 0.85rem; 
        border-radius: 6px; 
        margin: 0.25rem 0; 
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    }
    .sidebar-text { font-size: 0.85rem; color: #334155; margin: 4px 0; line-height: 1.4; }
    
    /* Force Radio Options to Wrap Elegantly */
    div[data-testid="stRadio"] > label {
        font-weight: 600 !important;
        color: #1e3a1e !important;
    }
    
    /* Prevent Button Text Overflow & Enable Wrapping */
    div[data-testid="stWidgetFormSubmitButton"] > button {
        width: 100% !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        height: auto !important;
        padding: 0.5rem 1rem !important;
    }
    div[data-testid="stWidgetFormSubmitButton"] p {
        white-space: normal !important;
        word-break: break-word !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. STATE INITIALIZATION (PURE IN-MEMORY ENGINE) ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'currency' not in st.session_state:
    st.session_state.currency = "KES (KSh)"

if 'sandbox_container' not in st.session_state:
    st.session_state.sandbox_container = []

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

crop_types = ["Cereal", "Vegetable", "Fruit", "Cash Crop", "Legume"]
expense_categories = ["Fertilizer", "Chemicals/Pesticides", "Labor", "Equipment Rental", "Seedlings", "Fuel"]

# Localized Currency Extraction Helper
c_symbol = st.session_state.currency.split(" ")[1].replace("(", "").replace(")", "")

def trigger_toast(message):
    st.toast(f"✔ Action: {message}", icon="💼")

# --- 3. SIGN-IN ACCESS CONTROL ENFORCEMENT ---
if not st.session_state.authenticated:
    st.markdown('<div class="main-header">🔑 Corporate Access Portal</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("login_gate"):
            st.subheader("Login Credentials Required")
            uid = st.text_input("Email Address", value="admin@agrigrow.com")
            pwd = st.text_input("Password", type="password", value="password")
            if st.form_submit_button("Authenticate Sign-In", use_container_width=True):
                if uid == "admin@agrigrow.com" and pwd == "password":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Authentication rejected. Invalid credentials entered.")
    st.stop()

# --- 4. SYSTEM CONSOLE NAVIGATION WITH FIXED OVERLAYS ---
with st.sidebar:
    st.markdown("### 🌾 Management Console")
    
    # 🗂️ MAIN SYSTEM NAVIGATION
    current_tab = st.radio("Select Workspace Tab:", [
        "📊 Dashboard", "🌱 Crops Registry", "🏗️ Projects Manager", 
        "📉 Expenses Tracker", "💰 Income Ledger", "⚖️ Cost-Benefit Sandbox", 
        "📋 Financial Reporting", "📈 Predictive Insights", "🧪 Market Input Registry", "⚙️ System Config"
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
                <div class="sidebar-text"><b>Memory Mode:</b> <span style='color:green; font-weight:bold;'>Active</span></div>
                <div class="sidebar-text"><b>Server Latency:</b> 4ms</div>
                <div class="sidebar-text"><b>Active Workers:</b> Local Canvas</div>
            </div>
        """, unsafe_allow_html=True)
        
    # 👤 3. USER PROFILE COMPONENT CARD
    with st.expander("👤 User Profile Frame", expanded=True):
        st.markdown(f"""
            <div class="sidebar-card" style="border-left: 3px solid #1e3a1e;">
                <div class="sidebar-text"><b>Identity:</b> Administrator</div>
                <div class="sidebar-text"><b>System Role:</b> Data Auditor Pro</div>
                <div class="sidebar-text"><b>Active Tab:</b> {current_tab}</div>
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
        color = "#16a34a" if calc_net_prof >= 0 else "#dc2626"
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
        fig_cf = px.bar(cf_df, x="Stream", y="Value", color="Stream", template="plotly_white", color_discrete_sequence=["#1e3a1e", "#ba3c3c", "#4180ab"])
        st.plotly_chart(fig_cf, use_container_width=True)
        
    with graph_col2:
        st.subheader("Expense Distribution per Category")
        if not e_df.empty:
            cat_totals = e_df.groupby("category")["total_cost"].sum().reset_index()
            fig_pie = px.pie(cat_totals, values="total_cost", names="category", hole=0.4, color_discrete_sequence=px.colors.sequential.Darkmint)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No recorded expense entries match your selection criteria.")

# 2. TAB: CROPS REGISTRY
elif current_tab == "🌱 Crops Registry":
    st.markdown('<div class="main-header">🌱 Global Crops Registry</div>', unsafe_allow_html=True)
    
    c_df = st.session_state.crops_data

    # 🌟 SINGLE CONSOLIDATED COLLAPSIBLE EXPANDER WINDOW FOR CROP MANAGEMENT TOOLS
    with st.expander("⚙️ Manage Crop Profiles", expanded=False):
        st.markdown("#### 📝 Register a New Crop Profile Type")
        with st.form("form_crop_add"):
            col_cr1, col_cr2, col_cr3 = st.columns(3)
            with col_cr1: cr_name = st.selectbox("Crop Name:", ["Maize", "Wheat", "Tomatoes", "Coffee", "Potatoes", "Barley", "Rice", "Sugarcane", "Beans"])
            with col_cr2: cr_type = st.selectbox("Crop Type / Category:", crop_types)
            with col_cr3: cr_season = st.text_input("Growing Season:", value="Main Season 2026")
                
            col_cr4, col_cr5, col_cr6 = st.columns(3)
            with col_cr4: cr_yield = st.number_input("Avg Yield per Acre:", min_value=0.0, value=35.0)
            with col_cr5: cr_price = st.number_input(f"Market Price per Unit ({c_symbol}):", min_value=0.0, value=450.00)
            with col_cr6: cr_cost = st.number_input(f"Avg Production Cost per Acre ({c_symbol}):", min_value=0.0, value=5000.00)

            cr_calc_inc = cr_yield * cr_price
            cr_calc_ret = cr_calc_inc - cr_cost
            st.markdown(f"**⚡ Real-Time Estimation Context:** Gross Revenue/Acre: `{c_symbol} {cr_calc_inc:,.2f}` | Net Return/Acre: `{c_symbol} {cr_calc_ret:,.2f}`")
            
            if st.form_submit_button("Save Crop Profile"):
                new_id = int(st.session_state.crops_data["id"].max() + 1) if not st.session_state.crops_data.empty else 1
                new_row = pd.DataFrame([{"id": new_id, "crop_name": cr_name, "crop_type": cr_type, "growing_season": cr_season, "yield_acre": cr_yield, "market_price": cr_price, "cost_acre": cr_cost, "income_acre": cr_calc_inc, "net_returns": cr_calc_ret}])
                st.session_state.crops_data = pd.concat([st.session_state.crops_data, new_row], ignore_index=True)
                st.success("Crop baseline profile successfully added.")
                st.rerun()

        st.markdown("---")
        st.markdown("#### 📥 Bulk Ingest Crops Data Portal")
        uploaded_crops_file = st.file_uploader("Upload structured CSV tracking lines directly:", type=["csv"], key="bulk_uploader_crops_csv")
        if uploaded_crops_file is not None:
            try:
                csv_crops_df = pd.read_csv(uploaded_crops_file)
                st.session_state.crops_data = pd.concat([st.session_state.crops_data, csv_crops_df], ignore_index=True)
                st.success("Successfully processed and committed raw CSV data to crop matrices.")
                st.rerun()
            except Exception as e:
                st.error(f"Ingestion processing failure: {str(e)}")

        st.markdown("---")
        st.markdown("#### 📤 Export Crop Register Arrays")
        if not c_df.empty:
            excel_crops_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_crops_buffer, engine="xlsxwriter") as xl_crops_writer:
                c_df.to_excel(xl_crops_writer, index=False, sheet_name="Crop_Profiles")
            st.download_button(label="📤 Download Comprehensive Crops Register Excel Sheet (.xlsx)", data=excel_crops_buffer.getvalue(), file_name="Crops_Report.xlsx", use_container_width=True)
        else:
            st.warning("No recorded data rows exist inside memory schemas to build crop profile sheets.")

    st.markdown('<div class="section-banner"><h5>Registered System Crops Base Metrics</h5></div>', unsafe_allow_html=True)
    st.dataframe(st.session_state.crops_data, use_container_width=True)

# 3. TAB: PROJECTS MANAGER
elif current_tab == "🏗️ Projects Manager":
    st.markdown('<div class="main-header">🏗️ Production Field Project Matrix</div>', unsafe_allow_html=True)
    
    p_df = st.session_state.projects_data
    crops_list = list(st.session_state.crops_data["crop_name"].unique()) if not st.session_state.crops_data.empty else ["Maize"]

    # SINGLE CONSOLIDATED COLLAPSIBLE EXPANDER WINDOW FOR FIELD OPERATIONS MANAGEMENT
    with st.expander("⚙️ Manage Field Projects", expanded=False):
        st.markdown("#### 📝 Launch a New Field Project Operation Block")
        with st.form("form_proj_add"):
            col_pr1, col_pr2, col_pr3 = st.columns(3)
            with col_pr1: pr_name = st.text_input("Project / Field Name Identifier:")
            with col_pr2: pr_crop = st.selectbox("Assigned Focus Crop Asset:", crops_list)
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
    st.dataframe(st.session_state.projects_data, use_container_width=True)

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
        st.markdown(f'<div class="card-metric" style="border-left: 4px solid #dc2626;"><div class="metric-titl">Total Expenses Ledger Invoiced</div><div class="metric-num">{c_symbol} {ex_tot:,.2f}</div></div>', unsafe_allow_html=True)
    with eb2:
        st.markdown(f'<div class="card-metric" style="border-left: 4px solid #16a34a;"><div class="metric-titl">Fully Settle Paid Outflows</div><div class="metric-num">{c_symbol} {ex_paid:,.2f}</div></div>', unsafe_allow_html=True)
    with eb3:
        st.markdown(f'<div class="card-metric" style="border-left: 4px solid #ea580c;"><div class="metric-titl">Outstanding Accounts Payable</div><div class="metric-num">{c_symbol} {ex_unpaid:,.2f}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # SINGLE CONSOLIDATED COLLAPSIBLE EXPANDER WINDOW FOR TRANSACTION MANAGEMENT TOOLS
    with st.expander("⚙️ Manage Expense Transactions", expanded=False):
        st.markdown("#### 📝 Manual Transaction Line Entry Form")
        with st.form("form_exp_add"):
            col_ex1, col_ex2, col_ex3 = st.columns(3)
            with col_ex1: ex_date = st.date_input("Transaction Value Date:", datetime.now())
            with col_ex2:
                proj_options = list(p_df["project_name"].unique()) if not p_df.empty else ["West Field Maize"]
                ex_proj = st.selectbox("Link to Active Project Area Unit Node:", proj_options)
            with col_ex3: ex_desc = st.text_input("Expense Item / Line Notation Description:")
                
            col_ex4, col_ex5, col_ex6 = st.columns(3)
            with col_ex4: ex_cat = st.selectbox("Expense Category Overhead Classification Group:", expense_categories)
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
                st.success("Invoiced transaction item saved cleanly to storage.")
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
    st.dataframe(st.session_state.expenses_data, use_container_width=True)

# 5. TAB: INCOME LEDGER
elif current_tab == "💰 Income Ledger":
    st.markdown('<div class="main-header">💰 Yield Sales & Receivables Revenue Inflows Ledger Workspace</div>', unsafe_allow_html=True)
    
    i_df = st.session_state.income_data
    p_df = st.session_state.projects_data
    crops_list = list(st.session_state.crops_data["crop_name"].unique()) if not st.session_state.crops_data.empty else ["Maize"]

    # SINGLE CONSOLIDATED COLLAPSIBLE EXPANDER WINDOW FOR REVENUE MANAGEMENT TOOLS
    with st.expander("⚙️ Manage Income Transactions", expanded=False):
        st.markdown("#### 📝 Log Yield Sales Order Commercial Valuation Receivables Receipts")
        with st.form("form_inc_add"):
            col_in1, col_in2, col_in3 = st.columns(3)
            with col_in1: in_date = st.date_input("Value Receipt Transaction Date:", datetime.now())
            with col_in2: in_src = st.text_input("Procurement B2B Buyer Corporation Name Identifier:")
            with col_in3: in_desc = st.text_input("Transaction Particulars Description Memorandum Note:")
                
            col_in4, col_in5, col_in6 = st.columns(3)
            with col_in4: in_proj = st.selectbox("Link Activity Tracking to Field Production Project Instance:", list(p_df["project_name"].unique()) if not p_df.empty else ["West Field Maize"])
            with col_in5: in_crop = st.selectbox("Cultivated Commodity Classification Asset Profile Context:", crops_list)
            with col_in6: in_yield = st.number_input("Dispatched Cargo Unit Output Weights Volume counts Sold:", min_value=0.0, value=10.0)
                
            col_in7, col_in8, col_in9 = st.columns(3)
            with col_in7: in_price = st.number_input(f"Agreed Spot Market Realized Price Value Allocation Metric per Unit ({c_symbol}):", min_value=0.0, value=450.00)
            with col_in8: in_other = st.number_input(f"Subsidiary Logistics Revenue / Crop Biomass Supplementary Gains ({c_symbol}):", min_value=0.0, value=0.00)
            with col_in9: in_paid = st.selectbox("Payment Settlement Clearance Inward Status Flag Picker Token:", ["Paid", "Unpaid"])
                
            col_in10, col_in11 = st.columns(2)
            with col_in10: in_mode = st.selectbox("Financial Settlement Interbank Channels Mode Alternative Options:", ["Bank", "MPesa", "Cash", "Cheque"])
            with col_in11: in_code = st.text_input("Electronic Ledger Clearing Reference Trace Code:", value="EFT-REF-74239")

            calc_in_amt = in_yield * in_price
            calc_in_tot = calc_in_amt + in_other
            st.markdown(f"**⚡ Live Inflow Revenue Calculations Check:** Core Cargo Value Realized: `{c_symbol} {calc_in_amt:,.2f}` | Gross Balance Cash Inflow Total realized: `{c_symbol} {calc_in_tot:,.2f}`")
            
            if st.form_submit_button("Record incoming revenue cash flows statement item"):
                new_id = int(st.session_state.income_data["id"].max() + 1) if not st.session_state.income_data.empty else 1
                new_row = pd.DataFrame([{"id": new_id, "date": str(in_date), "source": in_src, "description": in_desc, "project": in_proj, "crop": in_crop, "yield_units": in_yield, "price": in_price, "amount": calc_in_amt, "other_income": in_other, "total_income": calc_in_tot, "paid": in_paid, "payment_mode": in_mode, "payment_code": in_code}])
                st.session_state.income_data = pd.concat([st.session_state.income_data, new_row], ignore_index=True)
                st.success("Successfully logged commercial trading transaction settlement event entry.")
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
    st.dataframe(st.session_state.income_data, use_container_width=True)

# 6. TAB: COST-BENEFIT SANDBOX
elif current_tab == "⚖️ Cost-Benefit Sandbox":
    st.markdown('<div class="main-header">⚖️ Simulation Workspace - Multi-Crop Cost-Benefit Analysis Projections Modeling</div>', unsafe_allow_html=True)
    
    with st.form("form_sandbox_simulation"):
        st.markdown("**Add Asset Test Configuration Setup Scenario Metrics Block Frame Settings**")
        sb_col1, sb_col2, sb_col3, sb_col4, sb_col5 = st.columns(5)
        with sb_col1: sb_cr = st.text_input("Test Crop Label Identification Code Name:", value="Experimental Wheat Variant")
        with sb_col2: sb_sz = st.number_input("Test Size (Acres):", min_value=1.0, value=15.0)
        with sb_col3: sb_cpa = st.number_input(f"Simulated Cost per Acre ({c_symbol}):", min_value=0.0, value=4500.00)
        with sb_col4: sb_ypa = st.number_input("Simulated Yield per Acre:", min_value=0.0, value=35.0)
        with sb_col5: sb_ppu = st.number_input(f"Projected Price per Unit ({c_symbol}):", min_value=0.0, value=500.00)
        
        if st.form_submit_button("💥 Inject Target Sandbox Test Case Parameter Setup Object Into Memory"):
            sb_calc_exp = sb_cpa * sb_sz
            sb_calc_inc = sb_ypa * sb_sz * sb_ppu
            sb_calc_net = sb_calc_inc - sb_calc_exp
            sb_calc_roi = (sb_calc_net / sb_calc_exp * 100) if sb_calc_exp > 0 else 0.0
            
            st.session_state.sandbox_container.append({
                "Scenario Label": sb_cr, "Acreage Allocation": sb_sz, "Simulated Total Expenditures": sb_calc_exp,
                "Simulated Gross Revenue": sb_calc_inc, "Net Returns Forecast": sb_calc_net, "ROI Ratio Index": f"{sb_calc_roi:.1f}%"
            })
            st.success("Appended scenario configurations profile definition.")
            st.rerun()

    if st.session_state.sandbox_container:
        st.markdown('<div class="section-banner"><h5>Cost-Benefit Matrix Strategy Projection Comparisons Output Results Tables</h5></div>', unsafe_allow_html=True)
        st.table(pd.DataFrame(st.session_state.sandbox_container))
        if st.button("🗑️ Reset Simulator Configuration Environment Canvas Spaces"):
            st.session_state.sandbox_container = []
            st.success("Reset simulator space workspace layouts.")
            st.rerun()

# 7. TAB: FINANCIAL REPORTING
elif current_tab == "📋 Financial Reporting":
    st.markdown('<div class="main-header">📋 Corporate Accounting Financial Statements Portal</div>', unsafe_allow_html=True)
    
    col_f_sel, col_f_s, col_f_e = st.columns([2, 1, 1])
    with col_f_sel:
        rep_type = st.selectbox("Report Template Model:", [
            "Corporate Profit and Loss (P&L) Statement",
            "Global Enterprise Financial Summary Abstract"
        ])
    with col_f_s: st.date_input("Period Start Date:", date(2026, 1, 1))
    with col_f_e: st.date_input("Period End Date:", date(2026, 12, 31))
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🏭 Generate Statement Report Manifest", use_container_width=True):
        e_df = st.session_state.expenses_data
        i_df = st.session_state.income_data
        
        # Calculate accounting baseline vectors
        revenue = i_df["total_income"].sum() if not i_df.empty else 0.0
        
        # COGS components: Direct Field Production inputs (Fertilizers, Chemicals, Labor, Seedlings)
        cogs_cats = ["Fertilizer", "Chemicals/Pesticides", "Labor", "Seedlings"]
        cogs = e_df[e_df["category"].isin(cogs_cats)]["total_cost"].sum() if not e_df.empty else 0.0
        
        # Operating Expenses components: Secondary Support Overheads (Fuel, Equipment Hire, Rent)
        opex_cats = ["Equipment Rental", "Fuel"]
        opex = e_df[e_df["category"].isin(opex_cats)]["total_cost"].sum() if not e_df.empty else 0.0
        
        gross_profit = revenue - cogs
        net_income = gross_profit - opex
        
        gross_margin = (gross_profit / revenue * 100) if revenue > 0 else 0.0
        net_margin = (net_income / revenue * 100) if revenue > 0 else 0.0
        
        st.markdown(f"### 📄 Consolidated Financial Performance Manifest")
        
        st.components.v1.html(f"""
        <div style="background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 2.5rem; font-family: 'Courier New', Courier, monospace; box-shadow: 0 1px 3px rgba(0,0,0,0.05); color: #0f172a; line-height: 1.6;">
            <div style="text-align: center; font-weight: bold; font-size: 1.4rem; letter-spacing: 1px; margin-bottom: 0.25rem; text-transform: uppercase;">AGRIGROW ENTERPRISE PRO PLC</div>
            <div style="text-align: center; font-weight: bold; font-size: 1.0rem; margin-bottom: 0.25rem; text-transform: uppercase; color: #475569;">Profit and Loss Statement</div>
            <div style="text-align: center; font-size: 0.85rem; color:#64748b; margin-bottom: 2.5rem;">For the Period Ending December 31, 2026 | Currency: {c_symbol}</div>
            
            <div style="display: flex; justify-content: space-between; font-weight: bold; border-bottom: 3px solid #0f172a; padding-bottom: 0.5rem; text-transform: uppercase; font-size: 0.95rem;">
                <span>Account Classification Segment</span>
                <span>Value Amount ({c_symbol})</span>
            </div>
            
            <div style="display: flex; justify-content: space-between; padding: 0.5rem 0 0.25rem 0; font-weight: bold; font-size: 1rem; color: #1e3a1e;">
                <span>REVENUE</span>
                <span></span>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 0.25rem 0 0.25rem 1.5rem; font-size: 0.95rem;">
                <span>Gross Primary Crop Distribution Sales</span>
                <span>{revenue:,.2f}</span>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 0.4rem 0; font-weight: bold; border-top: 1px solid #cbd5e1; font-size: 0.95rem;">
                <span>Total Net Revenue</span>
                <span>{revenue:,.2f}</span>
            </div>
            
            <div style="display: flex; justify-content: space-between; padding: 1rem 0 0.25rem 0; font-weight: bold; font-size: 1rem; color: #9a3412;">
                <span>COST OF GOODS SOLD (COGS)</span>
                <span></span>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 0.25rem 0 0.25rem 1.5rem; font-size: 0.95rem; color: #64748b;">
                <span>Direct Field Production Overheads (Fertilizer, Seedlings, Labor)</span>
                <span>({cogs:,.2f})</span>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 0.4rem 0; font-weight: bold; border-top: 1px solid #cbd5e1; font-size: 0.95rem;">
                <span>Total Cost of Goods Sold</span>
                <span>({cogs:,.2f})</span>
            </div>
            
            <div style="display: flex; justify-content: space-between; padding: 0.75rem 0; font-weight: bold; border-top: 2px solid #0f172a; border-bottom: 2px solid #0f172a; background-color: #f8fafc; font-size: 1rem; margin-top: 0.5rem;">
                <span>GROSS PROFIT (Margin: {gross_margin:.1f}%)</span>
                <span>{gross_profit:,.2f}</span>
            </div>
            
            <div style="display: flex; justify-content: space-between; padding: 1.25rem 0 0.25rem 0; font-weight: bold; font-size: 1rem; color: #475569;">
                <span>OPERATING EXPENSES (OPEX)</span>
                <span></span>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 0.25rem 0 0.25rem 1.5rem; font-size: 0.95rem; color: #64748b;">
                <span>Secondary Logistics & Resource Overheads (Fuel, Equipment Rental)</span>
                <span>({opex:,.2f})</span>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 0.4rem 0; font-weight: bold; border-top: 1px solid #cbd5e1; font-size: 0.95rem;">
                <span>Total Operating Expenses</span>
                <span>({opex:,.2f})</span>
            </div>
            
            <div style="display: flex; justify-content: space-between; font-size: 1.15rem; font-weight: bold; border-top: 2px solid #0f172a; border-bottom: 4px double #0f172a; margin-top: 1.5rem; padding: 0.75rem 0; background-color: #f1f5f9;">
                <span>NET RECONCILED INCOME POSITION (Margin: {net_margin:.1f}%)</span>
                <span>{c_symbol} {net_income:,.2f}</span>
            </div>
        </div>
        """, height=500, scrolling=True)

# 8. TAB: PREDICTIVE INSIGHTS
elif current_tab == "📈 Predictive Insights":
    st.markdown('<div class="main-header">📈 Predictive Data Insights Panel</div>', unsafe_allow_html=True)
    
    e_df = st.session_state.expenses_data
    fert_rows = e_df[e_df["category"] == "Fertilizer"]
    fert_cost = fert_rows["cost_per_unit"].mean() if not fert_rows.empty else 2500.00

    with st.chat_message("assistant", avatar="🤖"):
        st.write("### 🤖 System Audit Engine Report:")
        st.write("1. **Capital Outlay Allocations:** Expenditure distributions verify safe operational ranges configurations benchmarks indicators.")
        st.write(f"2. **⚠️ Anomalous Cost Deviation Alert:** Fertilizer purchase entry costs row invoices mapping profiles verify an index calculation tracing approximately **+11.8%** higher margin variance deviation trends than open wholesale agricultural commodity directory pricing scales indices (Current average base: {c_symbol} {fert_cost:,.2f}).")

# 9. TAB: MARKET INPUT REGISTRY
elif current_tab == "🧪 Market Input Registry":
    st.markdown('<div class="main-header">🧪 Input Items Market Reference Directory</div>', unsafe_allow_html=True)
    
    st.dataframe(st.session_state.registry_data, use_container_width=True)
    
    with st.expander("➕ Append Reference Data Product Price Catalog", expanded=False):
        with st.form("form_reg_add"):
            col_rg1, col_rg2, col_rg3 = st.columns(3)
            with col_rg1: rg_dt = st.date_input("Audit Date:", date(2026, 5, 22))
            with col_rg2: rg_src = st.text_input("Supplier/Vendor Corporate Name:", value="National AgriSupply Solutions Group")
            with col_rg3: rg_dsc = st.text_input("Product Specification Name:", value="Organic Bio-Active Compound Fertilizer Mix")
            
            col_rg4, col_rg5 = st.columns(2)
            with col_rg4: rg_qty = st.number_input("Standard Packaging Content Size Units:", min_value=1, value=1)
            with col_rg5: rg_prc = st.number_input(f"Observed Present Unit Price ({c_symbol}):", min_value=0.0, value=3500.00)
            
            if st.form_submit_button("Commit Catalog Line Entry to Table"):
                new_id = int(st.session_state.registry_data["id"].max() + 1) if not st.session_state.registry_data.empty else 1
                new_row = pd.DataFrame([{"id": new_id, "date": str(rg_dt), "source": rg_src, "description": rg_dsc, "project": "Reference Benchmark Space", "crop": "Multi-Crop Compatibility", "yield_units": rg_qty, "price": rg_prc, "income": 0, "other_income": 0, "total_income": 0, "paid": "Verified Look Up Object", "payment_mode": "N/A Look Up Entry", "payment_code": "REGISTRY-HASH-92384"}])
                st.session_state.registry_data = pd.concat([st.session_state.registry_data, new_row], ignore_index=True)
                st.success("Appended verified reference data configuration parameters successfully.")
                st.rerun()

# 10. TAB: SYSTEM CONFIG
elif current_tab == "⚙️ System Config":
    st.markdown('<div class="main-header">⚙️ System Configuration Profile Settings</div>', unsafe_allow_html=True)
    
    with st.form("form_sys_config_save"):
        st.subheader("Administrative Access Control")
        st.text_input("Root Admin Identity Email Address:", value="admin@agrigrow.com")
        st.text_input("Master Secure Access Passphrase:", type="password", value="password")
        
        st.markdown("---")
        st.subheader("Global Settings & Localization Options")
        
        # Safe Mapping List
        curr_options = ["USD ($)", "EUR (€)", "KES (KSh)", "GBP (£)", "CAD (C$)"]
        
        # Safeguard the index matching lookup
        if st.session_state.currency in curr_options:
            default_idx = curr_options.index(st.session_state.currency)
        else:
            default_idx = 2 # Default to KES if something went sideways
        
        sys_curr = st.selectbox("Primary Accounting Base Valuation Currency Dropdown Option:", curr_options, index=default_idx)
        st.checkbox("Toggle Application Dark Mode Class Styling Theme", value=False)
        st.selectbox("System Numeric Values Decimal Format Standard Profile:", ["1,234,567.89 (Standard Comma Separation Bracket Allocation)"])
        st.checkbox("Enable Automated Server Outbound SMTP Transaction Alerts System Notifications", value=True)
        
        if st.form_submit_button("Save Core Configuration Changes"):
            # Commit the exact matching option to state safely
            st.session_state.currency = sys_curr
            st.success("Successfully written updated localization preferences globally across runtime environment scopes.")
            st.rerun()