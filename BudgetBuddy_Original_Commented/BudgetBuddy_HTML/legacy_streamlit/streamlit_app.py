import io
import os
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date

from database import (
    create_tables,
    get_user,
    update_profile,
    add_expense,
    add_expenses_batch,
    get_expenses,
    delete_expense,
    clear_user_expenses,
    set_budget,
    get_budgets
)

from auth import authentication_page
from style import apply_custom_styles

from analysis import (
    calculate_summary,
    category_analysis,
    monthly_analysis,
    get_highest_category,
    daily_trend_analysis,
    budget_compliance,
    inspect_dataset,
    get_statistical_summary,
    detect_dataset_type,
    process_wide_financial_dataset
)

from charts import (
    create_category_donut_chart,
    create_category_bar_chart,
    create_monthly_trend_chart,
    create_cumulative_savings_chart,
    create_wide_yearly_comparison_chart,
    create_wide_monthly_chart,
    create_correlation_heatmap,
    create_custom_chart
)

# -------------------------------------------------------------
# PAGE CONFIGURATION
# -------------------------------------------------------------
st.set_page_config(
    page_title="Budget Buddy",
    layout="wide",
    initial_sidebar_state="expanded"
)



# Database initialization
create_tables()

# Session State Initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "currency" not in st.session_state:
    st.session_state.currency = "₹"

# -------------------------------------------------------------
# AUTHENTICATION CHECK
# -------------------------------------------------------------
if not st.session_state.logged_in:
    apply_custom_styles("Dashboard")
    authentication_page()
    st.stop()

# -------------------------------------------------------------
# USER PROFILE
# -------------------------------------------------------------
user = get_user(st.session_state.user_id)
if not user:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.rerun()

user_id = user[0]
email = user[1]
name = user[2] or "User"
income = float(user[3]) if user[3] else 0.0

# -------------------------------------------------------------
# SIDEBAR NAVIGATION
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("<h2 style='margin-bottom: 0.2rem;'>Budget Buddy</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #64748b; font-size: 0.9rem;'>Welcome, {name}</p>", unsafe_allow_html=True)
    st.divider()

    menu = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Budget Planner",
            "Add Expense",
            "Expense History",
            "Dataset Analyzer",
            "Profile"
        ]
    )

    # Dynamically update light theme and background based on active tab
    apply_custom_styles(active_tab=menu)

    st.divider()

    apk_path = "data/BudgetBuddy-v1.0.apk"
    if os.path.exists(apk_path):
        with open(apk_path, "rb") as f:
            sidebar_apk_bytes = f.read()
        st.download_button(
            "Download Android APK",
            data=sidebar_apk_bytes,
            file_name="BudgetBuddy-v1.0.apk",
            mime="application/vnd.android.package-archive",
            use_container_width=True
        )

    st.divider()

    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.rerun()

# -------------------------------------------------------------
# EXPENSE DATA
# -------------------------------------------------------------
df = get_expenses(user_id)
budgets = get_budgets(user_id)
curr = st.session_state.currency

