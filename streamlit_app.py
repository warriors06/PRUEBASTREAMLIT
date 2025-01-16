import paho.mqtt.client as mqtt
import streamlit as st
import json

# Configuración de MQTT para TTN
MQTT_BROKER = "nam1.cloud.thethings.network"  # Cambia según tu región
MQTT_PORT = 8883  # Usando conexión TLS
MQTT_TOPIC = "v3/your-application-id@your-tenant-id/devices/+/up"  # Tópico para todos los nodos
MQTT_USER = "mediciondeparticulas@ttn"  # Tu ID de aplicación
MQTT_PASSWORD = "NNSXS.2DRR43EO3UVIOH5HM4TKT3NXVCK4BQWNDPQHIXQ.IINYNHMOMIJ6IS7Z5MZL6LTBSHS3YEESYL3DPO46NOBYI7NADV2A"  # Tu API Key generada en TTN Console

# Inicializar Streamlit
st.title("Datos de Todos los Nodos desde TTN")

# Inicializar el estado de la sesión
if "sensor_data" not in st.session_state:
    st.session_state.sensor_data = []

# Función callback para manejar mensajes MQTT
def on_message(client, userdata, message):
    try:
        # Decodificar el payload recibido
        data = json.loads(message.payload.decode())

        # Extraer datos relevantes
        if "uplink_message" in data:
            decoded_payload = data["uplink_message"]["decoded_payload"]
            device_id = data["end_device_ids"]["device_id"]
            received_at = data["received_at"]

            # Almacenar todos los datos del nodo
            sensor_data = {
                "device_id": device_id,
                "received_at": received_at,
                "raw_payload": decoded_payload,  # Datos completos del payload decodificado
            }

            # Guardar los datos en la sesión
            st.session_state.sensor_data.append(sensor_data)

            # Actualizar la página
            st.experimental_rerun()
    except Exception as e:
        st.error(f"Error procesando mensaje: {e}")

# Configurar cliente MQTT
client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
client.tls_set()  # Usar TLS para seguridad
client.on_message = on_message

# Conectar y suscribirse al tópico MQTT
try:
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.subscribe(MQTT_TOPIC)
    client.loop_start()
except Exception as e:
    st.error(f"Error conectándose al broker MQTT: {e}")

# Mostrar datos en la interfaz
st.subheader("Datos Recibidos de Todos los Nodos")
if st.session_state.sensor_data:
    for data in st.session_state.sensor_data:
        st.write(f"**Dispositivo:** {data['device_id']}")
        st.write(f"**Hora de Recepción:** {data['received_at']}")
        st.json(data["raw_payload"])  # Mostrar el payload completo
else:
    st.write("Esperando datos...")
