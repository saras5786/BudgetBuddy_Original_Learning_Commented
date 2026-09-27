# ================================================================
# BUDGET BUDDY - DATA ANALYSIS FUNCTIONS
# ================================================================
# Pandas handles tables/grouping. NumPy helps with numerical work.
# Typical flow: app.py -> function here -> result -> JavaScript.
# ================================================================

import pandas as pd
import numpy as np

# CALLED BY: app.py -> summary_payload() -> /api/dashboard
def calculate_summary(df, monthly_income=0.0):
    income=float(monthly_income or 0)
    total=float(df['amount'].sum()) if not df.empty else 0.0
    unique_days=df['expense_date'].nunique() if not df.empty and 'expense_date' in df else 0
    avg=total/max(1,unique_days) if not df.empty else 0.0
    remaining=income-total
    savings=max(0.0,(remaining/income)*100) if income>0 else 0.0
    ratio=(total/income)*100 if income>0 else 0.0
    if total==0: health='No Expenses Recorded'
    elif income<=0: health='Income Not Configured'
    elif ratio<=50: health='Healthy (High Savings)'
    elif ratio<=75: health='Balanced Spending'
    elif ratio<=95: health='High Utilization'
    else: health='Deficit (Expenses Exceed Income)'
    return {'income':income,'total_expenses':total,'remaining_balance':remaining,'savings_rate':savings,'expense_ratio':ratio,'avg_daily_expense':avg,'health_status':health}

# CALLED BY: Dashboard calculations and budget_compliance()
def category_analysis(df):
    if df.empty: return pd.DataFrame(columns=['category','amount','share_pct','count'])
    out=df.groupby('category')['amount'].agg(amount='sum',count='count').reset_index().sort_values('amount',ascending=False)
    total=out.amount.sum(); out['share_pct']=(out.amount/total*100) if total>0 else 0.0; return out

# CALLED BY: app.py -> summary_payload() for the monthly chart.
def monthly_analysis(df):
    if df.empty: return pd.DataFrame(columns=['month','amount','count'])
    x=df.copy(); x['date_parsed']=pd.to_datetime(x['expense_date'],errors='coerce'); x=x.dropna(subset=['date_parsed'])
    if x.empty: return pd.DataFrame(columns=['month','amount','count'])
    x['month']=x.date_parsed.dt.strftime('%Y-%m'); return x.groupby('month')['amount'].agg(amount='sum',count='count').reset_index().sort_values('month')

def get_highest_category(df):
    c=category_analysis(df)
    return 'None' if c.empty else f"{c.iloc[0]['category']} (₹{c.iloc[0]['amount']:,.0f})"

# CALLED BY: app.py -> /api/budgets
def budget_compliance(df,budgets):
    if not budgets: return pd.DataFrame()
    totals=dict(zip(*[category_analysis(df)[k].tolist() for k in ['category','amount']])) if not df.empty else {}
    rows=[]
    for cat,limit in budgets.items():
        spent=float(totals.get(cat,0)); pct=spent/limit*100 if limit>0 else 0; status='Within Budget' if pct<=80 else ('Near Limit' if pct<=100 else 'Exceeded')
        rows.append({'Category':cat,'Spent':spent,'Budget':float(limit),'Remaining':float(limit)-spent,'Percent_Used':pct,'Status':status})
    return pd.DataFrame(rows).sort_values('Percent_Used',ascending=False)

# CALLED BY: app.py -> /api/dataset
def inspect_dataset(df):
    if df is None or df.empty: return {}
    rows,cols=df.shape
    infos=[]
    for c in df.columns:
        infos.append({'Column':str(c),'Data_Type':str(df[c].dtype),'Null_Count':int(df[c].isna().sum()),'Null_Percentage':float(df[c].isna().mean()*100),'Unique_Values':int(df[c].nunique())})
    return {'rows':rows,'columns':cols,'memory_kb':df.memory_usage(deep=True).sum()/1024,'duplicates':int(df.duplicated().sum()),'numeric_cols':df.select_dtypes(include=[np.number]).columns.tolist(),'categorical_cols':df.select_dtypes(include=['object','category']).columns.tolist(),'datetime_cols':df.select_dtypes(include=['datetime']).columns.tolist(),'column_info':pd.DataFrame(infos)}

