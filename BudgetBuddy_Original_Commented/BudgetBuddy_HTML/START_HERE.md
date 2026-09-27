# Budget Buddy — Start Here

This is the ORIGINAL Budget Buddy project. Login, design, pages and features are preserved. The added comments/docs explain how files call each other.

## First reading order
1. `app.py`
2. `templates/login.html`
3. `database.py`
4. `templates/dashboard.html`
5. `static/js/dashboard.js`
6. `analysis.py`

## Login flow
`login.html` -> form POST -> `app.py: login()` -> `database.py: login_user()` -> SQLite `users` -> session -> `/dashboard`.

Demo: `login.html` -> `app.py: demo()` -> `database.py: get_or_create_demo_user()` -> dashboard.

## Dashboard flow
`dashboard.html` -> `dashboard.js` -> `GET /api/dashboard` -> `app.py: api_dashboard()` -> `summary_payload()` -> `database.py` + `analysis.py` -> JSON -> `dashboard.js` -> charts/cards.

## Add Expense flow
`add_expense.html` -> `add_expense.js` -> `POST /api/expenses` -> `app.py: api_add_expense()` -> `database.py: add_expense()` -> SQLite -> JSON -> JavaScript.

## Budget flow
`budget_planner.html` -> `budget_planner.js` -> `/api/budgets` -> `app.py` -> `database.py: set_budget()` -> SQLite.

## Expense History flow
`expense_history.html` -> `expense_history.js` -> `/api/expenses` -> `database.py: get_expenses()` -> JavaScript table.

## Dataset flow
`dataset_analyzer.html` -> `dataset_analyzer.js` -> `/api/dataset` -> `app.py` -> pandas reads file -> `analysis.py` -> JSON -> page.

## Profile flow
`profile.html` -> `profile.js` -> `/api/me` or `/api/profile` -> `app.py` -> `database.py`.

### How to trace any line
If JavaScript contains `BB.send('/api/expenses', ...)`, search for `/api/expenses` in `app.py`.
If HTML contains `url_for('budget_planner')`, search for `def budget_planner` in `app.py`.
