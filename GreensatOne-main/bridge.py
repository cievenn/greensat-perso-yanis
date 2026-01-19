import serial
import json
import os
import time
from datetime import datetime

# --- CONFIGURATION ---
PORT_USB = 'COM5'   # Vérifie ton port !
BAUDRATE = 115200

# Fichier JSON pour le site web
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(BASE_DIR, "data.json")

# Codes couleurs pour la console (fonctionne sur Windows 10+ et Mac/Linux)
C_RESET  = "\033[0m"
C_PINK   = "\033[95m"
C_CYAN   = "\033[96m"
C_GREEN  = "\033[92m"
C_YELLOW = "\033[93m"
C_RED    = "\033[91m"
C_BOLD   = "\033[1m"

def clear_screen():
    # Efface l'écran proprement
    os.system('cls' if os.name == 'nt' else 'clear')

def draw_kawaii_dashboard(data):
    clear_screen()
    t = data.get('temp', 0)
    h = data.get('hum', 0)
    g = data.get('gaz_pct', 0)
    l = data.get('lux', 0)
    p = data.get('press', 0)
    
    # Choix de la mascotte selon la température
    mascot = "( ^_^) "
    mood = "Happy"
    if t > 30: 
        mascot = "( 🥵 )"
        mood = "Chaud!"
    elif g > 20: 
        mascot = "( 🤢 )"
        mood = "Beurk!"
    elif l < 10: 
        mascot = "( 😴 )"
        mood = "Dodo "

    print(f"{C_PINK}╔══════════════════════════════════════════╗{C_RESET}")
    print(f"{C_PINK}║        🌸 GREENSAT KAWAII TERM 🌸        ║{C_RESET}")
    print(f"{C_PINK}╠══════════════════════════════════════════╣{C_RESET}")
    print(f"{C_PINK}║{C_RESET}  Mascotte: {C_BOLD}{mascot}{C_RESET}    Humeur: {mood}   {C_PINK}║{C_RESET}")
    print(f"{C_PINK}╠══════════════════════════════════════════╣{C_RESET}")
    
    # TEMPÉRATURE
    print(f"{C_PINK}║{C_RESET} {C_RED}🌡️  TEMP  {C_RESET} : {C_BOLD}{t:>5} °C{C_RESET}                    {C_PINK}║{C_RESET}")
    bar_t = "█" * int(t/2)
    print(f"{C_PINK}║{C_RESET}    [{C_RED}{bar_t:<20}{C_RESET}]             {C_PINK}║{C_RESET}")

    # HUMIDITÉ
    print(f"{C_PINK}║{C_RESET} {C_CYAN}💧  HUM   {C_RESET} : {C_BOLD}{h:>5} % {C_RESET}                    {C_PINK}║{C_RESET}")
    bar_h = "█" * int(h/5)
    print(f"{C_PINK}║{C_RESET}    [{C_CYAN}{bar_h:<20}{C_RESET}]             {C_PINK}║{C_RESET}")

    # GAZ
    print(f"{C_PINK}║{C_RESET} {C_GREEN}🍃  GAZ   {C_RESET} : {C_BOLD}{g:>5} % {C_RESET}                    {C_PINK}║{C_RESET}")
    color_g = C_GREEN if g < 20 else C_RED
    bar_g = "█" * int(g/2) if g < 40 else "█"*20
    print(f"{C_PINK}║{C_RESET}    [{color_g}{bar_g:<20}{C_RESET}]             {C_PINK}║{C_RESET}")

    # LUMIÈRE & PRESSION
    print(f"{C_PINK}╠══════════════════════════════════════════╣{C_RESET}")
    print(f"{C_PINK}║{C_RESET} {C_YELLOW}☀️  LUM   {C_RESET} : {C_BOLD}{l:>6} Lx{C_RESET}                   {C_PINK}║{C_RESET}")
    print(f"{C_PINK}║{C_RESET} {C_CYAN}☁️  PRES  {C_RESET} : {C_BOLD}{p:>6} hPa{C_RESET}                  {C_PINK}║{C_RESET}")
    print(f"{C_PINK}╚══════════════════════════════════════════╝{C_RESET}")
    print(f"\n{C_BOLD}>> Données sauvegardées pour le site !{C_RESET}")
    print(f">> Dernière synchro: {datetime.now().strftime('%H:%M:%S')}")

# --- PROGRAMME PRINCIPAL ---
try:
    clear_screen()
    print(f"{C_PINK}🌸 Démarrage du Bridge Kawaii...{C_RESET}")
    print(f"🔌 Connexion au Pico sur {PORT_USB}...")
    ser = serial.Serial(PORT_USB, BAUDRATE, timeout=1)
    
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            try:
                if line.startswith('{'):
                    data = json.loads(line)
                    if "error" not in data:
                        # 1. Sauvegarde pour le site
                        data["date_time"] = datetime.now().strftime("%H:%M:%S")
                        with open(JSON_FILE, 'w') as f:
                            json.dump(data, f)
                        
                        # 2. Affichage Kawaii dans la console
                        draw_kawaii_dashboard(data)
                        
            except Exception as e:
                pass # On ignore les erreurs de lecture pour ne pas casser l'affichage
                
except KeyboardInterrupt:
    print(f"\n{C_RED}👋 Bye Bye !{C_RESET}")
except Exception as e:
    print(f"{C_RED}❌ Erreur : {e}{C_RESET}")
    print("Vérifie que Thonny est bien fermé !")