from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import csv
import io
import os
import re
import calendar
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'expenses.db')

def get_db():
    """
    Connects to the SQLite database and sets up the row factory for enhanced
    dictionary-like access to query results.

    :return: A connection object configured with a row factory for dictionary-like access
    :rtype: sqlite3.Connection
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    pass
    return conn

def normalize_date(date_str):
    """
    Normalize a date string into the standard format `YYYY-MM-DD`. If the input date
    string is already in the desired format, it will be returned unmodified. The function
    attempts to parse and convert date strings provided in formats such as `MM/DD/YYYY`
    or `MM-DD-YYYY` using `/` or `-` as separators. If the date string does not match
    any known formats, it is returned as-is.

    :param date_str: The input date string to normalize.
    :type date_str: str
    :return: The normalized date string in the format `YYYY-MM-DD`, or the original
        string if no known formats matched.
    :rtype: str
    """
    date_str = date_str.strip()
    # Already in YYYY-MM-DD format
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return date_str
    # Try M/D/YYYY or MM/DD/YYYY (with / or - separators)
    for fmt in ('%m/%d/%Y', '%m-%d-%Y'):
        try:
            return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    # Return as-is if no format matched
    return date_str


def init_db():
    """
    Initializes the database by creating the `expenses` table if it does not already exist.
    This function also includes a migration step to ensure the `excluded` column is present
    in existing databases.

    The `expenses` table consists of the following fields:
    - id: An INTEGER primary key that auto-increments.
    - description: A TEXT field for storing the description of the expense.
    - amount: A REAL field for the expense amount.
    - date: A TEXT field for the date of the expense.
    - category: A TEXT field for categorizing the expense.
    - excluded: An INTEGER field used as a flag, defaulting to 0.

    If the `excluded` column is missing in existing databases, the function adds it
    after checking the table schema via PRAGMA table_info.

    :return: None
    """
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            excluded INTEGER NOT NULL DEFAULT 0
        )
    ''')
    # Migration: add excluded column to existing databases if missing
    existing_columns = {row['name'] for row in conn.execute('PRAGMA table_info(expenses)').fetchall()}
    if 'excluded' not in existing_columns:
        conn.execute('ALTER TABLE expenses ADD COLUMN excluded INTEGER NOT NULL DEFAULT 0')
    conn.commit()
    conn.close()


@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    """
    Fetches all expense records from the database, ordered by date in descending order.

    This function connects to the database, queries the expenses table, and retrieves
    all expense records. The records are then converted into a list of dictionaries and
    returned as a JSON response.

    :returns: A JSON response containing a list of expense records, where each record
        is represented as a dictionary.
    :rtype: flask.Response
    """
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
                (description, float(amount), normalize_date(date), category)
            )
            count += 1
        
        conn.commit()
        conn.close()
        return jsonify({'message': f'Successfully imported {count} expenses'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/expenses/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    conn = get_db()
    conn.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Expense deleted'}), 200


@app.route('/api/expenses/<int:expense_id>', methods=['PATCH'])
def update_expense(expense_id):
    data = request.get_json()
    conn = get_db()
    conn.execute('UPDATE expenses SET excluded = ? WHERE id = ?', (data.get('excluded', 0), expense_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Expense updated'}), 200


@app.route('/api/expenses/summary', methods=['GET'])
def get_summary():
    conn = get_db()
    summary = conn.execute('''
        SELECT category, SUM(amount) as total
        FROM expenses
        WHERE excluded = 0
        GROUP BY category
        ORDER BY total DESC
    ''').fetchall()
    conn.close()
    return jsonify([{'category': row['category'], 'total': row['total']} for row in summary])

def _compute_period_range(period, offset):
    """Compute date range and gap-fill dates for a given period and offset.

    Returns (start_of_week_or_None, ref_year, ref_month, start_date, end_date, all_dates, is_year).
    """
    now = datetime.now()
    start_of_week = None

    if period == 'week':
        start_of_week = now - timedelta(days=now.weekday()) + timedelta(weeks=offset)
        start_date = start_of_week.strftime('%Y-%m-%d')
        end_date = (start_of_week + timedelta(days=6)).strftime('%Y-%m-%d')
        all_dates = [(start_of_week + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
        return start_of_week, now.year, now.month, start_date, end_date, all_dates, False

    elif period == 'month':
        # Shift month by offset
        total_months = now.year * 12 + (now.month - 1) + offset
        year = total_months // 12
        month = total_months % 12 + 1
        start_date = f'{year}-{month:02d}-01'
        if month == 12:
            end_date = f'{year + 1}-01-01'
        else:
            end_date = f'{year}-{month + 1:02d}-01'
        days_in_month = calendar.monthrange(year, month)[1]
        all_dates = [f'{year}-{month:02d}-{day:02d}' for day in range(1, days_in_month + 1)]
        return None, year, month, start_date, end_date, all_dates, False

    else:  # year
        year = now.year + offset
        start_date = f'{year}-01-01'
        end_date = f'{year + 1}-01-01'
        all_dates = [f'{year}-{m:02d}' for m in range(1, 13)]
        return None, year, None, start_date, end_date, all_dates, True


@app.route('/api/expenses/timeseries', methods=['GET'])
def get_timeseries():
    period = request.args.get('period', 'month')
    if period not in ('week', 'month', 'year'):
        return jsonify({'error': 'Invalid period. Must be week, month, or year'}), 400

    try:
        offset = int(request.args.get('offset', 0))
    except (ValueError, TypeError):
        offset = 0

    start_of_week, ref_year, ref_month, start_date, end_date, all_dates, is_year = _compute_period_range(period, offset)

    conn = get_db()

    if is_year:
        rows = conn.execute('''
            SELECT substr(date, 1, 7) as month, SUM(amount) as total
            FROM expenses
            WHERE date >= ? AND date < ? AND excluded = 0
            GROUP BY substr(date, 1, 7)
            ORDER BY month ASC
        ''', (start_date, end_date)).fetchall()
    elif period == 'week':
        rows = conn.execute('''
            SELECT date, SUM(amount) as total
            FROM expenses
            WHERE date >= ? AND date <= ? AND excluded = 0
            GROUP BY date
            ORDER BY date ASC
        ''', (start_date, end_date)).fetchall()
    else:  # month
        rows = conn.execute('''
            SELECT date, SUM(amount) as total
            FROM expenses
            WHERE date >= ? AND date < ? AND excluded = 0
            GROUP BY date
            ORDER BY date ASC
        ''', (start_date, end_date)).fetchall()

    conn.close()

    if is_year:
        data_map = {row['month']: row['total'] for row in rows}
    else:
        data_map = {row['date']: row['total'] for row in rows}

    result = [{'date': d, 'total': data_map.get(d, 0)} for d in all_dates]

    return jsonify(result)


@app.route('/api/expenses/periods', methods=['GET'])
def get_available_periods():
    """
    Retrieves the availability of expense data for specified time periods. The endpoint
    calculates whether any expenses exist for the current or offset week, month, or year
    based on query parameters. The result is returned as a JSON object indicating the
    availability of expense data for each period.

    :raises ValueError: If the value of the offset query parameter cannot be cast to an integer.
    :raises TypeError: If the offset query parameter is not provided or is invalid.

    :return: A JSON object with available periods as keys (`week`, `month`, `year`) and
        boolean values indicating whether data exists for each period.
    :rtype: flask.Response
    """
    try:
        offset = int(request.args.get('offset', 0))
    except (ValueError, TypeError):
        offset = 0

    conn = get_db()
    result = {}

    for period in ('week', 'month', 'year'):
        _, _, _, start_date, end_date, _, is_year = _compute_period_range(period, offset)
        if period == 'week':
            count = conn.execute(
                'SELECT COUNT(*) as cnt FROM expenses WHERE date >= ? AND date <= ?',
                (start_date, end_date)
            ).fetchone()['cnt']
        else:
            count = conn.execute(
                'SELECT COUNT(*) as cnt FROM expenses WHERE date >= ? AND date < ?',
                (start_date, end_date)
            ).fetchone()['cnt']
        result[period] = count > 0

    conn.close()
    return jsonify(result)


@app.route('/api/expenses/period-label', methods=['GET'])
def get_period_label():
    pass
    """Return a human-readable label for a given period and offset."""
    period = request.args.get('period', 'month')
    if period not in ('week', 'month', 'year'):
        return jsonify({'error': 'Invalid period'}), 400

    try:
        offset = int(request.args.get('offset', 0))
    except (ValueError, TypeError):
        offset = 0

    now = datetime.now()

    if period == 'week':
        start_of_week = now - timedelta(days=now.weekday()) + timedelta(weeks=offset)
        end_of_week = start_of_week + timedelta(days=6)
        start_str = start_of_week.strftime('%b %d')
        end_str = end_of_week.strftime('%b %d, %Y')
        label = f'{start_str} – {end_str}'
    elif period == 'month':
        total_months = now.year * 12 + (now.month - 1) + offset
        year = total_months // 12
        month = total_months % 12 + 1
        label = datetime(year, month, 1).strftime('%B %Y')
    else:  # year
        year = now.year + offset
        label = str(year)

    return jsonify({'label': label})


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8080, debug=True)
