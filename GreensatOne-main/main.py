import time
from machine import Pin, I2C
from sensors import GasSensor, TempHumSensor, LightSensor, PressureSensor, GreenSatLogger, Alarm
import json 

# --- PINS (Inchangés) ---
PIN_DHT_POWER = 14
PIN_DHT_DATA  = 15
PIN_BUZZER    = 16
PIN_GAZ       = 26
PIN_BMP_POWER = 4
PIN_SDA_BMP   = 2
PIN_SCL_BMP   = 3
PIN_SDA_LUX   = 0
PIN_SCL_LUX   = 1

# --- ALIMENTATIONS ---
p1 = Pin(PIN_DHT_POWER, Pin.OUT)
p1.value(1)
p2 = Pin(PIN_BMP_POWER, Pin.OUT)
p2.value(1)
time.sleep(2) # Réveil des capteurs

# --- SETUP ---
buzzer = Alarm(PIN_BUZZER)
buzzer.beep(0.1)

# I2C
i2c_lux = I2C(0, scl=Pin(PIN_SCL_LUX), sda=Pin(PIN_SDA_LUX), freq=400000)
i2c_pres = I2C(1, scl=Pin(PIN_SCL_BMP), sda=Pin(PIN_SDA_BMP), freq=400000)

# Objets Capteurs
mq2 = GasSensor(PIN_GAZ)
dht11 = TempHumSensor(PIN_DHT_DATA)
lux_sensor = LightSensor(i2c_lux)
bmp280 = PressureSensor(i2c_pres)

print("💖 Calibrage des capteurs en cours... (Patience)")
mq2.calibrer()

print("\n" + "="*30)
print("🌸  GREENSAT PICO SYSTEM  🌸")
print("="*30 + "\n")

while True:
    try:
        # 1. LECTURES
        raw_gaz, pct_gaz = mq2.read()
        temp, hum = dht11.read()
        lux = lux_sensor.read()
        press = bmp280.read()
        
        # 2. PRÉPARATION DES DONNÉES
        data = {
            "gaz_pct": round(pct_gaz, 2),
            "temp": temp if temp is not None else 0,
            "hum": hum if hum is not None else 0,
            "lux": lux if lux != -1 else 0,
            "press": press if press != -1 else 0
        }

        # 3. AFFICHAGE KAWAII (Pour tes yeux dans Thonny) 🌸
        # On choisit une émoticône selon la situation
        mood = "(^･o･^)ﾉ"  # Chat coucou
        statut = "Tout va bien !"
        
        if data['gaz_pct'] > 20:
            mood = "(>﹏<)"  # Panique
            statut = "ATTENTION GAZ !"
        elif data['temp'] > 30:
            mood = "(🥵)"    # Chaud
            statut = "Trop chaud !"
        
        print(f"\n✨ {mood} {statut}")
        print(f"   ├─ 🌡️  Temp : {data['temp']}°C")
        print(f"   ├─ 💧  Hum  : {data['hum']}%")
        print(f"   ├─ 🍃  Gaz  : {data['gaz_pct']}%")
        print(f"   ├─ ☀️  Lux  : {data['lux']}")
        print(f"   └─ ☁️  Pres : {data['press']} hPa")
        
        # 4. ENVOI DISCRET (Pour le site web) 🤫
        # C'est cette ligne que le bridge.py va lire !
        print(json.dumps(data))

        # 5. SÉCURITÉ
        if pct_gaz > 30: buzzer.alert()
        elif temp is not None and temp > 35: buzzer.beep(0.5)

    except Exception as e:
        print(f"❌ Oupsie : {e}")

    time.sleep(2)