from flask import Flask, render_template, request, redirect, url_for, send_file
from database import (init_db, get_all_clients, get_client, get_client_accounts,
                      get_client_reports, get_report, get_report_balances, get_db)
from calculations import calculate_sacs, calculate_tcc, calculate_private_reserve_target
from pdf_generator import generate_sacs_pdf, generate_tcc_pdf
import io
import zipfile

from datetime import datetime, date

def calculate_age(dob_str):
    """Calculate current age from date of birth string."""
    if not dob_str:
        return None
    try:
        dob = datetime.strptime(str(dob_str), '%Y-%m-%d').date()
        today = date.today()
        age = today.year - dob.year
        if (today.month, today.day) < (dob.month, dob.day):
            age -= 1
        return age
    except:
        return None
    
app = Flask(__name__)

with app.app_context():
    init_db()

# ── HOME ────────────────────────────────────────────────────
@app.route('/')
def index():
    clients = get_all_clients()
    return render_template('index.html', clients=clients)

# ── ADD CLIENT ──────────────────────────────────────────────
@app.route('/client/new', methods=['GET', 'POST'])
def new_client():
    if request.method == 'POST':
        has_partner = 1 if request.form.get('has_partner') else 0

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO clients (
                name, has_partner, name_partner,
                dob, dob_partner,
                age, age_partner,
                ssn_last4, ssn_last4_partner,
                monthly_salary, monthly_expenses, private_reserve_target
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            request.form['name'],
            has_partner,
            request.form.get('name_partner') or None,
            request.form.get('dob') or None,
            request.form.get('dob_partner') or None,
            request.form.get('age') or None,
            request.form.get('age_partner') or None,
            request.form.get('ssn_last4') or None,
            request.form.get('ssn_last4_partner') or None,
            float(request.form.get('monthly_salary') or 0),
            float(request.form.get('monthly_expenses') or 0),
            float(request.form.get('private_reserve_target') or 0)
        ))
        client_id = cursor.lastrowid

        account_types      = request.form.getlist('account_type[]')
        account_categories = request.form.getlist('account_category[]')
        account_owners     = request.form.getlist('account_owner[]')
        account_last4s     = request.form.getlist('account_last4[]')

        for i in range(len(account_types)):
            if account_types[i]:
                cursor.execute('''
                    INSERT INTO accounts
                        (client_id, owner, account_type, account_category, last4)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    client_id,
                    account_owners[i],
                    account_types[i],
                    account_categories[i],
                    account_last4s[i] if i < len(account_last4s) else ''
                ))

        conn.commit()
        conn.close()
        return redirect(url_for('client_detail', client_id=client_id))

    return render_template('client.html', client=None, accounts=[])

# ── CLIENT DETAIL ───────────────────────────────────────────
@app.route('/client/<int:client_id>')
def client_detail(client_id):
    client  = get_client(client_id)
    accounts = get_client_accounts(client_id)
    reports  = get_client_reports(client_id)
    return render_template('index.html',
                           clients=get_all_clients(),
                           selected_client=client,
                           accounts=accounts,
                           reports=reports)

# ── GENERATE REPORT ─────────────────────────────────────────
@app.route('/client/<int:client_id>/report', methods=['GET', 'POST'])
def generate_report(client_id):
    client   = get_client(client_id)
    accounts = get_client_accounts(client_id)

    if request.method == 'POST':
        conn   = get_db()
        cursor = conn.cursor()

        inflow                  = float(request.form.get('inflow') or 0)
        outflow                 = float(request.form.get('outflow') or 0)
        private_reserve_balance = float(request.form.get('private_reserve_balance') or 0)
        quarter                 = request.form.get('quarter', 'Q1')
        year                    = int(request.form.get('year') or 2025)

        sacs = calculate_sacs(inflow, outflow)

        cursor.execute('''
            INSERT INTO reports
                (client_id, quarter, year, inflow, outflow, excess, private_reserve_balance)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (client_id, quarter, year, inflow, outflow,
              sacs['excess'], private_reserve_balance))

        report_id = cursor.lastrowid

        for account in accounts:
            balance_key = f'balance_{account["id"]}'
            balance     = float(request.form.get(balance_key) or 0)
            cursor.execute('''
                INSERT INTO report_balances (report_id, account_id, balance)
                VALUES (?, ?, ?)
            ''', (report_id, account['id'], balance))

        conn.commit()
        conn.close()
        return redirect(url_for('download_reports',
                                client_id=client_id, report_id=report_id))

    return render_template('report.html', client=client, accounts=accounts)

# ── DOWNLOAD REPORTS ────────────────────────────────────────
@app.route('/client/<int:client_id>/download/<int:report_id>')
def download_reports(client_id, report_id):
    client   = get_client(client_id)
    report   = get_report(report_id)
    balances = get_report_balances(report_id)

    sacs_data = calculate_sacs(report['inflow'], report['outflow'])
    tcc_data  = calculate_tcc(balances)

    # Auto-update ages from DOB before generating PDF
    conn_age = get_db()
    age1 = calculate_age(client['dob'])
    age2 = calculate_age(client['dob_partner']) if client['dob_partner'] else None
    if age1 or age2:
        conn_age.execute('''
            UPDATE clients SET age = ?, age_partner = ? WHERE id = ?
        ''', (age1, age2, client_id))
        conn_age.commit()
    conn_age.close()

    # Reload client with updated ages
    client = get_client(client_id)

    client_dict = dict(client)

    sacs_buffer = generate_sacs_pdf(client_dict, sacs_data,
                                    report['private_reserve_balance'])
    tcc_buffer  = generate_tcc_pdf(client_dict, tcc_data)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        zf.writestr(
            f"SACS_{client['name']}_{report['quarter']}{report['year']}.pdf",
            sacs_buffer.read()
        )
        zf.writestr(
            f"TCC_{client['name']}_{report['quarter']}{report['year']}.pdf",
            tcc_buffer.read()
        )

    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f"Reports_{client['name']}_{report['quarter']}{report['year']}.zip"
    )

if __name__ == '__main__':
    app.run(debug=True)