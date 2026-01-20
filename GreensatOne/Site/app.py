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

# API HISTORIQUE OPTIMISÉE
@app.route('/api/history')
def api_history():
    try:
        start_date = request.args.get('start')
        end_date = request.args.get('end')
        resolution = request.args.get('resolution', 'raw') # 'raw' ou 'day'
        
        conn = get_db_connection()
        
        # Construction de la requête selon la résolution demandée
        if resolution == 'day':
            # MODE ANNÉE : On fait la moyenne par jour pour ne pas tuer le navigateur
            # On groupe par jour (substr(date_time, 1, 10) extrait YYYY-MM-DD)
            query = '''
            SELECT 
                MIN(date_time) as date_time, 
                AVG(temp) as temp, 
                AVG(hum) as hum, 
                AVG(gaz_pct) as gaz_pct, 
                AVG(lux) as lux, 
                AVG(press) as press,
                AVG(air_pct) as air_pct
            FROM mesures 
            WHERE date_time BETWEEN ? AND ? 
            GROUP BY substr(date_time, 1, 10) 
            ORDER BY date_time ASC
            '''
            rows = conn.execute(query, (start_date, end_date)).fetchall()
            
        elif start_date and end_date:
            # MODE NORMAL : Données brutes
            query = "SELECT * FROM mesures WHERE date_time BETWEEN ? AND ? ORDER BY date_time ASC"
            rows = conn.execute(query, (start_date, end_date)).fetchall()
            
        else:
            # Fallback (Live)
            query = "SELECT * FROM (SELECT * FROM mesures ORDER BY date_time DESC LIMIT 100) ORDER BY date_time ASC"
            rows = conn.execute(query).fetchall()
            
        conn.close()
        
        # Petit hack : pour les moyennes, on arrondit les valeurs flottantes pour le JSON
        results = []
        for row in rows:
            d = dict(row)
            if resolution == 'day':
                # Arrondir les moyennes pour faire propre
                for k in ['temp', 'hum', 'gaz_pct', 'lux', 'press']:
                    if d[k] is not None: d[k] = round(d[k], 1)
            results.append(d)
            
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API LIMITES
@app.route('/api/limits')
def api_limits():
    try:
        conn = get_db_connection()
        row = conn.execute('SELECT MIN(date_time) as first_date, MAX(date_time) as last_date FROM mesures').fetchone()
        conn.close()
        return jsonify(dict(row))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Serveur lancé sur http://127.0.0.1:5000")
    app.run(debug=True, port=5000)