import sqlite3
from pathlib import Path
from datetime import date, timedelta
import random

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "bankwise.db"

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with get_connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, email TEXT, phone TEXT, city TEXT,
            created_at TEXT DEFAULT CURRENT_DATE
        );
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL, account_number TEXT UNIQUE NOT NULL,
            account_type TEXT NOT NULL, balance REAL NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'Active',
            FOREIGN KEY(customer_id) REFERENCES customers(id)
        );
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL, txn_type TEXT NOT NULL,
            amount REAL NOT NULL, description TEXT, channel TEXT,
            txn_date TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Completed',
            risk_score INTEGER DEFAULT 0,
            FOREIGN KEY(account_id) REFERENCES accounts(id)
        );
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL, loan_type TEXT NOT NULL,
            principal REAL NOT NULL, interest_rate REAL NOT NULL,
            tenure_months INTEGER NOT NULL, outstanding REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'Under Review',
            FOREIGN KEY(customer_id) REFERENCES customers(id)
        );
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL, card_type TEXT NOT NULL,
            last_four TEXT NOT NULL, limit_amount REAL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'Active',
            FOREIGN KEY(customer_id) REFERENCES customers(id)
        );
        """)
        conn.commit()

def seed_demo_data():
    with get_connection() as conn:
        if conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0] > 0:
            return
        people = [
            ("Aarav Sharma","aarav@example.com","9000000001","Pune"),
            ("Ananya Patel","ananya@example.com","9000000002","Mumbai"),
            ("Rohan Mehta","rohan@example.com","9000000003","Nashik"),
            ("Isha Kulkarni","isha@example.com","9000000004","Pune"),
            ("Kabir Shah","kabir@example.com","9000000005","Nagpur"),
            ("Meera Joshi","meera@example.com","9000000006","Kolhapur"),
            ("Vivaan Desai","vivaan@example.com","9000000007","Mumbai"),
            ("Sara Khan","sara@example.com","9000000008","Pune"),
        ]
        conn.executemany("INSERT INTO customers(name,email,phone,city) VALUES(?,?,?,?)", people)
        customers = conn.execute("SELECT id FROM customers").fetchall()
        rng = random.Random(42)
        account_ids = []
        for i, c in enumerate(customers):
            cur = conn.execute(
                "INSERT INTO accounts(customer_id,account_number,account_type,balance,status) VALUES(?,?,?,?,?)",
                (c["id"], f"BW{100000+i}", ["Savings","Current","Salary"][i%3], rng.randint(18000,250000), "Active")
            )
            account_ids.append(cur.lastrowid)
            if i % 2 == 0:
                conn.execute("INSERT INTO cards(customer_id,card_type,last_four,limit_amount,status) VALUES(?,?,?,?,?)",
                             (c["id"], "Debit", f"{rng.randint(1000,9999)}", 0, "Active"))
            else:
                conn.execute("INSERT INTO cards(customer_id,card_type,last_four,limit_amount,status) VALUES(?,?,?,?,?)",
                             (c["id"], "Credit", f"{rng.randint(1000,9999)}", rng.choice([50000,75000,100000]), "Active"))
        descriptions = ["Grocery store","Utility bill","Online shopping","Salary credit","Restaurant","ATM cash withdrawal","Fuel station","UPI transfer"]
        for _ in range(110):
            aid = rng.choice(account_ids)
            typ = rng.choices(["Credit","Debit"], weights=[3,7])[0]
            amount = round(rng.uniform(250,18000),2)
            risk = rng.choice([4,8,12,18,25,35,62,78,91])
            dt = date.today() - timedelta(days=rng.randint(0,89))
            conn.execute("""INSERT INTO transactions(account_id,txn_type,amount,description,channel,txn_date,status,risk_score)
                            VALUES(?,?,?,?,?,?,?,?)""",
                         (aid,typ,amount, rng.choice(descriptions), rng.choice(["UPI","Card","Net Banking","ATM"]),
                          dt.isoformat(),"Flagged" if risk >= 75 else "Completed",risk))
        for i,c in enumerate(customers[:6]):
            principal = [350000,700000,150000,500000,250000,900000][i]
            outstanding = round(principal * rng.uniform(.35,.92),2)
            conn.execute("INSERT INTO loans(customer_id,loan_type,principal,interest_rate,tenure_months,outstanding,status) VALUES(?,?,?,?,?,?,?)",
                         (c["id"], ["Home","Personal","Vehicle","Education"][i%4], principal, [8.5,10.5,9.2,7.8][i%4], rng.choice([24,36,60,120]), outstanding, ["Active","Under Review","Active"][i%3]))
        conn.commit()

def query_df(sql, params=()):
    import pandas as pd
    with get_connection() as conn:
        return pd.read_sql_query(sql, conn, params=params)

def execute(sql, params=()):
    with get_connection() as conn:
        cur = conn.execute(sql, params)
        conn.commit()
        return cur.lastrowid

def add_transaction(account_id, txn_type, amount, description, channel="Branch"):
    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")
    with get_connection() as conn:
        account = conn.execute("SELECT balance,status FROM accounts WHERE id=?", (account_id,)).fetchone()
        if not account:
            raise ValueError("Account not found.")
        if account["status"] != "Active":
            raise ValueError("Only active accounts can transact.")
        if txn_type == "Debit" and account["balance"] < amount:
            raise ValueError("Insufficient demo account balance.")
        new_balance = account["balance"] + amount if txn_type == "Credit" else account["balance"] - amount
        conn.execute("UPDATE accounts SET balance=? WHERE id=?", (new_balance, account_id))
        risk = 82 if amount >= 100000 else (45 if amount >= 50000 else 12)
        status = "Flagged" if risk >= 75 else "Completed"
        conn.execute("""INSERT INTO transactions(account_id,txn_type,amount,description,channel,txn_date,status,risk_score)
                        VALUES(?,?,?,?,?,?,?,?)""",
                     (account_id,txn_type,amount,description,channel,date.today().isoformat(),status,risk))
        conn.commit()
