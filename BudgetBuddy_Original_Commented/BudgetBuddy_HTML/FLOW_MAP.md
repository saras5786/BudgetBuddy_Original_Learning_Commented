# Full Project Flow

```text
LOGIN
login.html
  ↓ POST /login
app.py: login()
  ↓
database.py: login_user()
  ↓
budget_buddy.db
  ↓
session
  ↓
/dashboard

DASHBOARD
dashboard.html
  ↓
dashboard.js
  ↓ GET /api/dashboard
app.py: api_dashboard()
  ↓
summary_payload()
  ├─ database.py: get_expenses()
  ├─ database.py: get_budgets()
  └─ analysis.py: calculate_summary(), category_analysis(), monthly_analysis()
  ↓
JSON
  ↓
dashboard.js
  ↓
HTML charts/cards
```

| Action | HTML | JavaScript | Python | Database/analysis |
|---|---|---|---|---|
| Login | login.html | app.js | `/login` | `login_user()` |
| Signup | login.html | app.js | `/signup` | `create_user()` |
| Demo | login.html | app.js | `/demo` | `get_or_create_demo_user()` |
| Dashboard | dashboard.html | dashboard.js | `/api/dashboard` | analysis + expenses |
| Add expense | add_expense.html | add_expense.js | `/api/expenses` | `add_expense()` |
| Batch expense | add_expense.html | add_expense.js | `/api/expenses/batch` | `add_expenses_batch()` |
| Delete expense | expense_history.html | expense_history.js | `/api/expenses/<id>` | `delete_expense()` |
| Budget | budget_planner.html | budget_planner.js | `/api/budgets` | `set_budget()` |
| Profile | profile.html | profile.js | `/api/profile` | `update_profile()` |
| Dataset | dataset_analyzer.html | dataset_analyzer.js | `/api/dataset` | `analysis.py` |
