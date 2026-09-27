import pandas as pd
import numpy as np


def calculate_summary(df, monthly_income=0.0):
    income = float(monthly_income) if monthly_income else 0.0

    if df.empty:
        total_expenses = 0.0
        avg_daily = 0.0
        unique_days = 0
    else:
        total_expenses = float(df["amount"].sum())
        if "expense_date" in df.columns:
            unique_days = df["expense_date"].nunique()
            avg_daily = total_expenses / max(1, unique_days)
        else:
            avg_daily = total_expenses / 30.0

    remaining_balance = income - total_expenses
    savings_rate = max(0.0, (remaining_balance / income) * 100) if income > 0 else 0.0
    expense_ratio = (total_expenses / income * 100) if income > 0 else 0.0

    if total_expenses == 0:
        health_status = "No Expenses Recorded"
    elif income <= 0:
        health_status = "Income Not Configured"
    elif expense_ratio <= 50:
        health_status = "Healthy (High Savings)"
    elif expense_ratio <= 75:
        health_status = "Balanced Spending"
    elif expense_ratio <= 95:
        health_status = "High Utilization"
    else:
        health_status = "Deficit (Expenses Exceed Income)"

    return {
        "income": income,
        "total_expenses": total_expenses,
        "remaining_balance": remaining_balance,
        "savings_rate": savings_rate,
        "expense_ratio": expense_ratio,
        "avg_daily_expense": avg_daily,
        "health_status": health_status
    }


def category_analysis(df):
    if df.empty:
        return pd.DataFrame(columns=["category", "amount", "share_pct", "count"])

    category_data = (
        df.groupby("category")["amount"]
        .agg(amount="sum", count="count")
        .reset_index()
        .sort_values("amount", ascending=False)
    )

    total = category_data["amount"].sum()
    if total > 0:
        category_data["share_pct"] = (category_data["amount"] / total) * 100
    else:
        category_data["share_pct"] = 0.0

    return category_data


def monthly_analysis(df):
    if df.empty:
        return pd.DataFrame(columns=["month", "amount", "count"])

    df = df.copy()
    df["date_parsed"] = pd.to_datetime(df["expense_date"], errors="coerce")
    df = df.dropna(subset=["date_parsed"])

    if df.empty:
        return pd.DataFrame(columns=["month", "amount", "count"])

    df["month"] = df["date_parsed"].dt.strftime("%Y-%m")

    monthly_data = (
        df.groupby("month")["amount"]
        .agg(amount="sum", count="count")
        .reset_index()
        .sort_values("month")
    )

    return monthly_data


def get_highest_category(df):
    if df.empty:
        return "None"

    cat_df = category_analysis(df)
    if cat_df.empty or cat_df.iloc[0]["amount"] <= 0:
        return "None"

    top_row = cat_df.iloc[0]
    return f"{top_row['category']} (₹{top_row['amount']:,.0f})"


def daily_trend_analysis(df):
    if df.empty:
        return pd.DataFrame(columns=["date", "amount"])

    df = df.copy()
    df["date_parsed"] = pd.to_datetime(df["expense_date"], errors="coerce")
    df = df.dropna(subset=["date_parsed"])

    daily = (
        df.groupby("date_parsed")["amount"]
        .sum()
        .reset_index()
        .rename(columns={"date_parsed": "date"})
        .sort_values("date")
    )

    return daily


def budget_compliance(df, budgets):
    if not budgets:
        return pd.DataFrame()

    category_totals = {}
    if not df.empty:
        cat_df = category_analysis(df)
        category_totals = dict(zip(cat_df["category"], cat_df["amount"]))

    rows = []
    for cat, limit in budgets.items():
        spent = category_totals.get(cat, 0.0)
        remaining = limit - spent
        pct = (spent / limit * 100) if limit > 0 else 0.0

        if pct <= 80:
            status = "Within Budget"
        elif pct <= 100:
            status = "Near Limit"
        else:
            status = "Exceeded"

        rows.append({
            "Category": cat,
            "Spent": spent,
            "Budget": limit,
            "Remaining": remaining,
            "Percent_Used": pct,
            "Status": status
        })

    result = pd.DataFrame(rows).sort_values("Percent_Used", ascending=False)
    return result


# -------------------------------------------------------------
# UNIVERSAL DATASET ANALYZER
# -------------------------------------------------------------

def inspect_dataset(df):
    if df is None or df.empty:
        return {}

    num_rows, num_cols = df.shape
    memory_bytes = df.memory_usage(deep=True).sum()
    memory_kb = memory_bytes / 1024.0

    duplicate_rows = int(df.duplicated().sum())

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    datetime_cols = df.select_dtypes(include=["datetime"]).columns.tolist()

    missing_data = []
    for col in df.columns:
        null_count = int(df[col].isnull().sum())
        null_pct = (null_count / num_rows * 100) if num_rows > 0 else 0.0
        missing_data.append({
            "Column": col,
            "Data_Type": str(df[col].dtype),
            "Null_Count": null_count,
            "Null_Percentage": null_pct,
            "Unique_Values": int(df[col].nunique())
        })

    missing_df = pd.DataFrame(missing_data)

    return {
        "rows": num_rows,
        "columns": num_cols,
        "memory_kb": memory_kb,
        "duplicates": duplicate_rows,
        "numeric_cols": numeric_cols,
        "categorical_cols": categorical_cols,
        "datetime_cols": datetime_cols,
        "column_info": missing_df
    }


