import sqlite3
import os

DATABASE = os.environ.get('DB_PATH', 'aw_portal.db')

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            has_partner INTEGER DEFAULT 0,
            name_partner TEXT,
            dob TEXT,
            dob_partner TEXT,
            age INTEGER,
            age_partner INTEGER,
            ssn_last4 TEXT,
            ssn_last4_partner TEXT,
            monthly_salary REAL,
            monthly_expenses REAL,
            private_reserve_target REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            owner TEXT,
            account_type TEXT,
            account_category TEXT,
            last4 TEXT,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        );

        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            quarter TEXT,
            year INTEGER,
            inflow REAL,
            outflow REAL,
            excess REAL,
            private_reserve_balance REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        );

        CREATE TABLE IF NOT EXISTS report_balances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id INTEGER,
            account_id INTEGER,
            balance REAL,
            FOREIGN KEY (report_id) REFERENCES reports(id),
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        );
    ''')
    
    conn.commit()
    conn.close()

def get_all_clients():
    conn = get_db()
    clients = conn.execute('SELECT * FROM clients ORDER BY name').fetchall()
    conn.close()
    return clients

def get_client(client_id):
    conn = get_db()
    client = conn.execute('SELECT * FROM clients WHERE id = ?', (client_id,)).fetchone()
    conn.close()
    return client

def get_client_accounts(client_id):
    conn = get_db()
    accounts = conn.execute(
        'SELECT * FROM accounts WHERE client_id = ? ORDER BY account_category, owner',
        (client_id,)
    ).fetchall()
    conn.close()
    return accounts

def get_client_reports(client_id):
    conn = get_db()
    reports = conn.execute(
        'SELECT * FROM reports WHERE client_id = ? ORDER BY year DESC, quarter DESC',
        (client_id,)
    ).fetchall()
    conn.close()
    return reports

def get_report(report_id):
    conn = get_db()
    report = conn.execute('SELECT * FROM reports WHERE id = ?', (report_id,)).fetchone()
    conn.close()
    return report

def get_report_balances(report_id):
    conn = get_db()
    balances = conn.execute('''
        SELECT rb.*, a.account_type, a.account_category, a.owner, a.last4
        FROM report_balances rb
        JOIN accounts a ON rb.account_id = a.id
        WHERE rb.report_id = ?
    ''', (report_id,)).fetchall()
    conn.close()
    return balances