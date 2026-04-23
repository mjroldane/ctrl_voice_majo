import streamlit as st
import os
import json
import time
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import paho.mqtt.client as paho

# --- Configuración Inicial ---
st.set_page_config(page_title="Interfaz Multimodal", layout="centered")

# Crear directorio de trabajo solo una vez
if not os.path.exists("temp"):
    os.makedirs("temp")

# --- Lógica MQTT ---
broker = "broker.mqttdashboard.com"
port = 1883

def on_publish(client, userdata, result):
    print("El dato ha sido publicado")

def setup_client():
    client = paho.Client("GIT-HUBC")
    client.on_publish = on_publish
    return client

# Inicializar sesión
if "client" not in st.session_state:
    st.session_state.client = setup_client()

# --- UI y Ergonomía Cognitiva ---
st.title("Interfaces Multimodales")
st.markdown("---")

col1, col2 = st.columns([1, 2])

with col1:
    try:
        image = Image.open('voice_ctrl.jpg')
        st.image(image, width=150)
    except:
        st.warning("Imagen no encontrada")

with col2:
    st.subheader("Control por Voz")
    st.write("Presiona el botón e interactúa con el sistema. Tu comando será enviado vía MQTT.")

# --- Estilos personalizados para el botón ---
st.markdown("""
    <style>
    .bk-btn {
        background-color: #4CAF50 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Componente de Voz ---
stt_button = Button(label="Iniciar Escucha", width=200)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    
    recognition.onresult = function (e) {
        var value = e.results[0][0].transcript;
        document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
    }
    recognition.start();
    """))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)

# --- Procesamiento de Interacción ---
if result and "GET_TEXT" in result:
    comando = result.get("GET_TEXT")
    
    # Feedback visual claro
    with st.status("Procesando comando...", expanded=True) as status:
        st.write(f"Comando detectado: **{comando}**")
        
        try:
            st.session_state.client.connect(broker, port)
            message = json.dumps({"Act1": comando.strip()})
            st.session_state.client.publish("voice_ctrl", message)
            st.success("Enviado correctamente al broker.")
        except Exception as e:
            st.error(f"Error de conexión: {e}")
        
        status.update(label="Acción completada", state="complete")

# Área de logs/mensajes
st.divider()
st.caption("Estado del sistema: Conectado a broker.mqttdashboard.com")
