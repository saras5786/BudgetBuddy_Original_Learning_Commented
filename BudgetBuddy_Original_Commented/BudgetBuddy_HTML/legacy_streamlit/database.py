import sqlite3
import hashlib
import pandas as pd

DATABASE_NAME = "budget_buddy.db"


def get_connection():
    return sqlite3.connect(DATABASE_NAME)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT,
            income REAL DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            expense_date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            monthly_limit REAL NOT NULL,
            UNIQUE(user_id, category),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


def create_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO users (email, password)
            VALUES (?, ?)
            """,
            (email, hash_password(password))
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def login_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, email, name, income
        FROM users
        WHERE email = ? AND password = ?
        """,
        (email, hash_password(password))
    )

    user = cursor.fetchone()
    conn.close()
    return user


def get_or_create_demo_user():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, email, name, income FROM users WHERE email = ?", ("demo@budgetbuddy.app",))
    user = cursor.fetchone()

    if not user:
        cursor.execute(
            """
            INSERT INTO users (email, password, name, income)
            VALUES (?, ?, ?, ?)
            """,
            ("demo@budgetbuddy.app", hash_password("demo123"), "Demo User", 60000.0)
        )
        conn.commit()
        user_id = cursor.lastrowid
        user = (user_id, "demo@budgetbuddy.app", "Demo User", 60000.0)

    conn.close()
    return user


def update_profile(user_id, name, income):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE users
        SET name = ?, income = ?
        WHERE id = ?
        """,
        (name, float(income), user_id)
    )

    conn.commit()
    conn.close()


def get_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, email, name, income
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    )

    user = cursor.fetchone()
    conn.close()
    return user


def add_expense(user_id, amount, category, description, expense_date):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO expenses
        (user_id, amount, category, description, expense_date)
        VALUES (?, ?, ?, ?, ?)
        """,
        (user_id, float(amount), str(category).strip(), str(description).strip(), str(expense_date))
    )

    conn.commit()
    conn.close()


def add_expenses_batch(user_id, records):
    if not records:
        return 0

    conn = get_connection()
    cursor = conn.cursor()

    formatted_records = [
        (user_id, float(r[0]), str(r[1]).strip(), str(r[2]).strip() if len(r) > 2 else "", str(r[3]))
        for r in records
        if float(r[0]) > 0
    ]

    cursor.executemany(
        """
        INSERT INTO expenses
        (user_id, amount, category, description, expense_date)
        VALUES (?, ?, ?, ?, ?)
        """,
        formatted_records
    )

    count = cursor.rowcount
    conn.commit()
    conn.close()
    return count


def get_expenses(user_id):
    conn = get_connection()

    query = """
        SELECT
            id,
            amount,
            category,
            description,
            expense_date
        FROM expenses
        WHERE user_id = ?
        ORDER BY expense_date DESC, id DESC
    """

    df = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()
    return df


def delete_expense(expense_id, user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM expenses
        WHERE id = ? AND user_id = ?
        """,
        (expense_id, user_id)
    )

    conn.commit()
    conn.close()


def clear_user_expenses(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM expenses WHERE user_id = ?", (user_id,))
    deleted = cursor.rowcount

    conn.commit()
    conn.close()
    return deleted


def set_budget(user_id, category, monthly_limit):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO budgets (user_id, category, monthly_limit)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, category) DO UPDATE SET monthly_limit = excluded.monthly_limit
    """, (user_id, str(category).strip(), float(monthly_limit)))

    conn.commit()
    conn.close()


def get_budgets(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT category, monthly_limit FROM budgets WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()

    return {row[0]: row[1] for row in rows}
