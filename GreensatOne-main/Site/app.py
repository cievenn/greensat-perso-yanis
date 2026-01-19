from flask import Flask, render_template, jsonify
import json
import os

app = Flask(__name__)

# Chemin vers data.json
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(BASE_DIR, 'data.json')

def get_latest_data():
    try:
        if not os.path.exists(JSON_PATH):
            return None
        with open(JSON_PATH, 'r') as f:
            return json.load(f)
    except:
        return None

# Route pour la page principale (le joli design)
@app.route('/')
def index():
    return render_template('index.html')

# NOUVEAU : Route "API" pour que le Javascript récupère les chiffres discrètement
@app.route('/api/data')
def api_data():
    data = get_latest_data()
    if data:
        return jsonify(data) # Renvoie du JSON pur au site
    else:
        return jsonify({"error": "No data"}), 404

if __name__ == '__main__':
    print("🌸 SITE KAWAII LANCÉ ! http://127.0.0.1:5000")
    app.run(debug=True, port=5000, use_reloader=False)