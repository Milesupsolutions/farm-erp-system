import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import io
import sqlite3

# --- 1. SET PAGE CONFIGURATION & APP CONTROLS ---
st.set_page_config(
    page_title="MilesUpFarm ERP",
    page_icon="🚜",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- DATABASE INITIALIZATION ENGINE ---
DB_FILE = "agrigrow_farm_erp.db"

def init_db():
    conn = sqlite3.connect(DB_FILE, timeout=30)
    cursor = conn.cursor()
    
    # 1. Users Security Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        name TEXT NOT NULL,
        role TEXT NOT NULL
    )""")
    
    # Seed baseline users if table is empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO users VALUES (?, ?, ?, ?)", [
            ("admin@agrigrow.com", "password", "Paul Gaitho", "Data Auditor Pro"),
            ("owner@agrigrow.com", "ownerpassword", "Executive Management", "Farm Owner"),
            ("field@agrigrow.com", "fieldpassword", "Emily Mkabili", "Field Operations Lead")
        ])
        
    # 2. Crops Registry Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS crops (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        crop_name TEXT,
        crop_type TEXT,
        growing_season TEXT,
        yield_acre REAL,
        market_price REAL,
        cost_acre REAL,
        income_acre REAL,
        net_returns REAL
    )""")

    # 3. Production Projects Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_name TEXT,
        crop TEXT,
        acreage REAL,
        est_yield_acre REAL,
        est_market_price REAL,
        est_cost_acre REAL,
        estimated_cost REAL,
        estimated_income REAL,
        status TEXT,
        start_date TEXT
    )""")

    # 4. Expenses Tracker Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        project TEXT,
        description TEXT,
        category TEXT,
        uom TEXT,
        units REAL,
        cost_per_unit REAL,
        amount REAL,
        other_charges REAL,
        total_cost REAL,
        paid TEXT
    )""")

    # 5. Revenue / Income Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS income (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        source TEXT,
        description TEXT,
        project TEXT,
        crop TEXT,
        yield_units REAL,
        price REAL,
        amount REAL,
        other_income REAL,
        total_income REAL,
        paid TEXT,
        payment_mode TEXT,
        payment_code TEXT
    )""")

    # 6. Configuration Lists Tables
    cursor.execute("CREATE TABLE IF NOT EXISTS config_crops (name TEXT UNIQUE)")
    cursor.execute("CREATE TABLE IF NOT EXISTS config_projects (name TEXT UNIQUE)")
    cursor.execute("CREATE TABLE IF NOT EXISTS config_categories (name TEXT UNIQUE)")
    cursor.execute("CREATE TABLE IF NOT EXISTS config_crop_types (name TEXT UNIQUE)")
    
    # Seed configuration defaults if completely empty
    cursor.execute("SELECT COUNT(*) FROM config_crops")
    if cursor.fetchone()[0] == 0:
        for c in ["Maize", "Tomatoes", "Coffee", "Wheat", "Potatoes", "Beans"]:
            cursor.execute("INSERT OR IGNORE INTO config_crops VALUES (?)", (c,))
            
    cursor.execute("SELECT COUNT(*) FROM config_projects")
    if cursor.fetchone()[0] == 0:
        for p in ["West Field Project", "East Field Block"]:
            cursor.execute("INSERT OR IGNORE INTO config_projects VALUES (?)", (p,))
            
    cursor.execute("SELECT COUNT(*) FROM config_categories")
    if cursor.fetchone()[0] == 0:
        for cat in ["Fertilizer", "Chemicals/Pesticides", "Labor", "Equipment Rental", "Seedlings", "Fuel"]:
            cursor.execute("INSERT OR IGNORE INTO config_categories VALUES (?)", (cat,))

    cursor.execute("SELECT COUNT(*) FROM config_crop_types")
    if cursor.fetchone()[0] == 0:
        for ct in ["Cereal", "Vegetable", "Fruit", "Cash Crop", "Legume"]:
            cursor.execute("INSERT OR IGNORE INTO config_crop_types VALUES (?)", (ct,))

    conn.commit()
    conn.close()

# Initialize Database Architecture
init_db()

# Global Custom CSS Theme Styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght=300;400;500;600;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { font-family: 'Inter', sans-serif; background-color: #f4f6f9; }
    .main-header { font-size: 2.2rem; color: #1e293b; font-weight: 700; margin-bottom: 0.5rem; letter-spacing: -0.5px; }
    .section-banner { background-color: #ffffff; padding: 1rem 1.25rem; border-radius: 8px; border-left: 5px solid #2F578A; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }
    .section-banner h5 { margin: 0; color: #2F578A; font-weight: 600; }
    .card-metric { background: #ffffff; padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; position: relative; overflow: hidden; }
    .card-metric::before { content: ""; position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: #2F578A; }
    .metric-num { font-size: 1.8rem; font-weight: 700; color: #0f172a; margin-top: 0.5rem; }
    .metric-titl { font-size: 0.75rem; color: #64748b; text-transform: uppercase; font-weight: 700; letter-spacing: 0.8px; }
    [data-testid="stSidebar"] { min-width: 340px !important; background-color: #1e2638 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    div[data-testid="stWidgetFormSubmitButton"] > button { background-color: #2F578A !important; color: white !important; width: 100%; }
    div[data-testid="stForm"] { background-color: #ffffff; padding: 2rem; border-radius: 12px; border: 1px solid #e2e8f0; }
    </style>
""", unsafe_allow_html=True)

