from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import csv
import io
import os
from datetime import datetime

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
    pass
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

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8080, debug=True)
