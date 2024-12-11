# Installation notwendiger Bibliotheken
# !pip install streamlit pandas psycopg2 matplotlib

import streamlit as st
import pandas as pd
import psycopg2
import matplotlib.pyplot as plt

# Datenbankverbindung
DB_HOST = "10.154.4.40"  # Ersetzen durch Ihre Datenbankadresse
DB_PORT = "8082"  # Portnummer
DB_NAME = "sudhaus_db"  # Name der Datenbank
DB_USER = "postgres"  # Benutzername
DB_PASSWORD = "postgres"  # Passwort

# Funktion zur Datenabfrage aus der Datenbank
def fetch_data():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        query = "SELECT timestamp, temperature, humidity FROM sensor_data ORDER BY timestamp ASC;"
        data = pd.read_sql_query(query, conn)
        conn.close()
        return data
    except Exception as e:
        st.error(f"Fehler beim Abrufen der Daten: {e}")
        return pd.DataFrame()

# Streamlit Layout
st.title("Sensordaten-Dashboard")

# Daten laden
data = fetch_data()

if not data.empty:
    # Zeitstempel konvertieren
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    
    # Filter für Zeitbereich
    st.sidebar.header("Zeitraumfilter")
    start_date = st.sidebar.date_input("Startdatum", value=data['timestamp'].min().date())
    end_date = st.sidebar.date_input("Enddatum", value=data['timestamp'].max().date())
    
    if start_date <= end_date:
        filtered_data = data[(data['timestamp'].dt.date >= start_date) & (data['timestamp'].dt.date <= end_date)]
        
        if not filtered_data.empty:
            # Temperatur-Plot
            st.subheader("Temperaturverlauf")
            st.line_chart(filtered_data[['timestamp', 'temperature']].set_index('timestamp'))
            
            # Feuchtigkeit-Plot
            st.subheader("Feuchtigkeitsverlauf")
            st.line_chart(filtered_data[['timestamp', 'humidity']].set_index('timestamp'))
            
            # Datenanzeige
            st.subheader("Gefilterte Daten")
            st.dataframe(filtered_data)
        else:
            st.warning("Keine Daten im ausgewählten Zeitraum gefunden.")
    else:
        st.error("Das Startdatum muss vor dem Enddatum liegen.")
else:
    st.warning("Keine Daten gefunden.")
