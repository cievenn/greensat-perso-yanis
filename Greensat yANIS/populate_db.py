import sqlite3
import os
import random
import math
from datetime import datetime, timedelta

# --- CONFIGURATION ---
# On cible la même base de données que les autres fichiers
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'greensat.db')

def populate_database():
    print(f"🔧 Connexion à la base : {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Nettoyage (Optionnel : on vide la table pour avoir des données propres)
    print("🧹 Nettoyage de l'ancienne table...")
    cursor.execute("DROP TABLE IF EXISTS mesures")
    
    # 2. Re-création de la table (Structure identique à setup_db.py)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS mesures (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date_time DATETIME,
        temp REAL,
        hum REAL,
        gaz_pct REAL,
        lux REAL,
        press REAL,
        air_pct REAL
    )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON mesures(date_time)')

    # 3. Génération des données
    print("⏳ Génération de 2 ans d'historique... (Patientez)")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730) # 2 ans
    current_date = start_date
    
    batch_data = [] # On stocke tout ici pour insérer en un coup (beaucoup plus rapide)
    
    # Variables pour la simulation "Météo"
    base_press = 1013.0
    season_offset = 0

    while current_date <= end_date:
        # A. Gestion du Temps
        # Jour de l'année (0-365) pour simuler les saisons
        day_of_year = current_date.timetuple().tm_yday
        hour = current_date.hour + current_date.minute / 60.0
        
        # B. SAISONS (Sinusoïde annuelle : Froid en Hiver, Chaud en Été)
        # Le pic de chaleur est vers le jour 200 (Juillet)
        season_temp = -math.cos((day_of_year - 20) / 365 * 2 * math.pi) * 10 
        
        # C. CYCLE JOUR/NUIT (Sinusoïde journalière)
        # Min à 4h du matin, Max à 16h
        daily_temp = -math.cos(((hour - 4) / 24) * 2 * math.pi) * 5
        
        # Température Finale = Base 15°C + Saison + Jour + Aléatoire
        temp = 15 + season_temp + daily_temp + random.uniform(-2, 2)
        
        # D. LUMIÈRE (Lux)
        if 6 <= hour <= 21: # Soleil levé
            sun_angle = math.sin(((hour - 6) / 15) * math.pi)
            lux = 1000 * sun_angle + random.uniform(-100, 100)
            lux = max(0, lux) # Pas de lumière négative
            # Moins de lumière en hiver
            if season_temp < 0: lux *= 0.6 
        else:
            lux = 0 # Nuit
            
        # E. HUMIDITÉ (Inverse de la température souvent)
        hum = 60 - (daily_temp * 2) + random.uniform(-10, 10)
        hum = max(20, min(100, hum))
        
        # F. PRESSION (Varie lentement jour après jour)
        base_press += random.uniform(-0.5, 0.5)
        base_press = max(980, min(1040, base_press))
        
        # G. GAZ & AIR
        gaz_pct = random.uniform(2, 8)
        # Pics de pollution aléatoires (1 chance sur 100)
        if random.random() > 0.99: gaz_pct += random.uniform(10, 25)
        air_pct = round(100 - gaz_pct, 1)

        # Ajout à la liste
        batch_data.append((
            current_date.strftime("%Y-%m-%d %H:%M:%S"),
            round(temp, 1),
            int(hum),
            round(gaz_pct, 2),
            int(lux),
            round(base_press, 1),
            air_pct
        ))
        
        # On avance d'une heure (Pour 2 ans, 1 point/heure suffit largement et fait ~17k lignes)
        current_date += timedelta(hours=1)

    # 4. Insertion massive (Bulk Insert)
    print(f"💾 Sauvegarde de {len(batch_data)} enregistrements dans la base...")
    cursor.executemany('''
        INSERT INTO mesures (date_time, temp, hum, gaz_pct, lux, press, air_pct)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', batch_data)
    
    conn.commit()
    conn.close()
    print("✅ Terminé ! La base de données contient maintenant 2 ans d'historique.")

if __name__ == '__main__':
    populate_database()