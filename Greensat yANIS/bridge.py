import serial
import json
import sqlite3
import os
import time
from datetime import datetime

# --- CONFIGURATION ---
PORT_USB = 'COM5'   # Vérifie ton port !
BAUDRATE = 115200
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'greensat.db')

# Couleurs console
C_RESET = "\033[0m"
C_PINK = "\033[95m"
C_CYAN = "\033[96m"
C_GREEN = "\033[92m"
C_BOLD = "\033[1m"

def save_to_db(data):
    """Insère la donnée dans la base SQLite"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # On insère les valeurs
        cursor.execute('''
            INSERT INTO mesures (date_time, temp, hum, gaz_pct, lux, press, air_pct)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['date_time'], 
            data.get('temp', 0), 
            data.get('hum', 0), 
            data.get('gaz_pct', 0), 
            data.get('lux', 0), 
            data.get('press', 0), 
            data.get('air_pct', 0)
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Erreur DB: {e}")
        return False

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# --- PROGRAMME PRINCIPAL ---
print(f"{C_PINK}🌸 Démarrage du Bridge SQL...{C_RESET}")
try:
    ser = serial.Serial(PORT_USB, BAUDRATE, timeout=1)
    
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            try:
                if line.startswith('{'):
                    data = json.loads(line)
                    if "error" not in data:
                        # Ajout date
                        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        data["date_time"] = now
                        
                        # Calcul Air Quality si manquant
                        if "air_pct" not in data:
                            data["air_pct"] = round(100 - data.get("gaz_pct", 0), 1)

                        # Sauvegarde SQL
                        if save_to_db(data):
                            print(f"{C_GREEN}>> [SQL] Donnée enregistrée à {now}{C_RESET}")
                        
            except:
                pass
except Exception as e:
    print(f"Erreur : {e}")