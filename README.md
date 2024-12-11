# Sensordaten-Dashboard
Zunächst werden benötigte Sensordaten von einem MQTT-Broker, der öffentlich zugänglich ist, abgefragt. 
Je nach Verfügbarkeit: 

    broker_address = "test.mosquitto.org"
    #Alternativer broker: "broker.hivemq.com"
    port = 1883
    topic = "home/sensor/temperature"

Der Subscription-Thread ist für 120s offen und liefert jeweils 50 Messpunkte für Feuchte [%] und Temperatur[°C].

Die Daten werden in einen Postgres-Datenbankserver geschrieben, der on prem an der HSWT gehostet ist. Erreichbarkeit wird übereinen VPN-Tunnel gewährleistet.

Das Dashboard greift die Daten vom Datenbankserver ab und visualisiert sie mittels streamlit app. Eine leichte Erhöhung der Interaktivität wurde durch das Einbetten von plotly-Diagrammen erreicht.
Aufruf der app erfolgt via bash:

> streamlit run url
