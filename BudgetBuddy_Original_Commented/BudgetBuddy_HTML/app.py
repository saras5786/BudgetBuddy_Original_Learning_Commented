# ================================================================
# BUDGET BUDDY - MAIN PROGRAM
# ================================================================
# START HERE if you want to understand the complete project.
# Browser page -> HTML -> JavaScript -> /api route in this file
# -> database.py / analysis.py -> JSON -> JavaScript -> HTML.
# ================================================================

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file, flash
from functools import wraps
from pathlib import Path
from io import BytesIO
import pandas as pd
import numpy as np
import secrets

from database import *
from analysis import *

BASE=Path(__file__).resolve().parent
app=Flask(__name__, template_folder=str(BASE/'templates'), static_folder=str(BASE/'static'))
app.secret_key=secrets.token_hex(32)
create_tables()

CATEGORIES=["Groceries","Rent","Transportation","Gym","Utilities","Electricity Bill","Internet & Mobile Bill","Healthcare","Insurance","Investments","Savings","EMI/Loans","Taxes","Dining & Entertainment","Shopping & Wants","Education","Other"]
CURRENCIES=["₹ (INR)","$ (USD)","€ (EUR)","£ (GBP)","¥ (JPY)","Rs (PKR/NPR)"]

@app.context_processor
def common():
    user=get_user(session.get('user_id')) if session.get('user_id') else None
    return {'current_user':user,'currency':session.get('currency','₹'),'categories':CATEGORIES,'currencies':CURRENCIES}

def login_required(fn):
    @wraps(fn)
    def wrapper(*a,**kw):
        if not session.get('user_id'): return redirect(url_for('login'))
        return fn(*a,**kw)
    return wrapper

def current_user(): return get_user(session['user_id'])

def json_records(df):
    if df is None or df.empty:return []
    x=df.copy(); x=x.replace({np.nan:None}); return x.to_dict(orient='records')

def summary_payload(uid):
    user=get_user(uid); df=get_expenses(uid); budgets=get_budgets(uid); s=calculate_summary(df,user[3] if user else 0)
    cats=category_analysis(df); months=monthly_analysis(df)
    return {'summary':s,'top_category':get_highest_category(df),'category_data':json_records(cats),'monthly_data':json_records(months),'budgets':budgets}

# PAGE FLOW: Browser -> / -> login OR dashboard depending on session.
@app.route('/')
def index(): return redirect(url_for('dashboard') if session.get('user_id') else url_for('login'))

# LOGIN FLOW: login.html -> this route -> database.py: login_user() -> dashboard.
@app.route('/login',methods=['GET','POST'])
def login():
    if session.get('user_id'): return redirect(url_for('dashboard'))
    if request.method=='POST':
        user=login_user(request.form.get('email',''),request.form.get('password',''))
        if user: session['user_id']=user[0]; session.setdefault('currency','₹'); return redirect(url_for('dashboard'))
        flash('Invalid email or password.','error')
    return render_template('login.html')

# SIGNUP FLOW: login.html -> this route -> database.py: create_user().
@app.post('/signup')
def signup():
    email=request.form.get('email','').strip(); pw=request.form.get('password',''); confirm=request.form.get('confirm','')
    if not email or not pw: flash('Please provide both email and password.','error')
    elif pw!=confirm: flash('Passwords do not match.','error')
    elif len(pw)<4: flash('Password must contain at least 4 characters.','error')
    elif create_user(email,pw): flash('Account created successfully. Please sign in.','success')
    else: flash('An account with this email address already exists.','error')
    return redirect(url_for('login'))

# DEMO FLOW: login.html -> this route -> database.py: get_or_create_demo_user().
@app.post('/demo')
def demo():
    u=get_or_create_demo_user(); session['user_id']=u[0]; session['currency']='₹'; return redirect(url_for('dashboard'))

@app.get('/logout')
def logout(): session.clear(); return redirect(url_for('login'))

# PAGE FLOW: sidebar -> /dashboard -> dashboard.html -> dashboard.js.
@app.get('/dashboard')
@login_required
def dashboard(): return render_template('dashboard.html',active='Dashboard')

# PAGE FLOW: sidebar -> /budget-planner -> budget_planner.html -> budget_planner.js.
@app.get('/budget-planner')
@login_required
def budget_planner(): return render_template('budget_planner.html',active='Budget Planner')

# PAGE FLOW: sidebar -> /add-expense -> add_expense.html -> add_expense.js.
@app.get('/add-expense')
@login_required
def add_expense_page(): return render_template('add_expense.html',active='Add Expense',today=pd.Timestamp.today().strftime('%Y-%m-%d'))

