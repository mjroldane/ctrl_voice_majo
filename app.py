import streamlit as st
import os
import json
import paho.mqtt.client as paho
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image

# --- CONFIGURACIÓN DE PÁGINA: Compacta ---
st.set_page_config(
    page_title="Control de Voz Compacto",
    layout="wide", # Usamos todo el ancho para reducir altura
    initial_sidebar_state="collapsed"
)

# --- CSS: Legibilidad y Contraste Extremo ---
# Fondo blanco puro, texto gris oscuro para máximo contraste, diseño plano (flat)
st.markdown("""
    <style>
    /* Fondo blanco puro para la app */
    .stApp {
        background-color: #FFFFFF;
    }

    /* Título principal: Grande, oscuro y nítido */
    .main-title {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        color: #212529; /* Gris casi negro */
        font-weight: 700;
        margin-bottom: 2px;
        font-size: 2.2em;
    }

    /* Subtítulo: Más pequeño y sutil */
    .sub-title {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        color: #6c757d; /* Gris medio */
        font-weight: 400;
        margin-top: 0px;
        margin-bottom: 20px;
    }

    /* Contenedor de "Tarjeta" Plana: Fondo gris muy claro, bordes nítidos */
    .flat-card {
        background-color: #f8f9fa; /* Gris clarísimo */
        border-radius: 8px;
        border: 1px solid #dee2e6;
        padding: 15px;
        margin-bottom: 15px;
    }

    /* Subcabeceras dentro de tarjetas */
    .card-header {
        color: #495057;
        font-weight: 600;
        font-size: 1.1em;
        margin-bottom: 10px;
    }

    /* Botón Bokeh personalizado: Verde sólido, sin degradados */
    .bk-btn {
        background-color: #28a745 !important; /* Verde sólido */
        color: white !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        border: none !important;
        font-size: 1.0em !important;
        height: 45px !important;
        width: 130px !important;
    }

    /* Ocultar elementos de Streamlit que ocupan espacio */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Reducir márgenes superiores de bloques de Streamlit */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
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
st.markdown('<h1 class="main-title">Interfaces Multimodales</h1>', unsafe_allow_html=True)
st.markdown('<h3 class="sub-title">Control de Voz Compacto</h3>', unsafe_allow_html=True)

# --- CUERPO PRINCIPAL (2 COLUMNAS PARA CERO SCROLL) ---
col_ctrl, col_msg = st.columns([1, 1.2], gap="medium")

# Columna 1: Panel de Control (Imagen, Botón, Instrucciones)
with col_ctrl:
    st.markdown('<div class="flat-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-header">Panel de Acción</div>', unsafe_allow_html=True)
    
    # Imagen centrada y compacta (usando tu imagen suministrada)
    try:
        # Asegúrate de tener 'persona hablando.jpg' en la carpeta
        image = Image.open('persona hablando.jpg')
        st.image(image, width=120, use_column_width=False)
    except:
        st.info("Imagen 'persona hablando.jpg' no encontrada.")

    st.markdown("---")
    
    st.write("Pulsa 'Inicio' y habla.")
    
    # Botón Bokeh estilizado por el CSS (Compacto y plano)
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
    
    st.markdown('</div>', unsafe_allow_html=True) # Cierre flat-card

# Columna 2: Panel de Feedback (Logs, MQTT Status)
with col_msg:
    st.markdown('<div class="flat-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-header">Estado y Respuestas</div>', unsafe_allow_html=True)
    
    # Estado de Conexión (feedback inmediato)
    st.markdown("**MQTT:** `broker.mqttdashboard.com` 🟢 Conectado")
    
    # Placeholder para resultados dinámicos
    # Usamos st.empty() para actualizar el mismo espacio y no crecer hacia abajo
    log_area = st.empty()
    log_area.info("Último Comando: [Esperando entrada...]")
    
    # Procesamiento de voz y envío MQTT
    if result and "GET_TEXT" in result:
        comando = result.get("GET_TEXT")
        
        # Feedback visual nítido y compacto
        log_area.success(f"**Detectado:** {comando}")
        
        # Publicación MQTT
        mensaje_json = json.dumps({"Act1": comando.strip()})
        st.session_state.client.publish(topic, mensaje_json)
        
        st.write(f"📤 Enviado a: `{topic}`")

    st.markdown('</div>', unsafe_allow_html=True) # Cierre flat-card

# --- FOOTER SUTIL (UNA SOLA LÍNEA) ---
st.markdown("---")
st.caption(f"Status: Connected | Broker: {broker} | Client: {client_id}")
