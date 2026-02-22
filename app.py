import streamlit as st
import os

# Intentar la importación moderna con manejo de error
try:
    from google import genai
except ImportError:
    st.error("Error de importación: No se encontró la librería 'google-genai'.")
    st.info("Asegúrate de que 'google-genai' esté en tu requirements.txt y reinicia la app.")
    st.stop()

from PyPDF2 import PdfReader

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Asistente Experto Gemini", page_icon="📚")
st.title("🤖 Consultas al Experto")

# --- 2. CONFIGURACIÓN DEL CLIENTE ---
# Usamos st.secrets para la API Key
if "GOOGLE_API_KEY" in st.secrets:
    try:
        client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
    except Exception as e:
        st.error(f"Error al inicializar el cliente: {e}")
        st.stop()
else:
    st.error("⚠️ Falta la API Key en los Secrets de Streamlit.")
    st.stop()

# ... (El resto del código de carga de PDFs y Chat sigue igual) ...
# --- 3. CARGA DE DOCUMENTOS DESDE CARPETA ---
@st.cache_resource
def cargar_conocimiento_local():
    texto_total = ""
    ruta = "documentos"
    if os.path.exists(ruta):
        archivos = [f for f in os.listdir(ruta) if f.endswith('.pdf')]
        for archivo in archivos:
            try:
                path_completo = os.path.join(ruta, archivo)
                reader = PdfReader(path_completo)
                for page in reader.pages:
                    texto_total += page.extract_text() + "\n"
            except Exception as e:
                st.warning(f"Error leyendo {archivo}: {e}")
    return texto_total

contexto_maestro = cargar_conocimiento_local()

if not contexto_maestro:
    st.info("Sube tus archivos PDF a la carpeta 'documentos' en GitHub para activar la IA.")
    st.stop()

# --- 4. INTERFAZ DE CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar historial de mensajes
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada de usuario
if prompt := st.chat_input("¿En qué puedo ayudarte hoy?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Respuesta de la IA
    with st.chat_message("assistant"):
        try:
            # Construcción del mensaje para la nueva API
            instruccion = f"Contexto: {contexto_maestro}\n\nPregunta: {prompt}"
            
            # Nueva sintaxis: client.models.generate_content
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=instruccion
            )
            
            respuesta_texto = response.text
            st.markdown(respuesta_texto)
            st.session_state.messages.append({"role": "assistant", "content": respuesta_texto})
            
        except Exception as e:
            st.error(f"Error en la generación: {e}")
            st.info("Verifica que tu API Key tenga permisos para Gemini 1.5 Flash.")
