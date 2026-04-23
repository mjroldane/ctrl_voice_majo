import streamlit as st
import os
import json
import paho.mqtt.client as paho
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Control Multimodal", layout="wide")

# --- CSS PARA ESTÉTICA DE DASHBOARD ---
st.markdown("""
    <style>
    .card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #e0e0e0;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .stButton button {
        width: 100%;
        border-radius: 10px;
        height: 50px;
        background-color: #4CAF50;
        color: white;
    }
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
st.title("INTERFACES MULTIMODALES")
st.markdown("### CONTROL POR VOZ")

try:
    image = Image.open('voice_ctrl.jpg')
    st.image(image, width=300)
except:
    st.info("Imagen 'voice_ctrl.jpg' no encontrada.")

# --- CUERPO PRINCIPAL ---
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("CONTROL DE VOZ")
    st.markdown("""
    **INSTRUCCIONES:**
    1. Toca el botón 'Inicio'.
    2. Habla claramente tu comando.
    3. El sistema procesará tu voz.
    """)
    
    stt_button = Button(label="Inicio", width=200)
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
        refresh_on_update=False, override_height=60, debounce_time=0)
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("MENSAJES RECIBIDOS")
    st.write("🟢 **MQTT Estado:** Conectado")
    
    last_cmd = st.empty()
    last_cmd.info("Último Comando: [Esperando entrada...]")
    
    if result and "GET_TEXT" in result:
        comando = result.get("GET_TEXT")
        last_cmd.success(f"Último Comando: {comando}")
        
        mensaje_json = json.dumps({"Act1": comando.strip()})
        st.session_state.client.publish(topic, mensaje_json)
        st.write(f"**Respuesta MQTT:** Mensaje enviado a {topic}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("---")
st.markdown("**Configuración:**")
cols = st.columns(4)
cols[0].markdown(f"Broker: `{broker}`")
cols[1].markdown(f"Puerto: `{port}`")
cols[2].markdown(f"Cliente: `{client_id}`")
cols[3].markdown(f"Tópico: `{topic}`")
