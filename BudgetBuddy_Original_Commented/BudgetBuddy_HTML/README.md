# Budget Buddy — Original + Learning Comments

This package keeps the original project, including login, dashboard, budget planner, add expense, expense history, dataset analyzer, profile, styling, database and Android APK.

Only comments and learning guides were added.

Read `START_HERE.md` first.

## Run
```powershell
py -m pip install -r requirements.txt
py app.py
```
Open `http://127.0.0.1:5000`.

## Important dependency note
To preserve the original Excel export/upload feature, this original web version uses Flask and openpyxl in addition to pandas, NumPy and Matplotlib. Removing those would change the original application.
