import os
import json
import platform
import streamlit as st
import paho.mqtt.client as paho
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image

# Configuración de la página
st.set_page_config(
    page_title="Control por Voz",
    page_icon="🎤",
    layout="centered"
)

# Estilos minimalistas
st.markdown("""
<style>
  body { background-color: #ffffff; color: #000000; }
  .block-container { max-width: 600px; margin: auto; padding: 2rem; background: #000000; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
  h1, h2, h3 { color: #000000; }
  .stButton > button { background-color: #0066cc; color: #ffffff; border: none; border-radius: 8px; padding: 0.75rem 1.5rem; font-size: 1rem; transition: background-color 0.2s; }
  .stButton > button:hover { background-color: #005bb5; }
  .message-count { font-size: 1.25rem; margin-top: 1.5rem; text-align: center; color: #000000; }
  img { display: block; margin-left: auto; margin-right: auto; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# Título
st.title("🎤 Control por Voz Minimalista")
st.subheader("Presiona el botón y habla")

# Imagen central
if os.path.exists("voice_ctrl.jpg"):
    img = Image.open("voice_ctrl.jpg")
    st.image(img, width=200)

# Inicializar contador de mensajes
if 'message_count' not in st.session_state:
    st.session_state.message_count = 0

# Datos de conexión MQTT
broker = "157.230.214.127"
port = 1883

# Callback de publicación MQTT
def on_publish(client, userdata, result):
    pass

# Configurar cliente MQTT
client = paho.Client("StreamlitVoiceClient")
client.on_publish = on_publish

# Botón de reconocimiento de voz
voice_btn = Button(label="🎤 Iniciar", width=200, height=50)
voice_btn.js_on_event("button_click", CustomJS(code="""
    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new Recognition();
    recognition.interimResults = false;
    recognition.onresult = e => {
        const text = e.results[0][0].transcript;
        document.dispatchEvent(new CustomEvent('GET_TEXT', {detail: text}));
    };
    recognition.start();
"""))

# Escuchar eventos de voz
result = streamlit_bokeh_events(
    voice_btn,
    events="GET_TEXT",
    key="voice_event",
    debounce_time=0,
    override_height=75,
)

# Procesar y publicar texto reconocido
def publish_and_count(text):
    st.write(f"**Tú dijiste:** {text}")
    payload = json.dumps({"Act1": text})
    client.connect(broker, port)
    client.publish("voiceNicoR", payload)
    st.success("Mensaje enviado!")
    st.session_state.message_count += 1

if result and 'GET_TEXT' in result:
    text = result['GET_TEXT'].strip()
    publish_and_count(text)

# Mostrar contador de mensajes
st.markdown(f"<div class='message-count'>Mensajes enviados: {st.session_state.message_count}</div>", unsafe_allow_html=True)
