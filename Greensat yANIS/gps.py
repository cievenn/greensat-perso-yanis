from machine import UART, Pin
import time

# Initialisation UART GPS
gps = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))

def convert(coord, direction):
    if coord == "":
        return None
    deg = float(coord[:2])
    minutes = float(coord[2:])
    dec = deg + minutes / 60
    if direction in ["S", "W"]:
        dec = -dec
    return dec

def parse_gps(line):
    parts = line.split(",")

    if parts[0] == "$GPGGA" and parts[6] != "0":
        lat = convert(parts[2], parts[3])
        lon = convert(parts[4], parts[5])
        alt = parts[9]

        return lat, lon, alt
    return None

print("GPS en cours de recherche satellites...")

while True:
    if gps.any():
        line = gps.readline()
        print(line)
        try:
            line = line.decode("utf-8")
            data = parse_gps(line)

            if data:
                lat, lon, alt = data
                print("Latitude :", lat)
                print("Longitude:", lon)
                print("Altitude :", alt, "m")
                print("--------------------")
        except:
            pass

    time.sleep(0.2)
