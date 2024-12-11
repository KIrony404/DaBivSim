import os
import paho.mqtt.client as mqtt
import random
import json
import time
import threading
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Test für Schreibrechte im aktuellen Pfad
try:
    with open("test_write.txt", "w") as f:
        f.write("test")
    os.remove("test_write.txt")
    print("Write test passed.")
except IOError:
    print("Write test failed.")
    exit()  # Beende das Programm, falls Schreibrechte fehlen


# Sicherstellen, dass die Datendatei lokal angelegt und initialisiert ist
if not os.path.exists("temperature_data.csv"):
    with open("temperature_data.csv", "w") as f:
        f.write("Timestamp,Temperature,Humidity\n")

def publisher():
    # Verbindungsparameter für den Test-Broker
    broker_address = "test.mosquitto.org"
    port = 1883
    topic = "home/sensor/temperature"
    
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Publisher connected successfully to broker")
            client.connected_flag = True
        else:
            print(f"Connection failed with code {rc}")

    def on_publish(client, userdata, mid):
        print("Message published")

    # MQTT-Client initialisieren
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_publish = on_publish

    # Verbindung herstellen
    print("Publisher connecting to broker...")
    client.connect(broker_address, port, 60)

    # Loop starten
    client.loop_start()

    # Warten bis die Verbindung hergestellt ist
    client.connected_flag = False
    while not client.connected_flag:
        print("Waiting for connection...")
        time.sleep(1)

    # Dummy-Daten generieren und senden
    for _ in range(50):
        temperature = random.uniform(20.0, 30.0)
        humidity = random.uniform(30.0, 70.0)
        payload = json.dumps({"temperature": temperature, "humidity": humidity})
        result = client.publish(topic, payload)
        result.wait_for_publish()
        print(f"Published: {payload}")
        time.sleep(1)

    # Loop stoppen und Verbindung trennen
    client.loop_stop()
    client.disconnect()

import psycopg2

# Datenbankverbindungsdetails
DB_HOST = "10.154.4.40" # Ersetzen durch Ihre Datenbankadresse
DB_PORT = "8082"
DB_NAME = "sudhaus_db"
DB_USER = "postgres"
DB_PASSWORD = "postgres"

def save_to_database(timestamp, temperature, humidity):
    try:
        # Verbindung zur Datenbank herstellen
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cur = conn.cursor()

        # SQL-Befehl zum Einfügen der Daten
        insert_query = """
        INSERT INTO sensor_data (timestamp, temperature, humidity)
        VALUES (%s, %s, %s)
        """
        cur.execute(insert_query, (timestamp, temperature, humidity))
        
        # Änderungen übernehmen und Verbindung schließen
        conn.commit()
        cur.close()
        conn.close()
        print(f"Data saved to database: {timestamp}, {temperature}, {humidity}")
    except Exception as e:
        print(f"Error saving to database: {e}")

def subscriber():
    # Verbindungsparameter für den Test-Broker
    broker_address = "test.mosquitto.org"
    port = 1883
    topic = "home/sensor/temperature"
    
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Subscriber connected successfully to broker")
            client.subscribe(topic)
        else:
            print(f"Connection failed with code {rc}")

    def on_message(client, userdata, message):
        try:
            payload = message.payload.decode()  # Nachricht dekodieren
            print(f"Received raw message: {payload}")
            data = json.loads(payload)  # JSON parsen

            # Überprüfen, ob die notwendigen Schlüssel vorhanden sind
            if isinstance(data, dict) and "temperature" in data and "humidity" in data:
                print(f"Processed message: Temperature = {data['temperature']}, Humidity = {data['humidity']}")

                # Lokalen Zeitstempel in lesbarem Format erstellen
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Daten in eine CSV-Datei speichern
                with open("temperature_data.csv", "a") as f:
                    f.write(f"{timestamp},{data['temperature']},{data['humidity']}\n")
                # Daten in die PostgreSQL-Datenbank speichern
                save_to_database(timestamp, data['temperature'], data['humidity'])
            else:
                print("Received message is not in the expected format (missing 'temperature' or 'humidity').")
        except json.JSONDecodeError:
            print("Error decoding JSON from message.")
        except Exception as e:
            print(f"Error processing message: {e}")

    # MQTT-Client initialisieren
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    # Verbindung herstellen
    print("Subscriber connecting to broker...")
    client.connect(broker_address, port, 60)

    # Loop starten
    client.loop_start()

    # Warten für Nachrichtenempfang (120 Sekunden)
    time.sleep(120)

    # Loop stoppen und Verbindung trennen
    client.loop_stop()
    client.disconnect()


# Threads erstellen
subscriber_thread = threading.Thread(target=subscriber)
publisher_thread = threading.Thread(target=publisher)

# Threads starten
subscriber_thread.start()
time.sleep(1)  # Kurze Verzögerung, um sicherzustellen, dass der Subscriber zuerst verbunden ist
publisher_thread.start()

# Threads beenden lassen
subscriber_thread.join()
publisher_thread.join()

print("Threads beendet.")



# Datenbankverbindungsdetails
DB_HOST = "10.154.4.40" # Ersetzen durch Ihre Datenbankadresse
DB_PORT = "8082"
DB_NAME = "sudhaus_db"
DB_USER = "postgres"
DB_PASSWORD = "postgres"


def fetch_data_from_database():
    try:
        # Verbindung zur Datenbank herstellen
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        # SQL-Befehl zum Abrufen der Daten
        query = "SELECT timestamp, temperature, humidity FROM sensor_data ORDER BY timestamp ASC;"
        # Daten in ein Pandas-DataFrame laden
        data = pd.read_sql_query(query, conn)

        # Verbindung schließen
        conn.close()
        return data
    except Exception as e:
        print(f"Error fetching data from database: {e}")
        return pd.DataFrame()  # Leeres DataFrame bei Fehler

# Daten aus der Datenbank abrufen
data = fetch_data_from_database()

# Überprüfen, ob Daten geladen wurden
if not data.empty:
    # Zeitstempel in Pandas-Format konvertieren
    data['timestamp'] = pd.to_datetime(data['timestamp'])

    # Temperatur visualisieren
    plt.figure(figsize=(10, 5))
    plt.plot(data['timestamp'], data['temperature'], marker='o', label="Temperature (°C)")
    plt.xlabel("Timestamp")
    plt.ylabel("Temperature (°C)")
    plt.title("Temperature Data from Database")
    plt.grid(True)
    plt.legend()
    plt.show()

    # Luftfeuchtigkeit visualisieren
    plt.figure(figsize=(10, 5))
    plt.plot(data['timestamp'], data['humidity'], marker='o', color="orange", label="Humidity (%)")
    plt.xlabel("Timestamp")
    plt.ylabel("Humidity (%)")
    plt.title("Humidity Data from Database")
    plt.grid(True)
    plt.legend()
    plt.show()
else:
    print("No data found in the database.")