import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import os

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Asistente Experto", page_icon="📚")
st.title("🤖 Consultas al Experto")

# --- 2. MANEJO DE ERRORES DE CONFIGURACIÓN (Aquí va la seguridad) ---
if "GOOGLE_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # Definimos el modelo aquí para que esté disponible en toda la app
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Error al configurar Google AI: {e}")
        st.stop()
else:
    st.error("⚠️ No se encontró la API Key en los Secrets de Streamlit.")
    st.stop()

# --- 3. CARGA DE DOCUMENTOS (Solo el administrador) ---
@st.cache_resource
def cargar_base_conocimiento():
    texto_total = ""
    ruta_docs = "documentos"
    if os.path.exists(ruta_docs):
        archivos = [f for f in os.listdir(ruta_docs) if f.endswith('.pdf')]
        for archivo in archivos:
            try:
                reader = PdfReader(os.path.join(ruta_docs, archivo))
                for page in reader.pages:
                    texto_total += page.extract_text()
            except Exception as e:
                st.warning(f"No se pudo leer {archivo}: {e}")
    return texto_total

contexto_maestro = cargar_base_conocimiento()

if not contexto_maestro:
    st.info("Esperando documentos en la carpeta 'documentos'...")
    st.stop()

# --- 4. LÓGICA DEL CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Dibujar mensajes previos
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada del usuario
if pregunta := st.chat_input("Haz tu pregunta sobre los documentos:"):
    st.session_state.messages.append({"role": "user", "content": pregunta})
    with st.chat_message("user"):
        st.markdown(pregunta)

    # --- MANEJO DE ERRORES EN LA RESPUESTA ---
    with st.chat_message("assistant"):
        try:
            # Creamos el prompt con el contexto de tus PDFs
            prompt_final = f"Usa este texto: {contexto_maestro}. Pregunta: {pregunta}"
            
            # Llamada limpia a la API
            response = model.generate_content(prompt_final)
            
            respuesta_ia = response.text
            st.markdown(respuesta_ia)
            st.session_state.messages.append({"role": "assistant", "content": respuesta_ia})
            
        except Exception as e:
            # Si el error 404 persiste, aquí te dirá exactamente por qué
            st.error(f"Error detallado de la API: {e}")
            st.info("Si ves un error 404, asegúrate de haber actualizado el archivo requirements.txt con google-generativeai==0.8.3")
