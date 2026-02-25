from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import csv
import io
import os
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'expenses.db')

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            category TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    conn = get_db()
    expenses = conn.execute('SELECT * FROM expenses ORDER BY date DESC').fetchall()
    conn.close()
    return jsonify([dict(row) for row in expenses])

@app.route('/api/expenses/upload', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'File must be a CSV'}), 400
    
    try:
        stream = io.StringIO(file.stream.read().decode('utf-8'))
        reader = csv.DictReader(stream)
        
        conn = get_db()
        count = 0
        for row in reader:
            # Handle different possible column names
            description = row.get('description') or row.get('Description') or ''
            amount = row.get('amount') or row.get('Amount') or 0
            date = row.get('date') or row.get('Date') or ''
            category = row.get('category') or row.get('Category') or ''
            
            conn.execute(
                'INSERT INTO expenses (description, amount, date, category) VALUES (?, ?, ?, ?)',
                (description, float(amount), date, category)
            )
            count += 1
        
        conn.commit()
        conn.close()
        return jsonify({'message': f'Successfully imported {count} expenses'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/expenses/summary', methods=['GET'])
def get_summary():
    conn = get_db()
    summary = conn.execute('''
        SELECT category, SUM(amount) as total
        FROM expenses
        GROUP BY category
        ORDER BY total DESC
    ''').fetchall()
    conn.close()
    return jsonify([{'category': row['category'], 'total': row['total']} for row in summary])

@app.route('/api/expenses/timeseries', methods=['GET'])
def get_timeseries():
    period = request.args.get('period', 'month')
    if period not in ('week', 'month', 'year'):
        return jsonify({'error': 'Invalid period. Must be week, month, or year'}), 400

    now = datetime.now()
    conn = get_db()

    if period == 'week':
        start_of_week = now - timedelta(days=now.weekday())
        start_date = start_of_week.strftime('%Y-%m-%d')
        end_date = (start_of_week + timedelta(days=6)).strftime('%Y-%m-%d')
        rows = conn.execute('''
            SELECT date, SUM(amount) as total
            FROM expenses
            WHERE date >= ? AND date <= ?
            GROUP BY date
            ORDER BY date ASC
        ''', (start_date, end_date)).fetchall()
    elif period == 'month':
        start_date = now.strftime('%Y-%m-01')
        if now.month == 12:
            end_date = f'{now.year + 1}-01-01'
        else:
            end_date = f'{now.year}-{now.month + 1:02d}-01'
        rows = conn.execute('''
            SELECT date, SUM(amount) as total
            FROM expenses
            WHERE date >= ? AND date < ?
            GROUP BY date
            ORDER BY date ASC
        ''', (start_date, end_date)).fetchall()
    else:  # year
        start_date = f'{now.year}-01-01'
        end_date = f'{now.year + 1}-01-01'
        rows = conn.execute('''
            SELECT substr(date, 1, 7) as month, SUM(amount) as total
            FROM expenses
            WHERE date >= ? AND date < ?
            GROUP BY substr(date, 1, 7)
            ORDER BY month ASC
        ''', (start_date, end_date)).fetchall()

    conn.close()

    if period == 'year':
        result = [{'date': row['month'], 'total': row['total']} for row in rows]
    else:
        result = [{'date': row['date'], 'total': row['total']} for row in rows]

    return jsonify(result)


@app.route('/api/expenses/periods', methods=['GET'])
def get_available_periods():
    now = datetime.now()
    conn = get_db()

    # Check week
    start_of_week = now - timedelta(days=now.weekday())
    week_start = start_of_week.strftime('%Y-%m-%d')
    week_end = (start_of_week + timedelta(days=6)).strftime('%Y-%m-%d')
    week_count = conn.execute(
        'SELECT COUNT(*) as cnt FROM expenses WHERE date >= ? AND date <= ?',
        (week_start, week_end)
    ).fetchone()['cnt']

    # Check month
    month_start = now.strftime('%Y-%m-01')
    if now.month == 12:
        month_end = f'{now.year + 1}-01-01'
    else:
        month_end = f'{now.year}-{now.month + 1:02d}-01'
    month_count = conn.execute(
        'SELECT COUNT(*) as cnt FROM expenses WHERE date >= ? AND date < ?',
        (month_start, month_end)
    ).fetchone()['cnt']

    # Check year
    year_start = f'{now.year}-01-01'
    year_end = f'{now.year + 1}-01-01'
    year_count = conn.execute(
        'SELECT COUNT(*) as cnt FROM expenses WHERE date >= ? AND date < ?',
        (year_start, year_end)
    ).fetchone()['cnt']

    conn.close()

    return jsonify({
        'week': week_count > 0,
        'month': month_count > 0,
        'year': year_count > 0
    })


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8080, debug=True)
