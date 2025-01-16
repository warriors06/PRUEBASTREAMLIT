import paho.mqtt.client as mqtt
import streamlit as st
import json
import os
from time import sleep

# MQTT settings
MQTT_BROKER = "localhost"  # Node-RED está en local
MQTT_PORT = 1883          # Puerto estándar MQTT
MQTT_TOPIC = "sensor/data"  # El mismo topic que configuramos en Node-RED

# Inicializar el estado de la sesión si no existe
if 'sensor_data' not in st.session_state:
    st.session_state.sensor_data = {
        'temperature': 0,
        'humidity': 0,
        'pm2_5': 0,
        'pm10': 0,
        'devaddr': ''
    }

# Streamlit app
st.title("Sensor Data Display")

# Crear contenedores para las métricas
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

# Callback function when a message is received
def on_message(client, userdata, message):
    try:
        # Decodificar el mensaje JSON
        data = json.loads(message.payload.decode())
        
        # Actualizar los valores usando los datos decodificados
        if 'decodedValues' in data:
            decoded = data['decodedValues']
            st.session_state.sensor_data.update({
                'temperature': decoded['temperature'],
                'humidity': decoded['humidity'],
                'pm2_5': decoded['pm2_5'],
                'pm10': decoded['pm10'],
                'devaddr': data['devaddr']
            })
        
        st.experimental_rerun()
    except Exception as e:
        print(f"Error processing message: {e}")

# Create an MQTT client
client = mqtt.Client()
client.on_message = on_message

# Connect to the MQTT broker and subscribe to the topic
try:
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.subscribe(MQTT_TOPIC)
    client.loop_start()
    st.success("Connected to MQTT broker!")
except Exception as e:
    st.error(f"Error connecting to MQTT broker: {e}")

# Display the metrics
with col1:
    st.metric(
        label="Temperature",
        value=f"{st.session_state.sensor_data['temperature']}°C",
        delta=None
    )

with col2:
    st.metric(
        label="Humidity",
        value=f"{st.session_state.sensor_data['humidity']}%",
        delta=None
    )

with col3:
    st.metric(
        label="PM2.5",
        value=f"{st.session_state.sensor_data['pm2_5']} µg/m³",
        delta=None
    )

with col4:
    st.metric(
        label="PM10",
        value=f"{st.session_state.sensor_data['pm10']} µg/m³",
        delta=None
    )

# Display device address
st.text(f"Device Address: {st.session_state.sensor_data['devaddr']}")
