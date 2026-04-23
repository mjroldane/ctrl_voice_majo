import streamlit as st
import os
import json
import paho.mqtt.client as paho
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Control de Voz", layout="wide")

# --- CSS: MODO OSCURO (DARK MODE) ---
st.markdown("""
    <style>
    /* Fondo de la app en gris muy oscuro */
    .stApp {
        background-color: #121212;
        color: #e0e0e0;
    }

    /* Títulos en blanco para asegurar visibilidad */
    .main-title { color: #ffffff !important; }
    .sub-title { color: #b0b0b0 !important; }

    /* Tarjetas oscuras */
    .flat-card {
        background-color: #1e1e1e;
        border-radius: 10px;
        border: 1px solid #333333;
        padding: 20px;
        margin-bottom: 15px;
        color: #e0e0e0;
    }

    /* Texto de cabecera en las tarjetas */
    .card-header {
        color: #ffffff;
        font-weight: 600;
        font-size: 1.1em;
        margin-bottom: 10px;
    }

    /* Botón verde que resalta en fondo oscuro */
    .bk-btn {
        background-color: #28a745 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        border: none !important;
    }
    
    /* Asegurar que el texto normal se lea bien */
    div { color: #e0e0e0; }
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA MQTT ---
broker = "broker.mqttdashboard.com"
port = 1883
topic = "voice_ctrl"
client_id = "oiceClienteMajoRol"

if "client" not in st.session_state:
    st.session_state.client = paho.Client(client_id)
    try:
        st.session_state.client.connect(broker, port)
    except:
        st.error("Error conectando al broker")

# --- CABECERA ---
st.markdown('<h1 class="main-title">Interfaces Multimodales</h1>', unsafe_allow_html=True)
st.markdown('<h3 class="sub-title">Control de Voz Compacto</h3>', unsafe_allow_html=True)

# --- CUERPO ---
col_ctrl, col_msg = st.columns([1, 1.2], gap="medium")

with col_ctrl:
    st.markdown('<div class="flat-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-header">Panel de Acción</div>', unsafe_allow_html=True)
    
    try:
        image = Image.open('persona hablando.jpg')
        st.image(image, width=120)
    except:
        st.info("Imagen 'persona hablando.jpg' no encontrada.")

    st.write("Pulsa 'Inicio' y habla.")
    
    stt_button = Button(label="Inicio", width=130)
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
        stt_button, events="GET_TEXT", key="listen", 
        refresh_on_update=False, override_height=65, debounce_time=0)
    
    st.markdown('</div>', unsafe_allow_html=True)

with col_msg:
    st.markdown('<div class="flat-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-header">Estado y Respuestas</div>', unsafe_allow_html=True)
    
    st.markdown("🟢 **MQTT:** `broker.mqttdashboard.com`")
    
    log_area = st.empty()
    log_area.info("Último Comando: [Esperando entrada...]")
    
    if result and "GET_TEXT" in result:
        comando = result.get("GET_TEXT")
        log_area.success(f"**Detectado:** {comando}")
        
        mensaje_json = json.dumps({"Act1": comando.strip()})
        st.session_state.client.publish(topic, mensaje_json)
        st.write(f"📤 Enviado a: `{topic}`")

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.caption(f"Status: Connected | Client: {client_id}")
