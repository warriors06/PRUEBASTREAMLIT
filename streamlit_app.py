import paho.mqtt.client as mqtt
import streamlit as st
import json
import os
from time import sleep

# MQTT settings - Configuración explícita para localhost
MQTT_BROKER = "127.0.0.1"  # Usando la dirección IP específica en lugar de "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/data"

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
        st.write("Mensaje recibido:", data)  # Debug line
        
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
        st.error(f"Error procesando mensaje: {e}")
        print(f"Error detallado: {e}")

# Create an MQTT client
client = mqtt.Client()
client.on_message = on_message

# Agregar callback para debugging
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        st.success(f"Conectado al broker MQTT en {MQTT_BROKER}:{MQTT_PORT}")
        client.subscribe(MQTT_TOPIC)
    else:
        st.error(f"Error de conexión con código: {rc}")

client.on_connect = on_connect

# Connect to the MQTT broker and subscribe to the topic
try:
    st.info(f"Intentando conectar a MQTT broker en {MQTT_BROKER}:{MQTT_PORT}...")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
except Exception as e:
    st.error(f"Error connecting to MQTT broker: {e}")
    st.write("Detalles de conexión:", {
        "Broker": MQTT_BROKER,
        "Puerto": MQTT_PORT,
        "Topic": MQTT_TOPIC
    })

# Display the metrics
with col1:
    st.metric(
        label="Temperature",
        value=f"{st.session_state.sensor_data['temperature']}°C"
    )

with col2:
    st.metric(
        label="Humidity",
        value=f"{st.session_state.sensor_data['humidity']}%"
    )

with col3:
    st.metric(
        label="PM2.5",
        value=f"{st.session_state.sensor_data['pm2_5']} µg/m³"
    )

with col4:
    st.metric(
        label="PM10",
        value=f"{st.session_state.sensor_data['pm10']} µg/m³"
    )

# Display device address
st.text(f"Device Address: {st.session_state.sensor_data['devaddr']}")
