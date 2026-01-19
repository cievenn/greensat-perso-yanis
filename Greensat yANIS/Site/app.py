from flask import Flask, render_template, jsonify, request
import sqlite3
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'greensat.db')

def get_db_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except:
        return None

@app.route('/')
def index():
    return render_template('index.html')

# API TEMPS RÉEL
@app.route('/api/data')
def api_data():
    try:
        conn = get_db_connection()
        row = conn.execute('SELECT * FROM mesures ORDER BY date_time DESC LIMIT 1').fetchone()
        conn.close()
        return jsonify(dict(row)) if row else (jsonify({"error": "Empty"}), 404)
    except:
        return jsonify({"error": "DB Error"}), 500

# API HISTORIQUE
@app.route('/api/history')
def api_history():
    try:
        start_date = request.args.get('start')
        end_date = request.args.get('end')
        
        conn = get_db_connection()
        if start_date and end_date:
            query = "SELECT * FROM mesures WHERE date_time BETWEEN ? AND ? ORDER BY date_time ASC"
            rows = conn.execute(query, (start_date, end_date)).fetchall()
        else:
            # Fallback (si pas de date)
            query = "SELECT * FROM (SELECT * FROM mesures ORDER BY date_time DESC LIMIT 100) ORDER BY date_time ASC"
            rows = conn.execute(query).fetchall()
            
        conn.close()
        return jsonify([dict(row) for row in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- NOUVEAU : API LIMITES (Pour savoir quand cacher les flèches) ---
@app.route('/api/limits')
def api_limits():
    try:
        conn = get_db_connection()
        # On cherche la date la plus ancienne (min) et la plus récente (max)
        row = conn.execute('SELECT MIN(date_time) as first_date, MAX(date_time) as last_date FROM mesures').fetchone()
        conn.close()
        return jsonify(dict(row))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Serveur lancé sur http://127.0.0.1:5000")
    app.run(debug=True, port=5000)