# --- 2. CORE DATABASE PIPELINES ---
def run_query(query, params=()):
    with sqlite3.connect(DB_FILE, timeout=30) as conn:
        return pd.read_sql_query(query, conn, params=params)

def execute_db_command(command, params=()):
    with sqlite3.connect(DB_FILE, timeout=30) as conn:
        cursor = conn.cursor()
        cursor.execute(command, params)
        conn.commit()

# Retrieve dynamic list metrics from database config pools
def get_configured_crops():
    return sorted(run_query("SELECT name FROM config_crops")["name"].tolist())

def get_configured_projects():
    return sorted(run_query("SELECT name FROM config_projects")["name"].tolist())

def get_configured_categories():
    return sorted(run_query("SELECT name FROM config_categories")["name"].tolist())

def get_configured_crop_types():
    return sorted(run_query("SELECT name FROM config_crop_types")["name"].tolist())

# Session State Controls
if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'currency' not in st.session_state: st.session_state.currency = "KES (KSh)"
if 'sandbox_container' not in st.session_state: st.session_state.sandbox_container = []

c_symbol = st.session_state.currency.split(" ")[1].replace("(", "").replace(")", "")

# --- 3. LOGIN INTERFACE ACCESS ---
if not st.session_state.authenticated:
    st.markdown("""<style>[data-testid="stSidebar"] { display: none !important; }</style>""", unsafe_allow_html=True)
    st.markdown('<div class="main-header" style="text-align:center; margin-top:5rem;">🌾 MilesUpFarm ERP Login</div>', unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1.2, 1])
    with col2:
        with st.form("login_gate"):
            uid = st.text_input("User Email Address", value="admin@agrigrow.com")
            pwd = st.text_input("Access Passphrase", type="password", value="password")
            if st.form_submit_button("Authenticate Access Path"):
                res = run_query("SELECT name, role, password FROM users WHERE email=?", (uid,))
                if not res.empty and res.iloc[0]["password"] == pwd:
                    st.session_state.authenticated = True
                    st.session_state.user_name = res.iloc[0]["name"]
                    st.session_state.user_role = res.iloc[0]["role"]
                    st.rerun()
                else:
                    st.error("Invalid Login Credentials Specified.")
    st.stop()

