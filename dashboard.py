import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px

# Datenbankverbindung
DB_HOST = "10.154.4.40"  # Ersetzen durch Ihre Datenbankadresse
DB_PORT = "8082"  # Portnummer
DB_NAME = "sudhaus_db"  # Name der Datenbank
DB_USER = "postgres"  # Benutzername
DB_PASSWORD = "postgres"  # Passwort

# Benutzername und Passwort für die App
APP_USERNAME = "user"
APP_PASSWORD = "password" #xyzfhjklj

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

# Authentifizierungsfunktion
def login():
    st.title("Anmeldung")
    username = st.text_input("Benutzername")
    password = st.text_input("Passwort", type="password")
    if st.button("Anmelden"):
        if username == APP_USERNAME and password == APP_PASSWORD:
            st.session_state["logged_in"] = True
            st.experimental_rerun()
        else:
            st.error("Falscher Benutzername oder Passwort.")

# Hauptanwendung
def main_app():
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
        start_time = st.sidebar.time_input("Startzeit", value=pd.Timestamp("00:00:00").time())
        end_time = st.sidebar.time_input("Endzeit", value=pd.Timestamp("23:59:59").time())
        
        if start_date <= end_date:
            # Zeitbereich erstellen
            start_datetime = pd.Timestamp.combine(start_date, start_time)
            end_datetime = pd.Timestamp.combine(end_date, end_time)
            
            filtered_data = data[(data['timestamp'] >= start_datetime) & (data['timestamp'] <= end_datetime)]
            
            if not filtered_data.empty:
                # Interaktiver Temperatur-Plot mit Plotly
                st.subheader("Temperaturverlauf")
                fig_temp = px.line(filtered_data, x='timestamp', y='temperature', title='Temperaturverlauf', labels={
                    "timestamp": "Zeitstempel",
                    "temperature": "Temperatur (°C)"
                })
                st.plotly_chart(fig_temp, use_container_width=True)
                
                # Interaktiver Feuchtigkeits-Plot mit Plotly
                st.subheader("Feuchtigkeitsverlauf")
                fig_humidity = px.line(filtered_data, x='timestamp', y='humidity', title='Feuchtigkeitsverlauf', labels={
                    "timestamp": "Zeitstempel",
                    "humidity": "Feuchtigkeit (%)"
                })
                st.plotly_chart(fig_humidity, use_container_width=True)
                
                # Datenanzeige
                st.subheader("Gefilterte Daten")
                st.dataframe(filtered_data)
            else:
                st.warning("Keine Daten im ausgewählten Zeitraum gefunden.")
        else:
            st.error("Das Startdatum muss vor dem Enddatum liegen.")
    else:
        st.warning("Keine Daten gefunden.")

# Authentifizierungskontrolle
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
else:
    main_app()
