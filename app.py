import streamlit as st
import os
import json
import paho.mqtt.client as paho
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Control de Voz",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS: ESTILO LIMPIO Y CONTRASTE ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .main-title { color: #212529; font-weight: 700; font-size: 2.2em; margin-bottom: 2px; }
    .sub-title { color: #6c757d; font-weight: 400; margin-top: 0px; margin-bottom: 20px; }
    .flat-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        padding: 20px;
        margin-bottom: 15px;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .card-header { color: #495057; font-weight: 600; font-size: 1.1em; margin-bottom: 15px; width: 100%; text-align: left;}
    .bk-btn {
        background-color: #28a745 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        border: none !important;
        font-size: 1.0em !important;
        height: 45px !important;
        width: 150px !important;
    }
    #MainMenu, footer, header {visibility: hidden;}
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
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

# --- CUERPO PRINCIPAL ---
col_ctrl, col_msg = st.columns([1.3, 1], gap="medium")

# Columna 1: Panel de Control
with col_ctrl:
    st.markdown('<div class="flat-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-header">Panel de Acción</div>', unsafe_allow_html=True)
    
    try:
        image = Image.open('persona hablando.jpg')
        st.image(image, width=250, use_column_width=False)
    except:
        st.info("Imagen 'persona hablando.jpg' no encontrada.")

    st.markdown("---", style="width: 100%;")
    st.write("Pulsa 'Inicio' y habla.")
    
    stt_button = Button(label="Inicio", width=150)
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

# Columna 2: Panel de Feedback
with col_msg:
    st.markdown('<div class="flat-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-header">Estado y Respuestas</div>', unsafe_allow_html=True)
    
    st.markdown("**MQTT:** `broker.mqttdashboard.com` 🟢 Conectado")
    
    log_area = st.empty()
    log_area.info("Último Comando: [Esperando entrada...]")
    
    if result and "GET_TEXT" in result:
        comando = result.get("GET_TEXT")
        log_area.success(f"**Detectado:** {comando}")
        
        mensaje_json = json.dumps({"Act1": comando.strip()})
        st.session_state.client.publish(topic, mensaje_json)
        st.write(f"📤 Enviado a: `{topic}`")

    st.markdown('</div>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("---")
st.caption(f"Status: Connected | Broker: {broker} | Client: {client_id}")