# --- 4. NAVIGATION CONSOLE ---
with st.sidebar:
    st.markdown("## 🚜 MilesUpFarm ERP")
    st.markdown("---")
    current_tab = st.radio("System Workspaces:", [
        "📊 Dashboard", "🌱 Crops Registry", "🏗️ Projects Matrix", 
        "📉 Expenses Tracker", "💰 Income Ledger", "⚖️ Cost-Benefit Sandbox", 
        "📋 Financial Reports", "📥 Bulk Data Engine", "📋 List & Categories Config", "⚙️ System Config"
    ])
    st.markdown("---")
    st.markdown(f"User: **{st.session_state.user_name}**")
    if st.button("🚪 Log Out", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# --- 5. WORKSPACE TAB SWITCH ENGINE ---

# 1. TAB: DASHBOARD
if current_tab == "📊 Dashboard":
    st.markdown('<div class="main-header">📊 Operations Dashboard</div>', unsafe_allow_html=True)
    
    e_df = run_query("SELECT * FROM expenses")
    i_df = run_query("SELECT * FROM income")
    
    # Query deployed project logs created explicitly by the user
    deployed_projects_df = run_query("SELECT DISTINCT project_name FROM projects")
    user_created_projects = deployed_projects_df["project_name"].tolist() if not deployed_projects_df.empty else []

    for df in [e_df, i_df]:
        if not df.empty and "date" in df.columns:
            df["parsed_date"] = pd.to_datetime(df["date"], errors="coerce")
            df["Year"] = df["parsed_date"].dt.year.fillna(2026).astype(int).astype(str)
            df["Month"] = df["parsed_date"].dt.strftime("%B").fillna("Unknown")
        else:
            df["Year"] = pd.Series(dtype=str)
            df["Month"] = pd.Series(dtype=str)

    # Filter Bar Configuration
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        p_list = ["All Active Projects"] + sorted(user_created_projects)
        f_proj = st.selectbox("Filter by Created Project:", p_list)
    with fc2:
        all_years = sorted(list(set(e_df["Year"].dropna().tolist() + i_df["Year"].dropna().tolist() + ["2026"])))
        f_year = st.selectbox("Filter by Year Allocation:", ["All Years"] + all_years)
    with fc3:
        months_order = ["All Months", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        f_month = st.selectbox("Filter by Month Cycle:", months_order)

    # Apply Filters
    if f_proj != "All Active Projects":
        e_df = e_df[e_df["project"] == f_proj] if not e_df.empty else e_df
        i_df = i_df[i_df["project"] == f_proj] if not i_df.empty else i_df
    if f_year != "All Years":
        e_df = e_df[e_df["Year"] == f_year] if not e_df.empty else e_df
        i_df = i_df[i_df["Year"] == f_year] if not i_df.empty else i_df
    if f_month != "All Months":
        e_df = e_df[e_df["Month"] == f_month] if not e_df.empty else e_df
        i_df = i_df[i_df["Month"] == f_month] if not i_df.empty else i_df

    total_exp = e_df["total_cost"].sum() if not e_df.empty else 0.0
    total_inc = i_df["total_income"].sum() if not i_df.empty else 0.0
    net_profit = total_inc - total_exp
    margin = (net_profit / total_inc * 100) if total_inc > 0 else 0.0

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1: st.markdown(f'<div class="card-metric"><div class="metric-titl">Expenditures</div><div class="metric-num">{c_symbol} {total_exp:,.2f}</div></div>', unsafe_allow_html=True)
    with kpi2: st.markdown(f'<div class="card-metric"><div class="metric-titl">Revenues</div><div class="metric-num">{c_symbol} {total_inc:,.2f}</div></div>', unsafe_allow_html=True)
    with kpi3: 
        color = "#2F578A" if net_profit >= 0 else "#dc2626"
        st.markdown(f'<div class="card-metric"><div class="metric-titl">Net Gains Position</div><div class="metric-num" style="color:{color};">{c_symbol} {net_profit:,.2f}</div></div>', unsafe_allow_html=True)
    with kpi4: st.markdown(f'<div class="card-metric"><div class="metric-titl">Profit Margin Ratio</div><div class="metric-num">{margin:.1f}%</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    g1, g2 = st.columns(2)
    with g1:
        st.subheader("Cash Flow Balance Analytics")
        st.plotly_chart(px.bar(pd.DataFrame({"Type": ["Income", "Expenses", "Net Profit"], "Value": [total_inc, total_exp, net_profit]}), x="Type", y="Value", color="Type", template="plotly_white"), use_container_width=True)
    with g2:
        st.subheader("Operational Expense Breakdown")
        if not e_df.empty:
            st.plotly_chart(px.pie(e_df.groupby("category")["total_cost"].sum().reset_index(), values="total_cost", names="category", hole=0.4), use_container_width=True)
        else:
            st.info("No expense logs matching filter selections found.")

# 2. TAB: CROPS REGISTRY
elif current_tab == "🌱 Crops Registry":
    st.markdown('<div class="main-header">🌱 Crops Baseline Registry</div>', unsafe_allow_html=True)
    
    configured_crops_options = get_configured_crops()
    configured_types_options = get_configured_crop_types()

    if not configured_crops_options or not configured_types_options:
        st.warning("⚠️ Attention: Please seed options in 'List & Categories Config' first before registering crop matrix items.")
    
    with st.expander("➕ Register a New Crop Profile", expanded=True):
        with st.form("add_crop"):
            c1, c2, c3 = st.columns(3)
            with c1: name = st.selectbox("Crop Variety Name Reference:", configured_crops_options)
            with c2: c_type = st.selectbox("Crop Category:", configured_types_options)
            with c3: season = st.text_input("Production Season Name:", value="2026 Main Season")
            
            c4, c5, c6 = st.columns(3)
            with c4: yld = st.number_input("Average Yield Target per Acre:", min_value=0.0, value=1.0)
            with c5: prc = st.number_input(f"Expected Unit Market Price ({c_symbol}):", min_value=0.0, value=1.0)
            with c6: cst = st.number_input(f"Estimated Production Cost/Acre ({c_symbol}):", min_value=0.0, value=0.0)
            
            if st.form_submit_button("Commit New Crop Registry Row"):
                inc = yld * prc
                ret = inc - cst
                execute_db_command("INSERT INTO crops (crop_name, crop_type, growing_season, yield_acre, market_price, cost_acre, income_acre, net_returns) VALUES (?,?,?,?,?,?,?,?)", (name, c_type, season, yld, prc, cst, inc, ret))
                st.success(f"Crop model '{name}' added successfully.")
                st.rerun()

    crops_df = run_query("SELECT * FROM crops")
    st.dataframe(crops_df, use_container_width=True, hide_index=True)
    if not crops_df.empty:
        with st.expander("🗑️ Wipe Out a Registered Crop Entry"):
            del_id = st.selectbox("Select Target Crop Entry ID to Remove:", crops_df["id"].tolist())
            if st.button("Delete Crop Matrix Block Permanent", type="primary"):
                execute_db_command("DELETE FROM crops WHERE id=?", (del_id,))
                st.rerun()

# 3. TAB: PROJECTS MATRIX
elif current_tab == "🏗️ Projects Matrix":
    st.markdown('<div class="main-header">🏗️ Production Field Project Allocation</div>', unsafe_allow_html=True)
    
    configured_projects_options = get_configured_projects()
    configured_crops_options = get_configured_crops()

    if not configured_projects_options or not configured_crops_options:
        st.warning("⚠️ Attention: Setup your custom Project and Crop names in 'List & Categories Config' first.")

    with st.expander("⚙️ Open New Field Project", expanded=True):
        with st.form("add_project"):
            p1, p2, p3 = st.columns(3)
            with p1: p_name = st.selectbox("Project Area Name Selector:", configured_projects_options)
            with p2: cr_node = st.selectbox("Project Crop:", configured_crops_options)
            with p3: size = st.number_input("Allocated Acreage Size Scale:", min_value=0.1, value=1.0)
            
            p4, p5, p6 = st.columns(3)
            with p4: est_y = st.number_input("Est Yield Capacity / Acre:", min_value=0.0, value=1.0)
            with p5: est_p = st.number_input(f"Target Selling Unit Price ({c_symbol}):", min_value=0.0, value=1.0)
            with p6: est_c = st.number_input(f"Budgetary Input Cost Allocation/Acre ({c_symbol}):", min_value=0.0, value=0.0)
            
            p7, p8 = st.columns(2)
            with p7: status = st.selectbox("Project Lifecycle Phase Status Flag:", ["Proposal", "Ongoing", "Completed"])
            with p8: s_date = st.date_input("Scheduled Project Commencement Date:", datetime.now())
            
            if st.form_submit_button("Deploy Production Field Matrix Instance"):
                tot_c = est_c * size
                tot_i = est_p * est_y * size
                execute_db_command("INSERT INTO projects (project_name, crop, acreage, est_yield_acre, est_market_price, est_cost_acre, estimated_cost, estimated_income, status, start_date) VALUES (?,?,?,?,?,?,?,?,?,?)", (p_name, cr_node, size, est_y, est_p, est_c, tot_c, tot_i, status, str(s_date)))
                st.success(f"Project instance '{p_name}' successfully launched.")
                st.rerun()

    p_df = run_query("SELECT * FROM projects")
    st.dataframe(p_df, use_container_width=True, hide_index=True)
    if not p_df.empty:
        with st.expander("🗑️ Remove Project Block Instance Record"):
            del_id = st.selectbox("Select Target Project Instance ID:", p_df["id"].tolist())
            if st.button("Delete Project Asset Block", type="primary"):
                execute_db_command("DELETE FROM projects WHERE id=?", (del_id,))
                st.rerun()

# 4. TAB: EXPENSES TRACKER
elif current_tab == "📉 Expenses Tracker":
    st.markdown('<div class="main-header">📉 Expenses and Costs</div>', unsafe_allow_html=True)
    with st.expander("⚙️ Record New Expense/Cost", expanded=True):
        with st.form("add_expense"):
            e1, e2, e3 = st.columns(3)
            with e1: ex_date = st.date_input("Expense/Cost Date:", datetime.now())
            with e2: ex_proj = st.selectbox("Project Involved:", get_configured_projects())
            with e3: ex_desc = st.text_input("Expense/Cost Descriptions:")
            
            e4, e5, e6 = st.columns(3)
            with e4: ex_cat = st.selectbox("Expense/Cost Category:", get_configured_categories())
            with e5: ex_uom = st.selectbox("Unit of Measure (UoM):", ["Bags", "Liters", "Hours", "Kgs", "Tonnes", "Units"])
            with e6: ex_qty = st.number_input("Qty:", min_value=0.0, value=1.0)
            
            e7, e8, e9 = st.columns(3)
            with e7: ex_cpu = st.number_input(f"Cost per Unit ({c_symbol}):", min_value=0.0, value=0.0)
            with e8: ex_surch = st.number_input(f"Logistics/Transaction/Others ({c_symbol}):", min_value=0.0, value=0.0)
            with e9: ex_paid = st.selectbox("Paid/Not Paid Status:", ["Paid", "Not Paid"])
            
            if st.form_submit_button("Record Expense/Cost"):
                base_amt = ex_qty * ex_cpu
                tot_cost = base_amt + ex_surch
                execute_db_command("INSERT INTO expenses (date, project, description, category, uom, units, cost_per_unit, amount, other_charges, total_cost, paid) VALUES (?,?,?,?,?,?,?,?,?,?,?)", (str(ex_date), ex_proj, ex_desc, ex_cat, ex_uom, ex_qty, ex_cpu, base_amt, ex_surch, tot_cost, ex_paid))
                st.success("Expense voucher posted.")
                st.rerun()

    e_df = run_query("SELECT * FROM expenses")
    st.dataframe(e_df, use_container_width=True, hide_index=True)
    if not e_df.empty:
        with st.expander("🗑️ Delete Expense/Cost"):
            del_id = st.selectbox("Select Entry ID to Void:", e_df["id"].tolist())
            if st.button("Delete Expense Record Lines", type="primary"):
                execute_db_command("DELETE FROM expenses WHERE id=?", (del_id,))
                st.rerun()

# 5. TAB: INCOME LEDGER
elif current_tab == "💰 Income Ledger":
    st.markdown('<div class="main-header">💰 Sales Order Revenues Outflows Ledger</div>', unsafe_allow_html=True)
    with st.expander("⚙️ Record Inbound Commodity Order Realized Receipts", expanded=True):
        with st.form("add_income"):
            i1, i2, i3 = st.columns(3)
            with i1: in_date = st.date_input("Value Receipt Date Matrix:", datetime.now())
            with i2: in_src = st.text_input("Purchasing Customer Entity Entity:")
            with i3: in_desc = st.text_input("Transaction Memorandum Notes Details:")
            
            i4, i5, i6 = st.columns(3)
            with i4: in_proj = st.selectbox("Originating Field Area Block Node:", get_configured_projects())
            with i5: in_crop = st.selectbox("Cultivated Crop Node Commodity:", get_configured_crops())
            with i6: in_qty = st.number_input("Volumes / Yield Quantities Dispatched:", min_value=0.0, value=1.0)
            
            i7, i8, i9 = st.columns(3)
            with i7: in_prc = st.number_input(f"Agreed Sales Price/Unit Metric ({c_symbol}):", min_value=0.0, value=1.0)
            with i8: in_other = st.number_input(f"Biomass / Secondary Offtake Gains ({c_symbol}):", min_value=0.0, value=0.0)
            with i9: in_paid = st.selectbox("Settlement Clearing Status Flag Loop:", ["Paid", "Unpaid"])
            
            i10, i11 = st.columns(2)
            with i10: in_mode = st.selectbox("Settlement Channels:", ["M-Pesa", "Bank Transfer", "Cash", "Cheque"])
            with i11: in_code = st.text_input("Electronic Transaction Processing Reference ID:")
            
            if st.form_submit_button("Commit Revenue Transaction Row"):
                base_inc = in_qty * in_prc
                tot_inc = base_inc + in_other
                execute_db_command("INSERT INTO income (date, source, description, project, crop, yield_units, price, amount, other_income, total_income, paid, payment_mode, payment_code) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", (str(in_date), in_src, in_desc, in_proj, in_crop, in_qty, in_prc, base_inc, in_other, tot_inc, in_paid, in_mode, in_code))
                st.success("Revenue dispatch record committed.")
                st.rerun()

    i_df = run_query("SELECT * FROM income")
    st.dataframe(i_df, use_container_width=True, hide_index=True)
    if not i_df.empty:
        with st.expander("🗑️ Delete Revenue Inward Transaction Line Entry"):
            del_id = st.selectbox("Select Target Income Entry Line ID:", i_df["id"].tolist())
            if st.button("Delete Revenue Line Entry Permanently", type="primary"):
                execute_db_command("DELETE FROM income WHERE id=?", (del_id,))
                st.rerun()

# 6. TAB: COST-BENEFIT SANDBOX
elif current_tab == "⚖️ Cost-Benefit Sandbox":
    st.markdown('<div class="main-header">⚖️ Simulation Pro-Forma Modeling Matrix Space</div>', unsafe_allow_html=True)
    with st.form("sandbox_form"):
        sb1, sb2, sb3 = st.columns(3)
        with sb1: sb_crop = st.selectbox("Target Simulation Crop Node Selection:", get_configured_crops())
        with sb2: sb_size = st.number_input("Simulated Acreage Weight Factor:", min_value=1.0, value=10.0)
        with sb3: sb_cpa = st.number_input(f"Simulated Inputs Production Cost / Acre ({c_symbol}):", min_value=0.0, value=1500.0)
        
        sb4, sb5 = st.columns(2)
        with sb4: sb_ypa = st.number_input("Simulated Target Outputs Yield / Acre Metric:", min_value=0.0, value=12.0)
        with sb5: sb_ppu = st.number_input(f"Target Projected Selling Market Value/Unit ({c_symbol}):", min_value=0.0, value=250.0)
        
        if st.form_submit_button("💥 Run Multi-Crop Scenario Projection Matrix Simulation"):
            t_cost = sb_cpa * sb_size
            t_rev = sb_ypa * sb_size * sb_ppu
            t_net = t_rev - t_cost
            roi = (t_net / t_cost * 100) if t_cost > 0 else 0.0
            st.session_state.sandbox_container.append({
                "Crop Target": sb_crop, "Acreage Weight": sb_size, 
                "Projected Cost": t_cost, "Projected Revenue": t_rev, 
                "Net Income Returns": t_net, "Pro-Forma ROI": f"{roi:.1f}%"
            })
            st.rerun()

    if st.session_state.sandbox_container:
        st.markdown("### Simulation Scenarios Output Result Log Matrix")
        st.dataframe(pd.DataFrame(st.session_state.sandbox_container), use_container_width=True, hide_index=True)
        if st.button("🗑️ Clear Scenario Space Cache Canvas"):
            st.session_state.sandbox_container = []
            st.rerun()

# 7. TAB: FINANCIAL REPORTS
elif current_tab == "📋 Financial Reports":
    st.markdown('<div class="main-header">📋 Reconciled Income Performance Statement Engine</div>', unsafe_allow_html=True)
    
    e_df = run_query("SELECT * FROM expenses")
    i_df = run_query("SELECT * FROM income")
    
    rev = i_df["total_income"].sum() if not i_df.empty else 0.0
    c_cats = ["Fertilizer", "Chemicals/Pesticides", "Labor", "Seedlings"]
    cogs = e_df[e_df["category"].isin(c_cats)]["total_cost"].sum() if not e_df.empty else 0.0
    opex = e_df[~e_df["category"].isin(c_cats)]["total_cost"].sum() if not e_df.empty else 0.0
    gp = rev - cogs
    ni = gp - opex
    
    st.components.v1.html(f"""
    <div style="background:#ffffff; border:1px solid #cbd5e1; border-radius:8px; padding:2.5rem; font-family:'Courier New', monospace; color:#0f172a; line-height:1.6;">
        <div style="text-align:center; font-weight:bold; font-size:1.4rem;">AGRIGROW ENTERPRISE PRO PLC</div>
        <div style="text-align:center; font-weight:bold; font-size:1.0rem; color:#475569; margin-bottom:2rem;">PROFIT AND LOSS BALANCE STATEMENT</div>
        <div style="display:flex; justify-content:space-between; font-weight:bold; border-bottom:3px solid #0f172a; padding-bottom:0.5rem;">
            <span>Account Head Segment Segment Matrix</span><span>Net Balance Valuation ({c_symbol})</span>
        </div>
        <div style="display:flex; justify-content:space-between; padding:0.5rem 0; font-weight:bold; color:#2F578A;"><span>OPERATIONAL REVENUES INFLOWS</span></div>
        <div style="display:flex; justify-content:space-between; padding:0.25rem 0 0.25rem 1.5rem;"><span>Gross Farm Commodity Sales Returns</span><span>{rev:,.2f}</span></div>
        <div style="display:flex; justify-content:space-between; padding:0.5rem 0; font-weight:bold; color:#ba3c3c;"><span>COST OF GOODS SOLD (COGS)</span></div>
        <div style="display:flex; justify-content:space-between; padding:0.25rem 0 0.25rem 1.5rem; color:#64748b;"><span>Direct Fields Primary Input Overheads</span><span>({cogs:,.2f})</span></div>
        <div style="display:flex; justify-content:space-between; padding:0.75rem 0; font-weight:bold; border-top:2px solid #0f172a; border-bottom:2px solid #0f172a; background:#f8fafc;">
            <span>GROSS CORPORATE RUNNING MARGIN</span><span>{gp:,.2f}</span>
        </div>
        <div style="display:flex; justify-content:space-between; padding:0.5rem 0; font-weight:bold; color:#475569;"><span>OPERATING EXPENDITURES (OPEX)</span></div>
        <div style="display:flex; justify-content:space-between; padding:0.25rem 0 0.25rem 1.5rem; color:#64748b;"><span>Secondary Logistics & Administrative Maintenance</span><span>({opex:,.2f})</span></div>
        <div style="display:flex; justify-content:space-between; font-size:1.15rem; font-weight:bold; border-top:2px solid #0f172a; border-bottom:4px double #0f172a; margin-top:1.5rem; padding:0.75rem 0; background:#f1f5f9;">
            <span>NET ACCOUNTABLE RETAINED EARNINGS POSITION</span><span>{c_symbol} {ni:,.2f}</span>
        </div>
    </div>
    """, height=420)
    
    report_df = pd.DataFrame({
        "Financial Statement Line Item Head": ["Revenues Flow Streams", "Cost of Goods Sold (COGS)", "Gross Profit Realized Margin", "Operating Expenses (OPEX)", "Net Retained Corporate Gains"],
        "Value Framework Matrix Allocation": [rev, -cogs, gp, -opex, ni]
    })
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        report_df.to_excel(writer, index=False, sheet_name="P_and_L_Statement")
    st.download_button("📥 Export Performance P&L Statement to Excel", data=buffer.getvalue(), file_name=f"AgriGrow_Financial_Report_{date.today()}.xlsx", mime="application/vnd.ms-excel")

# 8. TAB: BULK DATA ENGINE
elif current_tab == "📥 Bulk Data Engine":
    st.markdown('<div class="main-header">📥 Enterprise Data Import/Export Synchronization Hub</div>', unsafe_allow_html=True)
    t1, t2 = st.tabs(["🚀 Bulk Import Component Matrix", "💾 Complete Database Export Module"])
    
    with t1:
        st.markdown("##### Upload Data directly into the SQLite Engine from Excel / CSV templates")
        tgt_table = st.selectbox("Target Core Architecture Storage Node Selection:", ["expenses", "income", "projects", "crops"])
        uploaded_file = st.file_uploader("Drop Template Excel/CSV Matrix Document Block here:", type=["csv", "xlsx"])
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".csv"):
                    imported_df = pd.read_csv(uploaded_file)
                else:
                    imported_df = pd.read_excel(uploaded_file)
                
                st.markdown("##### Previewing Inbound Document Payload Structure")
                st.dataframe(imported_df.head(5), use_container_width=True)
                
                if st.button("🚀 Push Inbound Document Data Rows directly to Database Layer", use_container_width=True):
                    if "id" in imported_df.columns:
                        imported_df = imported_df.drop(columns=["id"])
                    
                    with sqlite3.connect(DB_FILE) as conn:
                        imported_df.to_sql(tgt_table, conn, if_exists="append", index=False)
                    st.success(f"Successfully processed and merged records cleanly into your live database '{tgt_table}' storage.")
                    st.rerun()
            except Exception as ex:
                st.error(f"Data mapping error processing bulk sheet payload arrays: {ex}")
                
    with t2:
        st.markdown("##### Download individual datasets directly as Excel spreadsheets")
        export_choice = st.selectbox("Select Table Array to Export:", ["crops", "projects", "expenses", "income"])
        export_df = run_query(f"SELECT * FROM {export_choice}")
        
        ex_buffer = io.BytesIO()
        with pd.ExcelWriter(ex_buffer, engine='xlsxwriter') as writer:
            export_df.to_excel(writer, index=False, sheet_name=export_choice.upper())
        
        st.download_button(
            label=f"💾 Download Retained {export_choice.upper()} Sheet Records Matrix",
            data=ex_buffer.getvalue(),
            file_name=f"AgriGrow_{export_choice}_dump_{date.today()}.xlsx",
            mime="application/vnd.ms-excel",
            use_container_width=True
        )

# 9. TAB: LIST & CATEGORIES CONFIG (ISOLATED WORKSPACE HUB)
elif current_tab == "📋 List & Categories Config":
    st.markdown('<div class="main-header">📋 Lists and Dropdown Selection Master Registry</div>', unsafe_allow_html=True)
    st.info("💡 Use this canvas space to modify options that appear as select dropdown options across your system registry forms.")
    
    lc1, lc2, lc3, lc4 = st.columns(4)
    
    with lc1:
        st.markdown("##### 🌱 Crop Variety Names")
        current_c_list = get_configured_crops()
        st.write(", ".join(current_c_list) if current_c_list else "*No crop varieties registered yet*")
        with st.form("add_config_crop"):
            new_cc = st.text_input("Append Crop Name Option:")
            if st.form_submit_button("Add Crop"):
                if new_cc:
                    execute_db_command("INSERT OR IGNORE INTO config_crops VALUES (?)", (new_cc.strip(),))
                    st.rerun()
                    
    with lc2:
        st.markdown("##### 🌾 Crop Classification Categories")
        current_type_list = get_configured_crop_types()
        st.write(", ".join(current_type_list) if current_type_list else "*No classification groups registered*")
        with st.form("add_config_crop_type"):
            new_ct = st.text_input("Append Classification Group:")
            if st.form_submit_button("Add Group"):
                if new_ct:
                    execute_db_command("INSERT OR IGNORE INTO config_crop_types VALUES (?)", (new_ct.strip(),))
                    st.rerun()

    with lc3:
        st.markdown("##### 🏗️ Field Area / Project Names")
        current_p_list = get_configured_projects()
        st.write(", ".join(current_p_list) if current_p_list else "*No custom area fields registered*")
        with st.form("add_config_project"):
            new_cp = st.text_input("Append Field Block Area Option:")
            if st.form_submit_button("Add Project Name"):
                if new_cp:
                    execute_db_command("INSERT OR IGNORE INTO config_projects VALUES (?)", (new_cp.strip(),))
                    st.rerun()
                    
    with lc4:
        st.markdown("##### 📉 Expenditure Accounts Overheads")
        current_cat_list = get_configured_categories()
        st.write(", ".join(current_cat_list) if current_cat_list else "*No overhead categories registered*")
        with st.form("add_config_cat"):
            new_cat = st.text_input("Append Invoiced Overhead Category:")
            if st.form_submit_button("Add Expense Category"):
                if new_cat:
                    execute_db_command("INSERT OR IGNORE INTO config_categories VALUES (?)", (new_cat.strip(),))
                    st.rerun()

# 10. TAB: SYSTEM CONFIG
elif current_tab == "⚙️ System Config":
    st.markdown('<div class="main-header">⚙️ System Administrative Access Configuration Settings</div>', unsafe_allow_html=True)
    
    sc_bot1, sc_bot2 = st.columns(2)
    with sc_bot1:
        with st.form("sys_localization"):
            st.markdown("##### Localization Settings Options")
            sys_curr = st.selectbox("Primary Valuation Currency Options:", ["USD ($)", "EUR (€)", "KES (KSh)", "GBP (£)"], index=2)
            if st.form_submit_button("Save Currency Base Standard Config"):
                st.session_state.currency = sys_curr
                st.rerun()
                
    with sc_bot2:
        with st.form("sys_users"):
            st.markdown("##### 👥 User Access Control Administration Gate")
            u_email = st.text_input("Assign Identity Email Credentials:")
            u_pass = st.text_input("Assign Access Entry Passphrase Keys:", type="password")
            u_name = st.text_input("Assign Account User Full Identity Name:")
            u_role = st.selectbox("Assign Roles Node Authorization Group Level:", ["Field Operations Lead", "Financial Officer", "Data Auditor Pro", "Farm Owner"])
            if st.form_submit_button("🔒 Authorize & Append New Identity Frame Profile Row"):
                if u_email and u_pass and u_name:
                    execute_db_command("INSERT OR IGNORE INTO users (email, password, name, role) VALUES (?,?,?,?)", (u_email.strip(), u_pass, u_name, u_role))
                    st.success("Successfully written credentials row.")
                    st.rerun()