# CALLED BY: app.py -> /api/dataset
def get_statistical_summary(df):
    if df is None or df.empty: return pd.DataFrame(),pd.DataFrame()
    n=df.select_dtypes(include=[np.number]); c=df.select_dtypes(include=['object','category'])
    ns=n.describe().T.reset_index().rename(columns={'index':'Column'}) if not n.empty else pd.DataFrame()
    if not ns.empty: ns['skewness']=n.skew().values
    cs=c.describe().T.reset_index().rename(columns={'index':'Column'}) if not c.empty else pd.DataFrame()
    return ns,cs

# CALLED BY: dataset_payload() to choose the analysis path.
def detect_dataset_type(df):
    if df is None or df.empty:return 'empty'
    cols=[str(c).strip().lower() for c in df.columns]
    keywords=['groceries','rent','transportation','utilities','total expenditure','income','savings','investments']
    if sum(any(k in c for c in cols) for k in keywords)>=3:return 'financial_wide'
    amount=any('amount' in c or 'expense' in c or 'cost' in c for c in cols); cat=any('category' in c or 'type' in c or 'item' in c for c in cols); date=any('date' in c or 'month' in c or 'time' in c for c in cols)
    return 'financial_long' if amount and (cat or date) else 'general_tabular'

def process_wide_financial_dataset(df):
    x=df.copy(); x.columns=[str(c).strip() for c in x.columns]
    date_col=next((c for c in x.columns if c.lower() in ['month','date','timestamp','day']),x.columns[0])
    x['parsed_date']=pd.to_datetime(x[date_col],format='%d-%m-%Y',errors='coerce')
    if x.parsed_date.isna().all(): x['parsed_date']=pd.to_datetime(x[date_col],errors='coerce')
    x=x.dropna(subset=['parsed_date']).sort_values('parsed_date')
    income_col=next((c for c in x.columns if c.lower()=='income'),None)
    total_col=next((c for c in x.columns if 'total expenditure' in c.lower() or 'total expense' in c.lower()),None)
    excluded={'parsed_date',date_col}; excluded|={v for v in [income_col,total_col] if v}
    cats=[c for c in x.columns if c not in excluded and pd.api.types.is_numeric_dtype(x[c])]
    totals=x[cats].sum().reset_index(); totals.columns=['Category','Total_Amount']; totals=totals.sort_values('Total_Amount',ascending=False)
    x['Year']=x.parsed_date.dt.year; x['YearMonth']=x.parsed_date.dt.strftime('%Y-%m'); x['Computed_Expenditure']=x[total_col] if total_col else x[cats].sum(axis=1)
    yearly=x.groupby('Year').agg(Total_Expenses=('Computed_Expenditure','sum'),Total_Income=(income_col,'sum') if income_col else ('Computed_Expenditure',lambda s:0.0),Days_Recorded=('parsed_date','count')).reset_index(); yearly['Net_Savings']=yearly.Total_Income-yearly.Total_Expenses; yearly['Savings_Rate']=np.where(yearly.Total_Income>0,yearly.Net_Savings/yearly.Total_Income*100,0)
    monthly=x.groupby('YearMonth').agg(Total_Expenses=('Computed_Expenditure','sum'),Total_Income=(income_col,'sum') if income_col else ('Computed_Expenditure',lambda s:0.0)).reset_index()
    records=[]
    for _,r in x.iterrows():
        ds=r.parsed_date.strftime('%Y-%m-%d')
        for c in cats:
            v=float(r[c])
            if v>0: records.append((v,c,f'{c} expense on {ds}',ds))
    total_income=float(x[income_col].sum()) if income_col else 0.0; total_exp=float(x.Computed_Expenditure.sum())
    return {'cleaned_df':x,'date_col':date_col,'category_cols':cats,'category_totals':totals,'yearly_summary':yearly,'monthly_summary':monthly,'unpivoted_records':records,'total_records':len(x),'total_income':total_income,'total_expenditure':total_exp,'net_balance':total_income-total_exp,'min_date':x.parsed_date.min().strftime('%d %b %Y'),'max_date':x.parsed_date.max().strftime('%d %b %Y')}
