import streamlit as st
import os
import json
import paho.mqtt.client as paho
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Control por Voz Premium", layout="wide", initial_sidebar_state="collapsed")

# --- CSS AVANZADO: GLASSMORPHISM & MICRO-INTERACCIONES ---
# Este bloque CSS transforma completamente la estética de la app
st.markdown("""
    <style>
    /* Fondo de la página con degradado suave */
    .stApp {
        background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%);
    }

    /* Tarjeta principal con efecto Glassmorphism */
    .glass-card {
        background: rgba(255, 255, 255, 0.25);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.18);
        padding: 40px;
        margin: auto;
        max-width: 800px;
        text-align: center;
    }

    /* Estilo del título principal */
    .main-title {
        font-family: 'Helvetica Neue', sans-serif;
        color: #1a2a4a;
        font-weight: 700;
        letter-spacing: -1px;
        margin-bottom: 5px;
    }

    /* Estilo del subtítulo */
    .sub-title {
        font-family: 'Helvetica Neue', sans-serif;
        color: #5c6c8c;
        font-weight: 300;
        margin-bottom: 30px;
    }

    /* Botón Bokeh personalizado como círculo flotante */
    .bk-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 50px !important; /* Círculo */
        border: none !important;
        box-shadow: 0 4px 15px rgba(118, 75, 162, 0.3) !important;
        transition: all 0.3s ease !important; /* Animación suave */
        font-size: 1.1em !important;
        height: 60px !important;
        width: 150px !important;
    }

    /* Micro-interacción: Efecto hover en el botón */
    .bk-btn:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
        transform: translateY(-2px); /* Pequeño salto */
        box-shadow: 0 6px 20px rgba(118, 75, 162, 0.4) !important;
    }

    /* Contenedor del feedback MQTT */
    .feedback-box {
        background-color: rgba(255, 255, 255, 0.5);
        border-radius: 10px;
        padding: 15px;
        margin-top: 20px;
        font-family: monospace;
        font-size: 0.9em;
        border: 1px solid rgba(0,0,0,0.05);
    }

    /* Ocultar el footer por defecto de Streamlit */
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA MQTT (SE MANTIENE IGUAL) ---
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
# Usamos HTML para aplicar las clases de estilo definidas arriba
st.markdown('<h1 class="main-title">Interfaces Multimodales</h1>', unsafe_allow_html=True)
st.markdown('<h3 class="sub-title">Control por Voz Premium</h3>', unsafe_allow_html=True)

# --- CUERPO PRINCIPAL (TARJETAglass) ---
# Creamos un contenedor centrado
col_main = st.columns([1, 4, 1])[1]

with col_main:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    # Imagen centrada y estilizada
    try:
        image = Image.open('persona hablando.jpg')
        st.image(image, width=150, use_column_width=False, output_format="PNG")
    except:
        st.info("Imagen 'persona hablando.jpg' no encontrada.")

    st.markdown("---")
    
    st.markdown("##### Pulsa el botón y habla claramente.")
    
    # Botón Bokeh estilizado por el CSS
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
        refresh_on_update=False, override_height=80, debounce_time=0)
    
    # Área de Feedback dinámica
    if result and "GET_TEXT" in result:
        comando = result.get("GET_TEXT")
        
        # Feedback visual inmediato
        st.success(f"**Detectado:** {comando}")
        
        # Publicación MQTT
        mensaje_json = json.dumps({"Act1": comando.strip()})
        st.session_state.client.publish(topic, mensaje_json)
        
        st.markdown(f'<div class="feedback-box">📤 Enviado a: `{topic}`</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True) # Cierre de glass-card

# --- FOOTER SUTIL ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.columns([1, 6, 1])[1].caption(f"Status: Connected | Broker: {broker} | Client: {client_id}")