# PAGE FLOW: sidebar -> /expense-history -> expense_history.html -> expense_history.js.
@app.get('/expense-history')
@login_required
def expense_history(): return render_template('expense_history.html',active='Expense History')

# PAGE FLOW: sidebar -> /dataset-analyzer -> dataset_analyzer.html -> dataset_analyzer.js.
@app.get('/dataset-analyzer')
@login_required
def dataset_analyzer(): return render_template('dataset_analyzer.html',active='Dataset Analyzer')

# PAGE FLOW: sidebar -> /profile -> profile.html -> profile.js.
@app.get('/profile')
@login_required
def profile(): return render_template('profile.html',active='Profile')

@app.get('/api/me')
@login_required
def api_me():
    u=current_user(); return jsonify({'id':u[0],'email':u[1],'name':u[2] or 'User','income':float(u[3] or 0),'currency':session.get('currency','₹')})

# API FLOW: dashboard.js -> this route -> summary_payload() -> database.py + analysis.py.
@app.get('/api/dashboard')
@login_required
def api_dashboard(): return jsonify(summary_payload(session['user_id']))

# API FLOW: expense_history.js -> this route -> database.py: get_expenses().
@app.get('/api/expenses')
@login_required
def api_expenses(): return jsonify(json_records(get_expenses(session['user_id'])))

# API FLOW: add_expense.js -> this route -> database.py: add_expense().
@app.post('/api/expenses')
@login_required
def api_add_expense():
    data=request.get_json(force=True)
    try: amount=float(data.get('amount',0))
    except: amount=0
    if amount<=0:return jsonify({'error':'Please enter a valid amount greater than zero.'}),400
    add_expense(session['user_id'],amount,data.get('category','Other'),data.get('description',''),data.get('date'))
    return jsonify({'message':'Expense recorded successfully.'})

@app.post('/api/expenses/batch')
@login_required
def api_batch():
    data=request.get_json(force=True); rows=data.get('records',[]); valid=[]
    for r in rows:
        try:
            amt=float(r.get('amount',0))
            if amt>0: valid.append((amt,r.get('category','Other'),r.get('description',''),r.get('date')))
        except: pass
    n=add_expenses_batch(session['user_id'],valid); return jsonify({'message':f'Saved {n} expenses successfully.','count':n})

@app.delete('/api/expenses/<int:expense_id>')
@login_required
def api_delete(expense_id):
    n=delete_expense(expense_id,session['user_id']); return jsonify({'message':f'Record {expense_id} deleted.','deleted':n})

@app.delete('/api/expenses')
@login_required
def api_clear():
    n=clear_user_expenses(session['user_id']); return jsonify({'message':f'Cleared {n} expenses from your account.','deleted':n})

@app.get('/api/budgets')
@login_required
def api_budgets():
    df=get_expenses(session['user_id']); budgets=get_budgets(session['user_id']); comp=budget_compliance(df,budgets); return jsonify({'budgets':budgets,'rows':json_records(comp)})

# API FLOW: budget_planner.js -> this route -> database.py: set_budget().
@app.post('/api/budgets')
@login_required
def api_set_budget():
    d=request.get_json(force=True); limit=float(d.get('limit',0));
    if limit<0:return jsonify({'error':'Budget cannot be negative.'}),400
    set_budget(session['user_id'],d.get('category','Other'),limit); return jsonify({'message':'Budget updated successfully.'})

# API FLOW: profile.js -> this route -> database.py: update_profile().
@app.post('/api/profile')
@login_required
def api_profile():
    d=request.get_json(force=True); update_profile(session['user_id'],d.get('name','').strip(),float(d.get('income',0))); session['currency']=d.get('currency','₹'); return jsonify({'message':'Profile updated successfully.'})

@app.get('/api/export/csv')
@login_required
def export_csv():
    df=get_expenses(session['user_id']);
    # Apply optional filters
    q=request.args.get('q','').lower(); cat=request.args.get('category','All'); minamt=float(request.args.get('min_amount',0) or 0); order=request.args.get('order','Newest First')
    if cat!='All': df=df[df.category==cat]
    if q: df=df[df.description.fillna('').str.lower().str.contains(q) | df.category.fillna('').str.lower().str.contains(q)]
    df=df[df.amount>=minamt]
    if order=='Oldest First': df=df.sort_values('expense_date')
    elif order=='Highest Amount': df=df.sort_values('amount',ascending=False)
    elif order=='Lowest Amount': df=df.sort_values('amount')
    else: df=df.sort_values(['expense_date','id'],ascending=[False,False])
    raw=df.to_csv(index=False).encode(); return send_file(BytesIO(raw),mimetype='text/csv',as_attachment=True,download_name='budget_buddy_expenses.csv')