def get_statistical_summary(df):
    if df is None or df.empty:
        return pd.DataFrame(), pd.DataFrame()

    numeric_df = df.select_dtypes(include=[np.number])
    categorical_df = df.select_dtypes(include=["object", "category"])

    num_stats = pd.DataFrame()
    cat_stats = pd.DataFrame()

    if not numeric_df.empty:
        desc = numeric_df.describe().T
        desc["skewness"] = numeric_df.skew()
        desc = desc.reset_index().rename(columns={"index": "Column"})
        num_stats = desc

    if not categorical_df.empty:
        desc_cat = categorical_df.describe().T.reset_index().rename(columns={"index": "Column"})
        cat_stats = desc_cat

    return num_stats, cat_stats


def detect_dataset_type(df):
    if df is None or df.empty:
        return "empty"

    cols_lower = [str(c).strip().lower() for c in df.columns]

    # Check wide financial sheet (e.g. Month/Date, Groceries, Rent, Total Expenditure, Income)
    financial_keywords = ["groceries", "rent", "transportation", "utilities", "total expenditure", "income", "savings", "investments"]
    matches = sum(1 for kw in financial_keywords if any(kw in col for col in cols_lower))

    if matches >= 3:
        return "financial_wide"

    # Check long financial transaction sheet (date, category, amount)
    has_amount = any("amount" in c or "expense" in c or "cost" in c for c in cols_lower)
    has_cat = any("category" in c or "type" in c or "item" in c for c in cols_lower)
    has_date = any("date" in c or "month" in c or "time" in c for c in cols_lower)

    if has_amount and (has_cat or has_date):
        return "financial_long"

    return "general_tabular"


def process_wide_financial_dataset(df):
    # Clean column names
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    # Identify date column
    date_col = None
    for c in df.columns:
        if c.lower() in ["month", "date", "timestamp", "day"]:
            date_col = c
            break

    if date_col is None:
        date_col = df.columns[0]

    # Parse dates
    df["parsed_date"] = pd.to_datetime(df[date_col], format="%d-%m-%Y", errors="coerce")
    if df["parsed_date"].isnull().all():
        df["parsed_date"] = pd.to_datetime(df[date_col], errors="coerce")

    df = df.dropna(subset=["parsed_date"])
    df = df.sort_values("parsed_date")

    # Separate special columns
    income_col = next((c for c in df.columns if c.lower() == "income"), None)
    total_exp_col = next((c for c in df.columns if "total expenditure" in c.lower() or "total expense" in c.lower()), None)

    non_cat_cols = {"parsed_date", date_col}
    if income_col:
        non_cat_cols.add(income_col)
    if total_exp_col:
        non_cat_cols.add(total_exp_col)

    category_cols = [c for c in df.columns if c not in non_cat_cols and np.issubdtype(df[c].dtype, np.number)]

    # Compute category totals
    category_totals = df[category_cols].sum().reset_index()
    category_totals.columns = ["Category", "Total_Amount"]
    category_totals = category_totals.sort_values("Total_Amount", ascending=False)

    # Compute yearly summary
    df["Year"] = df["parsed_date"].dt.year
    df["YearMonth"] = df["parsed_date"].dt.strftime("%Y-%m")

    # If Total Expenditure col is missing, compute it from categories
    if total_exp_col and total_exp_col in df.columns:
        df["Computed_Expenditure"] = df[total_exp_col]
    else:
        df["Computed_Expenditure"] = df[category_cols].sum(axis=1)

    yearly = df.groupby("Year").agg(
        Total_Expenses=("Computed_Expenditure", "sum"),
        Total_Income=(income_col, "sum") if income_col else ("Computed_Expenditure", lambda x: 0.0),
        Days_Recorded=("parsed_date", "count")
    ).reset_index()

    yearly["Net_Savings"] = yearly["Total_Income"] - yearly["Total_Expenses"]
    yearly["Savings_Rate"] = np.where(
        yearly["Total_Income"] > 0,
        (yearly["Net_Savings"] / yearly["Total_Income"]) * 100,
        0.0
    )

    # Monthly trend
    monthly = df.groupby("YearMonth").agg(
        Total_Expenses=("Computed_Expenditure", "sum"),
        Total_Income=(income_col, "sum") if income_col else ("Computed_Expenditure", lambda x: 0.0)
    ).reset_index()

    # Unpivot to normalized long transactions for direct DB import
    unpivoted_records = []
    for _, row in df.iterrows():
        dt_str = row["parsed_date"].strftime("%Y-%m-%d")
        for cat in category_cols:
            val = float(row[cat])
            if val > 0:
                unpivoted_records.append((val, cat, f"{cat} expense on {dt_str}", dt_str))

    total_income = float(df[income_col].sum()) if income_col else 0.0
    total_exp = float(df["Computed_Expenditure"].sum())

    return {
        "cleaned_df": df,
        "date_col": date_col,
        "category_cols": category_cols,
        "category_totals": category_totals,
        "yearly_summary": yearly,
        "monthly_summary": monthly,
        "unpivoted_records": unpivoted_records,
        "total_records": len(df),
        "total_income": total_income,
        "total_expenditure": total_exp,
        "net_balance": total_income - total_exp,
        "min_date": df["parsed_date"].min().strftime("%d %b %Y"),
        "max_date": df["parsed_date"].max().strftime("%d %b %Y")
    }
