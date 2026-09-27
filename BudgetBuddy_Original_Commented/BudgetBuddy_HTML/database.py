# ================================================================
# BUDGET BUDDY - DATABASE FUNCTIONS
# ================================================================
# This file stores and reads users, expenses and budgets.
# Typical flow: app.py route -> function here -> SQLite -> result.
# ================================================================

import sqlite3
import hashlib
from pathlib import Path
import pandas as pd

DATABASE_NAME = Path(__file__).resolve().parent / "budget_buddy.db"

# STEP: Open the SQLite database file.
def get_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# STEP: Create the users, expenses and budgets tables.
def create_tables():
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        name TEXT,
        income REAL DEFAULT 0
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        description TEXT,
        expense_date TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        category TEXT NOT NULL,
        monthly_limit REAL NOT NULL,
        UNIQUE(user_id, category),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )""")
    conn.commit(); conn.close()

# CALLED BY: app.py -> /signup
def create_user(email, password):
    conn = get_connection()
    try:
        conn.execute("INSERT INTO users (email,password) VALUES (?,?)", (email.strip(), hash_password(password)))
        conn.commit(); return True
    except sqlite3.IntegrityError:
        return False
    finally: conn.close()

# CALLED BY: app.py -> /login
def login_user(email, password):
    conn = get_connection()
    row = conn.execute("SELECT id,email,name,income FROM users WHERE email=? AND password=?", (email.strip(), hash_password(password))).fetchone()
    conn.close(); return tuple(row) if row else None

# CALLED BY: app.py -> /demo
def get_or_create_demo_user():
    conn = get_connection()
    row = conn.execute("SELECT id,email,name,income FROM users WHERE email=?", ("demo@budgetbuddy.app",)).fetchone()
    if not row:
        conn.execute("INSERT INTO users (email,password,name,income) VALUES (?,?,?,?)", ("demo@budgetbuddy.app", hash_password("demo123"), "Demo User", 60000.0))
        conn.commit()
        row = conn.execute("SELECT id,email,name,income FROM users WHERE email=?", ("demo@budgetbuddy.app",)).fetchone()
    conn.close(); return tuple(row)

def get_user(user_id):
    conn = get_connection(); row = conn.execute("SELECT id,email,name,income FROM users WHERE id=?", (user_id,)).fetchone(); conn.close()
    return tuple(row) if row else None

def update_profile(user_id, name, income):
    conn = get_connection(); conn.execute("UPDATE users SET name=?, income=? WHERE id=?", (str(name).strip(), float(income), user_id)); conn.commit(); conn.close()

# CALLED BY: app.py -> /api/expenses
def add_expense(user_id, amount, category, description, expense_date):
    conn = get_connection(); conn.execute("INSERT INTO expenses (user_id,amount,category,description,expense_date) VALUES (?,?,?,?,?)", (user_id,float(amount),str(category).strip(),str(description or '').strip(),str(expense_date))); conn.commit(); conn.close()

def add_expenses_batch(user_id, records):
    valid = [(user_id,float(r[0]),str(r[1]).strip(),str(r[2] if len(r)>2 else '').strip(),str(r[3])) for r in records if float(r[0]) > 0]
    if not valid: return 0
    conn=get_connection(); cur=conn.cursor(); cur.executemany("INSERT INTO expenses (user_id,amount,category,description,expense_date) VALUES (?,?,?,?,?)", valid); count=cur.rowcount; conn.commit(); conn.close(); return count

# CALLED BY: Dashboard, Expense History and analysis routes.
def get_expenses(user_id):
    conn=get_connection(); df=pd.read_sql_query("SELECT id,amount,category,description,expense_date FROM expenses WHERE user_id=? ORDER BY expense_date DESC,id DESC", conn, params=(user_id,)); conn.close(); return df

def delete_expense(expense_id,user_id):
    conn=get_connection(); cur=conn.cursor(); cur.execute("DELETE FROM expenses WHERE id=? AND user_id=?",(expense_id,user_id)); deleted=cur.rowcount; conn.commit(); conn.close(); return deleted

def clear_user_expenses(user_id):
    conn=get_connection(); cur=conn.cursor(); cur.execute("DELETE FROM expenses WHERE user_id=?",(user_id,)); deleted=cur.rowcount; conn.commit(); conn.close(); return deleted

# CALLED BY: app.py -> /api/budgets
def set_budget(user_id,category,monthly_limit):
    conn=get_connection(); conn.execute("INSERT INTO budgets (user_id,category,monthly_limit) VALUES (?,?,?) ON CONFLICT(user_id,category) DO UPDATE SET monthly_limit=excluded.monthly_limit",(user_id,str(category).strip(),float(monthly_limit))); conn.commit(); conn.close()

def get_budgets(user_id):
    conn=get_connection(); rows=conn.execute("SELECT category,monthly_limit FROM budgets WHERE user_id=?",(user_id,)).fetchall(); conn.close(); return {r[0]:r[1] for r in rows}
