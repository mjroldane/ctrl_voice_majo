import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import paho.mqtt.client as paho
import json

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Control por Voz", layout="centered")

# --- CSS PARA EL ESTILO "MORADITO" ---
st.markdown("""
    <style>
    /* Fondo de la app */
    .stApp {
        background-color: #F3E5F5;
    }
    
    /* Contenedor tipo tarjeta */
    .card {
        background-color: #FFFFFF;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0px 4px 15px rgba(126, 87, 194, 0.2);
        border: 1px solid #E1BEE7;
    }
    
    /* Estilo de texto */
    h1, h2, h3 {
        color: #4A148C !important;
    }
    
    /* Botón personalizado para que combine */
    div.stButton > button {
        background-color: #7E57C2 !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 10px 20px !important;
        font-weight: bold;
    }
    div.stButton > button:hover {
        background-color: #5E35B1 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA MQTT ---
def on_publish(client, userdata, result):
    print("El dato ha sido publicado \n")

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(f"Mensaje recibido: {message_received}")

broker = "broker.mqttdashboard.com"
port = 1883
client1 = paho.Client("Majorolgib")
client1.on_message = on_message

# --- INTERFAZ GRÁFICA ---
st.title("💜 Detecta tu voz aquí")
st.subheader("Control por Voz")

# Usamos un contenedor para que se vea como una tarjeta
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    try:
        image = Image.open('voice_ctrl.jpg')
        st.image(image, width=200)
    except:
        st.warning("Imagen 'voice_ctrl.jpg' no encontrada en la carpeta.")

    st.write("Pulsa el botón e inicia tu comando de voz.")

    # Botón Bokeh estilizado
    stt_button = Button(label=" Inicio ", width=200)

    stt_button.js_on_event("button_click", CustomJS(code="""
        var recognition = new webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
    
        recognition.onresult = function (e) {
            var value = "";
            for (var i = e.resultIndex; i < e.results.length; ++i) {
                if (e.results[i].isFinal) {
                    value += e.results[i][0].transcript;
                }
            }
            if ( value != "") {
                document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
            }
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

    # --- LÓGICA DE PUBLICACIÓN (NO ALTERADA) ---
    if result:
        if "GET_TEXT" in result:
            texto_detectado = result.get("GET_TEXT")
            st.success(f"Detectado: {texto_detectado}")
            
            client1.on_publish = on_publish                            
            client1.connect(broker, port)  
            message = json.dumps({"Act1": texto_detectado.strip()})
            ret = client1.publish("Majoroldan", message)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Carpeta temporal
try:
    os.mkdir("temp")
except:
    pass