# -------------------------------------------------------------
# 1. DASHBOARD
# -------------------------------------------------------------
if menu == "Dashboard":
    st.markdown("## Financial Dashboard")

    if income <= 0:
        st.info("Set your baseline monthly income in Profile to enable complete savings analytics.")

    summary = calculate_summary(df, income)

    # KPI Metric Cards with hover animations
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric("Monthly Income", f"{curr}{summary['income']:,.2f}")
    with kpi2:
        st.metric("Total Expenses", f"{curr}{summary['total_expenses']:,.2f}")
    with kpi3:
        st.metric("Net Balance", f"{curr}{summary['remaining_balance']:,.2f}")
    with kpi4:
        st.metric("Savings Rate", f"{summary['savings_rate']:.1f}%")

    kpi5, kpi6, kpi7, kpi8 = st.columns(4)
    with kpi5:
        st.metric("Top Category", get_highest_category(df))
    with kpi6:
        st.metric("Daily Average Spend", f"{curr}{summary['avg_daily_expense']:,.2f}")
    with kpi7:
        st.metric("Expense to Income", f"{summary['expense_ratio']:.1f}%")
    with kpi8:
        st.metric("Financial Health", summary["health_status"])

    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

    if df.empty:
        st.markdown(
            """
            <div class='glass-card'>
                <h4>No Expenses Recorded</h4>
                <p style='color: #64748b;'>Add transactions manually under <b>Add Expense</b> or upload an existing file in <b>Dataset Analyzer</b> to view insights.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        cat_df = category_analysis(df)
        monthly_df = monthly_analysis(df)

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown("### Expense Distribution")
            fig_donut = create_category_donut_chart(cat_df)
            st.plotly_chart(fig_donut, use_container_width=True)

        with col_c2:
            st.markdown("### Spending by Category")
            fig_bar = create_category_bar_chart(cat_df)
            st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("### Monthly Expense Trend vs Income")
        fig_trend = create_monthly_trend_chart(monthly_df, income)
        st.plotly_chart(fig_trend, use_container_width=True)

        if income > 0 and not monthly_df.empty:
            st.markdown("### Cumulative Savings Trajectory")
            fig_savings = create_cumulative_savings_chart(monthly_df, income)
            st.plotly_chart(fig_savings, use_container_width=True)

# -------------------------------------------------------------
# 2. BUDGET PLANNER
# -------------------------------------------------------------
elif menu == "Budget Planner":
    st.markdown("## Budget Planner")
    st.markdown("<p style='color: #64748b;'>Set monthly spending limits for each category and track consumption in real time.</p>", unsafe_allow_html=True)

    col_b1, col_b2 = st.columns([1, 2])

    with col_b1:
        st.markdown("### Set Category Limit")
        standard_categories = [
            "Groceries", "Rent", "Transportation", "Gym", "Utilities",
            "Electricity Bill", "Internet & Mobile Bill", "Healthcare",
            "Insurance", "Investments", "Savings", "EMI/Loans", "Taxes",
            "Dining & Entertainment", "Shopping & Wants", "Education", "Other"
        ]

        target_category = st.selectbox("Category", standard_categories)
        current_limit = budgets.get(target_category, 0.0)
        new_limit = st.number_input("Monthly Limit (" + curr + ")", min_value=0.0, value=float(current_limit), step=500.0)

        if st.button("Save Limit", use_container_width=True):
            set_budget(user_id, target_category, new_limit)
            st.success(f"Budget for {target_category} updated to {curr}{new_limit:,.2f}")
            st.rerun()

    with col_b2:
        st.markdown("### Active Category Budgets")
        if not budgets:
            st.info("No budgets configured yet. Select a category on the left to set a monthly limit.")
        else:
            budget_df = budget_compliance(df, budgets)

            total_allocated = sum(budgets.values())
            st.write(f"**Total Allocated Budget:** {curr}{total_allocated:,.2f} | **Monthly Income:** {curr}{income:,.2f}")
            st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

            for _, row in budget_df.iterrows():
                cat = row["Category"]
                spent = row["Spent"]
                limit = row["Budget"]
                pct = row["Percent_Used"]
                status = row["Status"]

                pct_norm = min(1.0, max(0.0, pct / 100.0))

                color_badge = "#10b981" if status == "Within Budget" else ("#f59e0b" if status == "Near Limit" else "#ef4444")

                st.markdown(
                    f"""
                    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;'>
                        <span style='font-weight: 600;'>{cat}</span>
                        <span style='color: {color_badge}; font-weight: 600; font-size: 0.85rem;'>{status} ({pct:.1f}%)</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.progress(pct_norm)
                st.markdown(
                    f"<p style='color: #64748b; font-size: 0.82rem; margin-top: -8px; margin-bottom: 14px;'>Spent: {curr}{spent:,.2f} of {curr}{limit:,.2f} (Remaining: {curr}{(limit - spent):,.2f})</p>",
                    unsafe_allow_html=True
                )

# -------------------------------------------------------------
# 3. ADD EXPENSE
# -------------------------------------------------------------
elif menu == "Add Expense":
    st.markdown("## Record Expenses")

    tab_single, tab_batch = st.tabs(["Single Entry", "Batch Entry"])

    with tab_single:
        col_e1, col_e2 = st.columns(2)

        with col_e1:
            exp_amount = st.number_input("Amount (" + curr + ")", min_value=0.0, step=50.0)
            exp_category = st.selectbox(
                "Category",
                [
                    "Groceries", "Rent", "Transportation", "Gym", "Utilities",
                    "Electricity Bill", "Internet & Mobile Bill", "Healthcare",
                    "Insurance", "Investments", "Savings", "EMI/Loans", "Taxes",
                    "Dining & Entertainment", "Shopping & Wants", "Education", "Other"
                ]
            )

        with col_e2:
            exp_date = st.date_input("Date", value=date.today())
            exp_desc = st.text_input("Description", placeholder="e.g. Weekly grocery purchase")

        if st.button("Add Expense", use_container_width=True):
            if exp_amount <= 0:
                st.error("Please enter a valid amount greater than zero.")
            else:
                add_expense(user_id, exp_amount, exp_category, exp_desc, str(exp_date))
                st.success("Expense recorded successfully.")
                st.rerun()

    with tab_batch:
        st.markdown("### Quick Multi-Row Entry")
        st.markdown("<p style='color: #64748b;'>Enter multiple expenses and submit in one transaction.</p>", unsafe_allow_html=True)

        batch_template = pd.DataFrame([
            {"Amount": 0.0, "Category": "Groceries", "Description": "", "Date": str(date.today())},
            {"Amount": 0.0, "Category": "Dining & Entertainment", "Description": "", "Date": str(date.today())},
            {"Amount": 0.0, "Category": "Transportation", "Description": "", "Date": str(date.today())},
        ])

        edited_batch = st.data_editor(batch_template, num_rows="dynamic", use_container_width=True)

        if st.button("Save All Records", use_container_width=True):
            valid_records = []
            for _, r in edited_batch.iterrows():
                try:
                    amt = float(r["Amount"])
                    if amt > 0:
                        valid_records.append((amt, str(r["Category"]), str(r.get("Description", "")), str(r["Date"])))
                except Exception:
                    continue

            if not valid_records:
                st.warning("No rows with amount greater than zero.")
            else:
                count = add_expenses_batch(user_id, valid_records)
                st.success(f"Saved {count} expenses successfully.")
                st.rerun()

# -------------------------------------------------------------
# 4. EXPENSE HISTORY
# -------------------------------------------------------------
elif menu == "Expense History":
    st.markdown("## Expense History")

    if df.empty:
        st.info("No expense history recorded yet.")
    else:
        # Filter controls
        f_col1, f_col2, f_col3, f_col4 = st.columns(4)

        categories_list = ["All"] + sorted(df["category"].dropna().unique().tolist())

        with f_col1:
            cat_filter = st.selectbox("Filter Category", categories_list)

        with f_col2:
            search_query = st.text_input("Search Description", placeholder="Keyword...")

        with f_col3:
            min_amt = st.number_input("Minimum Amount (" + curr + ")", min_value=0.0, value=0.0, step=100.0)

        with f_col4:
            sort_order = st.selectbox("Sort Order", ["Newest First", "Oldest First", "Highest Amount", "Lowest Amount"])

        # Filter logic
        filtered_df = df.copy()

        if cat_filter != "All":
            filtered_df = filtered_df[filtered_df["category"] == cat_filter]

        if search_query:
            filtered_df = filtered_df[
                filtered_df["description"].str.contains(search_query, case=False, na=False) |
                filtered_df["category"].str.contains(search_query, case=False, na=False)
            ]

        if min_amt > 0:
            filtered_df = filtered_df[filtered_df["amount"] >= min_amt]

        if sort_order == "Newest First":
            filtered_df = filtered_df.sort_values("expense_date", ascending=False)
        elif sort_order == "Oldest First":
            filtered_df = filtered_df.sort_values("expense_date", ascending=True)
        elif sort_order == "Highest Amount":
            filtered_df = filtered_df.sort_values("amount", ascending=False)
        elif sort_order == "Lowest Amount":
            filtered_df = filtered_df.sort_values("amount", ascending=True)

        st.markdown(f"**Showing {len(filtered_df)} records** | **Total Sum:** {curr}{filtered_df['amount'].sum():,.2f}")

        # Display table
        display_table = filtered_df.copy()
        display_table.columns = ["ID", "Amount (" + curr + ")", "Category", "Description", "Date"]
        st.dataframe(display_table, use_container_width=True)

        # Export & Actions
        act_col1, act_col2, act_col3 = st.columns([1, 1, 1])

        with act_col1:
            csv_data = filtered_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Export Filtered CSV",
                data=csv_data,
                file_name="budget_buddy_expenses.csv",
                mime="text/csv",
                use_container_width=True
            )

        with act_col2:
            try:
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                    filtered_df.to_excel(writer, index=False, sheet_name="Expenses")
                st.download_button(
                    "Export Filtered Excel",
                    data=buffer.getvalue(),
                    file_name="budget_buddy_expenses.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            except Exception:
                pass

        with act_col3:
            delete_id = st.number_input("Delete by Record ID", min_value=1, step=1, key="del_id")
            if st.button("Delete Record", use_container_width=True):
                delete_expense(int(delete_id), user_id)
                st.success(f"Record {delete_id} deleted.")
                st.rerun()

# -------------------------------------------------------------
# 5. DATASET ANALYZER (UNIVERSAL CSV & XLSX)
# -------------------------------------------------------------
elif menu == "Dataset Analyzer":
    st.markdown("## Universal Dataset Analyzer")
    st.markdown("<p style='color: #64748b;'>Upload any CSV or Excel file (.xlsx, .xls) for instant automated analysis, statistical inspection, and interactive visualization.</p>", unsafe_allow_html=True)

    col_up1, col_up2 = st.columns([3, 1])

    with col_up1:
        uploaded_file = st.file_uploader(
            "Choose a dataset file",
            type=["csv", "xlsx", "xls"],
            help="Supports any tabular dataset in CSV or Excel format"
        )

    with col_up2:
        st.write("Or explore sample data:")
        load_sample = st.button("Load 2020-2026 Sample Dataset", use_container_width=True)

    active_df = None

    if load_sample:
        sample_path = "data/sample_financial_data.csv"
        if os.path.exists(sample_path):
            active_df = pd.read_csv(sample_path)
            st.session_state.active_analyzer_df = active_df
            st.session_state.analyzer_source = "2020-2026 Multi-Year Financial Dataset"
        else:
            st.error("Sample dataset file not found.")

    elif uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                active_df = pd.read_csv(uploaded_file)
            else:
                active_df = pd.read_excel(uploaded_file)
            st.session_state.active_analyzer_df = active_df
            st.session_state.analyzer_source = uploaded_file.name
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")

    elif "active_analyzer_df" in st.session_state:
        active_df = st.session_state.active_analyzer_df

    if active_df is not None and not active_df.empty:
        source_label = st.session_state.get("analyzer_source", "Uploaded Dataset")
        st.success(f"Active Dataset: **{source_label}** ({len(active_df):,} rows, {len(active_df.columns)} columns)")

        ds_type = detect_dataset_type(active_df)

        # -------------------------------------------------------------
        # SPECIALIZED MODE: FINANCIAL DATASET (e.g. 2020-2026 sheet)
        # -------------------------------------------------------------
        if ds_type == "financial_wide":
            st.markdown("### Financial Analysis Mode")
            st.write("Multi-column financial structure recognized. Generating multi-year financial summaries.")

            fin_res = process_wide_financial_dataset(active_df)

            f_kpi1, f_kpi2, f_kpi3, f_kpi4 = st.columns(4)
            with f_kpi1:
                st.metric("Total Recorded Days", f"{fin_res['total_records']:,}")
            with f_kpi2:
                st.metric("Total Income", f"{curr}{fin_res['total_income']:,.2f}")
            with f_kpi3:
                st.metric("Total Expenditure", f"{curr}{fin_res['total_expenditure']:,.2f}")
            with f_kpi4:
                st.metric("Net Savings", f"{curr}{fin_res['net_balance']:,.2f}")

            st.write(f"**Timeline:** {fin_res['min_date']} to {fin_res['max_date']}")

            # Yearly comparison
            st.markdown("#### Yearly Income vs Expenditure Comparison")
            fig_yearly = create_wide_yearly_comparison_chart(fin_res["yearly_summary"])
            st.plotly_chart(fig_yearly, use_container_width=True)

            # Category distribution across dataset
            c_col1, c_col2 = st.columns(2)
            with c_col1:
                st.markdown("#### All-Time Category Distribution")
                cat_totals_df = fin_res["category_totals"].rename(columns={"Category": "category", "Total_Amount": "amount"})
                fig_cat_donut = create_category_donut_chart(cat_totals_df)
                st.plotly_chart(fig_cat_donut, use_container_width=True)

            with c_col2:
                st.markdown("#### All-Time Category Rankings")
                fig_cat_bar = create_category_bar_chart(cat_totals_df)
                st.plotly_chart(fig_cat_bar, use_container_width=True)

            # Multi-Year Monthly Trend
            st.markdown("#### Multi-Year Monthly Spending Trend")
            fig_monthly_wide = create_wide_monthly_chart(fin_res["monthly_summary"])
            st.plotly_chart(fig_monthly_wide, use_container_width=True)

            # Annual Table
            st.markdown("#### Annual Performance Breakdown")
            yearly_display = fin_res["yearly_summary"].copy()
            yearly_display["Total_Income"] = yearly_display["Total_Income"].apply(lambda x: f"{curr}{x:,.2f}")
            yearly_display["Total_Expenses"] = yearly_display["Total_Expenses"].apply(lambda x: f"{curr}{x:,.2f}")
            yearly_display["Net_Savings"] = yearly_display["Net_Savings"].apply(lambda x: f"{curr}{x:,.2f}")
            yearly_display["Savings_Rate"] = yearly_display["Savings_Rate"].apply(lambda x: f"{x:.1f}%")
            st.dataframe(yearly_display, use_container_width=True)

            # One-Click Database Import
            st.markdown("#### Import Dataset into Budget Buddy")
            st.write(f"Convert all **{len(fin_res['unpivoted_records']):,}** individual category expenses into your account database.")

            col_imp1, col_imp2 = st.columns([1, 2])
            with col_imp1:
                if st.button("Import to Database", use_container_width=True):
                    inserted = add_expenses_batch(user_id, fin_res["unpivoted_records"])
                    st.success(f"Successfully imported {inserted:,} expenses into your account.")
                    st.rerun()

            st.divider()

        # -------------------------------------------------------------
        # GENERAL EXPLORATORY DATA ANALYSIS (EDA) FOR ANY DATASET
        # -------------------------------------------------------------
        st.markdown("### Exploratory Data Analysis")

        inspection = inspect_dataset(active_df)

        e_col1, e_col2, e_col3, e_col4 = st.columns(4)
        with e_col1:
            st.metric("Total Rows", f"{inspection['rows']:,}")
        with e_col2:
            st.metric("Total Columns", f"{inspection['columns']:,}")
        with e_col3:
            st.metric("Memory Footprint", f"{inspection['memory_kb']:.1f} KB")
        with e_col4:
            st.metric("Duplicate Rows", f"{inspection['duplicates']:,}")

        # Tabs for detailed EDA
        tab_preview, tab_stats, tab_corr, tab_plot = st.tabs([
            "Data Preview",
            "Statistical Summary",
            "Correlation Heatmap",
            "Custom Chart Builder"
        ])

        with tab_preview:
            st.markdown("#### Dataset Preview")
            st.dataframe(active_df.head(100), use_container_width=True)

            st.markdown("#### Column Details & Missing Values")
            st.dataframe(inspection["column_info"], use_container_width=True)

        with tab_stats:
            num_stats, cat_stats = get_statistical_summary(active_df)
            if not num_stats.empty:
                st.markdown("#### Numerical Attributes Summary")
                st.dataframe(num_stats, use_container_width=True)
            if not cat_stats.empty:
                st.markdown("#### Categorical Attributes Summary")
                st.dataframe(cat_stats, use_container_width=True)

        with tab_corr:
            st.markdown("#### Correlation Matrix")
            fig_corr = create_correlation_heatmap(active_df)
            st.plotly_chart(fig_corr, use_container_width=True)

        with tab_plot:
            st.markdown("#### Interactive Custom Chart Builder")
            st.write("Plot any columns from your uploaded dataset with smooth interactive hover states.")

            p_col1, p_col2, p_col3, p_col4 = st.columns(4)
            with p_col1:
                chart_type = st.selectbox("Chart Type", ["Bar", "Line", "Scatter", "Histogram", "Box", "Area"])
            with p_col2:
                x_axis = st.selectbox("X-Axis Column", active_df.columns.tolist())
            with p_col3:
                numeric_options = ["None"] + inspection["numeric_cols"]
                y_axis = st.selectbox("Y-Axis Column", numeric_options)
                y_val = y_axis if y_axis != "None" else None
            with p_col4:
                color_options = ["None"] + active_df.columns.tolist()
                color_axis = st.selectbox("Color Grouping", color_options)
                color_val = color_axis if color_axis != "None" else None

            fig_custom = create_custom_chart(active_df, chart_type, x_axis, y_val, color_val)
            st.plotly_chart(fig_custom, use_container_width=True)

    else:
        st.info("Upload a CSV or Excel file above or click 'Load 2020-2026 Sample Dataset' to begin analysis.")

# -------------------------------------------------------------
# 6. PROFILE
# -------------------------------------------------------------
elif menu == "Profile":
    st.markdown("## User Profile")

    p_col1, p_col2 = st.columns(2)

    with p_col1:
        st.markdown("### Account Information")
        st.write(f"**Email Address:** {email}")

        edit_name = st.text_input("Name", value=name)
        edit_income = st.number_input("Monthly Income (" + curr + ")", min_value=0.0, value=float(income), step=500.0)

        currency_choice = st.selectbox(
            "Preferred Currency Symbol",
            ["₹ (INR)", "$ (USD)", "€ (EUR)", "£ (GBP)", "¥ (JPY)", "Rs (PKR/NPR)"],
            index=0
        )

        if st.button("Save Changes", use_container_width=True):
            clean_curr = currency_choice.split()[0]
            st.session_state.currency = clean_curr
            update_profile(user_id, edit_name.strip(), edit_income)
            st.success("Profile updated successfully.")
            st.rerun()

    with p_col2:
        st.markdown("### Data Management")
        st.write(f"**Total Expenses Recorded:** {len(df):,}")
        st.write(f"**Active Category Budgets:** {len(budgets):,}")

        st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
        st.markdown("#### Reset Account Data")
        st.write("Remove all recorded expenses associated with your account.")
        if st.button("Clear All Expenses", type="secondary", use_container_width=True):
            deleted = clear_user_expenses(user_id)
            st.success(f"Cleared {deleted:,} expenses from your account.")
            st.rerun()

    # Mobile Application Download Section
    st.divider()
    st.markdown("### Mobile Application (Android)")
    st.markdown("<p style='color: #64748b;'>Download and install the Budget Buddy Android package directly on your mobile device.</p>", unsafe_allow_html=True)

    apk_file = "data/BudgetBuddy-v1.0.apk"
    if os.path.exists(apk_file):
        m_col1, m_col2 = st.columns([2, 1])
        with m_col1:
            st.markdown(
                """
                <div class='glass-card' style='padding: 1rem; margin-bottom: 0;'>
                    <p style='margin: 0 0 4px 0;'><b>Package:</b> app.budgetbuddy.tracker</p>
                    <p style='margin: 0 0 4px 0;'><b>Version:</b> 1.0.0 (Release Build)</p>
                    <p style='margin: 0 0 4px 0;'><b>Requirements:</b> Android 8.0 or higher</p>
                    <p style='margin: 0;'><b>Installation:</b> Open downloaded APK and permit installation from browser if prompted.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        with m_col2:
            with open(apk_file, "rb") as f:
                prof_apk_data = f.read()
            st.download_button(
                "Download APK (v1.0.0)",
                data=prof_apk_data,
                file_name="BudgetBuddy-v1.0.apk",
                mime="application/vnd.android.package-archive",
                use_container_width=True
            )
