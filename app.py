import streamlit as st
from google import genai
from PyPDF2 import PdfReader
import os

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Asistente Experto Gemini", page_icon="📚")
st.title("🤖 Consultas al Experto (v2.0)")

# --- 2. CONFIGURACIÓN DEL NUEVO CLIENTE ---
if "GOOGLE_API_KEY" in st.secrets:
    try:
        # La nueva forma de conectar con Gemini
        client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
    except Exception as e:
        st.error(f"Error al conectar con la nueva API: {e}")
        st.stop()
else:
    st.error("⚠️ Falta la API Key en los Secrets.")
    st.stop()

# --- 3. CARGA DE DOCUMENTOS ---
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
                    texto_página = page.extract_text()
                    if texto_página:
                        texto_total += texto_página
            except Exception as e:
                st.warning(f"No se pudo leer {archivo}: {e}")
    return texto_total

contexto_maestro = cargar_base_conocimiento()

if not contexto_maestro:
    st.info("Sube PDFs a la carpeta 'documentos' en GitHub para comenzar.")
    st.stop()

# --- 4. LÓGICA DEL CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if pregunta := st.chat_input("Pregúntame algo sobre los documentos:"):
    st.session_state.messages.append({"role": "user", "content": pregunta})
    with st.chat_message("user"):
        st.markdown(pregunta)

    with st.chat_message("assistant"):
        try:
            # Nueva forma de generar contenido
            prompt_final = f"Usa este texto para responder: {contexto_maestro}. Pregunta: {pregunta}"
            
            response = client.models.generate_content(
                model="gemini-1.5-flash", 
                contents=prompt_final
            )
            
            respuesta_ia = response.text
            st.markdown(respuesta_ia)
            st.session_state.messages.append({"role": "assistant", "content": respuesta_ia})
            
        except Exception as e:
            st.error(f"Error con la nueva librería: {e}")