@app.get('/api/export/excel')
@login_required
def export_excel():
    df=get_expenses(session['user_id'])
    q=request.args.get('q','').lower(); cat=request.args.get('category','All'); minamt=float(request.args.get('min_amount',0) or 0); order=request.args.get('order','Newest First')
    if cat!='All': df=df[df.category==cat]
    if q: df=df[df.description.fillna('').str.lower().str.contains(q) | df.category.fillna('').str.lower().str.contains(q)]
    df=df[df.amount>=minamt]
    if order=='Oldest First': df=df.sort_values('expense_date')
    elif order=='Highest Amount': df=df.sort_values('amount',ascending=False)
    elif order=='Lowest Amount': df=df.sort_values('amount')
    else: df=df.sort_values(['expense_date','id'],ascending=[False,False])
    bio=BytesIO()
    with pd.ExcelWriter(bio,engine='openpyxl') as writer: df.to_excel(writer,index=False,sheet_name='Expenses')
    bio.seek(0); return send_file(bio,mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',as_attachment=True,download_name='budget_buddy_expenses.xlsx')

# API FLOW: dataset_analyzer.js -> this route -> pandas -> analysis.py.
@app.post('/api/dataset')
@login_required
def analyze_dataset():
    if 'file' not in request.files:return jsonify({'error':'No dataset file uploaded.'}),400
    f=request.files['file']; name=f.filename or ''
    try:
        if name.lower().endswith('.csv'): df=pd.read_csv(f)
        elif name.lower().endswith(('.xlsx','.xls')): df=pd.read_excel(f)
        else:return jsonify({'error':'Only CSV and Excel files are supported.'}),400
    except Exception as e:return jsonify({'error':f'Error reading file: {e}'}),400
    return jsonify(dataset_payload(df,name))

def dataset_payload(df,source):
    if df is None or df.empty:return {'source':source,'empty':True}
    ins=inspect_dataset(df); num,cat=get_statistical_summary(df); payload={'source':source,'rows':len(df),'columns':len(df.columns),'type':detect_dataset_type(df),'inspection':{k:v for k,v in ins.items() if k!='column_info'},'column_info':json_records(ins['column_info']),'preview':json_records(df.head(100)),'numeric_stats':json_records(num),'categorical_stats':json_records(cat),'columns':[str(c) for c in df.columns]}
    if payload['type']=='financial_wide':
        r=process_wide_financial_dataset(df); payload['financial']={'total_records':r['total_records'],'total_income':r['total_income'],'total_expenditure':r['total_expenditure'],'net_balance':r['net_balance'],'min_date':r['min_date'],'max_date':r['max_date'],'category_totals':json_records(r['category_totals'].rename(columns={'Category':'category','Total_Amount':'amount'})),'yearly_summary':json_records(r['yearly_summary']),'monthly_summary':json_records(r['monthly_summary']),'import_count':len(r['unpivoted_records'])}
        # Store import rows temporarily in session for explicit import.
        session['dataset_import_records']=[list(x) for x in r['unpivoted_records']]
    return payload

@app.post('/api/dataset/import')
@login_required
def import_dataset():
    records=session.get('dataset_import_records',[]); n=add_expenses_batch(session['user_id'],records); session.pop('dataset_import_records',None); return jsonify({'message':f'Successfully imported {n:,} expenses into your account.','count':n})

@app.get('/api/sample-dataset')
@login_required
def sample_dataset():
    path=BASE/'data'/'sample_financial_data.csv'
    df=pd.read_csv(path); return jsonify(dataset_payload(df,'2020-2026 Multi-Year Financial Dataset'))

@app.get('/api/dataset/chart')
@login_required
def dataset_chart():
    # Kept as a simple JSON endpoint for the browser chart builder; dataset itself is supplied client-side.
    return jsonify({'message':'Use the chart builder in the Dataset Analyzer page.'})

@app.get('/download/apk')
def download_apk():
    path=BASE/'data'/'BudgetBuddy-v1.0.apk'
    if not path.exists(): return jsonify({'error':'APK not found'}),404
    return send_file(path,as_attachment=True,download_name='BudgetBuddy-v1.0.apk',mimetype='application/vnd.android.package-archive')

if __name__=='__main__':
    app.run(host='127.0.0.1',port=5000,debug=True)
