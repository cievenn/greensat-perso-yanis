from machine import Pin, ADC, I2C
import dht
import time
import struct

class GasSensor:
    def __init__(self, pin_adc):
        self.sensor = ADC(Pin(pin_adc))
        self.baseline = 0
    def calibrer(self):
        print("Calibrage Gaz...")
        total = 0
        for _ in range(20):
            total += self.sensor.read_u16()
            time.sleep(0.1)
        self.baseline = total / 20
    def read(self):
        val = self.sensor.read_u16()
        diff = val - self.baseline
        if diff < 0: diff = 0
        pct = (diff / 10000) * 100
        if pct > 100: pct = 100
        return val, pct

class TempHumSensor:
    def __init__(self, pin_data):
        self.sensor = dht.DHT11(Pin(pin_data))
    def read(self):
        try:
            self.sensor.measure()
            return self.sensor.temperature(), self.sensor.humidity()
        except OSError:
            return None, None

class LightSensor:
    def __init__(self, i2c_bus, addr=0x23):
        self.i2c = i2c_bus
        self.addr = addr
        try:
            self.i2c.writeto(self.addr, b'\x01')
        except:
            pass
    def read(self):
        try:
            self.i2c.writeto(self.addr, b'\x10')
            time.sleep(0.2)
            data = self.i2c.readfrom(self.addr, 2)
            lux = ((data[0] << 8) | data[1]) / 1.2
            return round(lux, 1)
        except:
            return -1

class PressureSensor:
    """Gère le BMP280 (Pression) avec pilote intégré"""
    def __init__(self, i2c_bus, addr=0x76):
        self.i2c = i2c_bus
        self.addr = addr
        self.t_fine = 0
        try:
            # Configuration du capteur
            self.calib = self.read_calibration()
            self.i2c.writeto_mem(self.addr, 0xF4, b'\x27') # Mode normal
            self.i2c.writeto_mem(self.addr, 0xF5, b'\xA0') # Standby 1000ms
        except:
            print("Erreur BMP280: Vérifier adresse (0x76 ou 0x77)")

    def read_calibration(self):
        # Lecture des constantes de calibration (nécessaire pour le calcul)
        c = self.i2c.readfrom_mem(self.addr, 0x88, 24)
        return struct.unpack('<HhhHhhhhhhhh', c)

    def read(self):
        try:
            # Lecture des données brutes
            data = self.i2c.readfrom_mem(self.addr, 0xF7, 6)
            pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
            temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
            
            # Compensation Température
            var1 = (temp_raw / 16384.0 - self.calib[0] / 1024.0) * self.calib[1]
            var2 = ((temp_raw / 131072.0 - self.calib[0] / 8192.0) ** 2) * self.calib[2]
            self.t_fine = var1 + var2
            
            # Compensation Pression
            var1 = (self.t_fine / 2.0) - 64000.0
            var2 = var1 * var1 * self.calib[5] / 32768.0
            var2 = var2 + var1 * self.calib[4] * 2.0
            var2 = (var2 / 4.0) + (self.calib[3] * 65536.0)
            var1 = (self.calib[2] * var1 * var1 / 524288.0 + self.calib[1] * var1) / 524288.0
            var1 = (1.0 + var1 / 32768.0) * self.calib[0]
            if var1 == 0: return 0
            p = 1048576.0 - pres_raw
            p = (p - (var2 / 4096.0)) * 6250.0 / var1
            var1 = self.calib[8] * p * p / 2147483648.0
            var2 = p * self.calib[7] / 32768.0
            p = p + (var1 + var2 + self.calib[6]) / 16.0
            
            return round(p / 100, 1) # Retourne en hPa
        except:
            return -1

class Alarm:
    def __init__(self, pin_buzzer):
        self.buzzer = Pin(pin_buzzer, Pin.OUT)
        self.buzzer.value(0)
    def beep(self, duration=0.1):
        self.buzzer.value(1)
        time.sleep(duration)
        self.buzzer.value(0)
    def alert(self):
        for _ in range(3):
            self.beep(0.1)
            time.sleep(0.1)

class GreenSatLogger:
    def __init__(self):
        self.start_time = time.time()
    def save(self, gaz, temp, hum, lux, press):
        return time.time() - self.start_time