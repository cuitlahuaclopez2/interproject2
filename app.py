import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Asistente Virtual Experto", page_icon="📚")
st.title("🤖 Consultas al Experto")
st.info("Este chat responde basado exclusivamente en nuestra base de conocimientos oficial.")

# --- CONEXIÓN CON GEMINI ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Error: Configura la API Key en los Secrets de Streamlit.")
    st.stop()

# --- FUNCIÓN PARA CARGAR DOCUMENTOS DEL SERVIDOR ---
@st.cache_resource # Esto hace que solo lea los archivos UNA vez (ahorra tiempo y dinero)
def cargar_base_conocimiento():
    texto_total = ""
    ruta_docs = "documentos" # Nombre de la carpeta en GitHub
    
    if os.path.exists(ruta_docs):
        archivos = [f for f in os.listdir(ruta_docs) if f.endswith('.pdf')]
        for archivo in archivos:
            try:
                path = os.path.join(ruta_docs, archivo)
                reader = PdfReader(path)
                for page in reader.pages:
                    texto_total += page.extract_text()
            except Exception as e:
                st.error(f"Error leyendo {archivo}: {e}")
    return texto_total

# Cargamos el conocimiento del administrador
contexto_maestro = cargar_base_conocimiento()

if not contexto_maestro:
    st.warning("⚠️ El administrador aún no ha subido documentos a la carpeta 'documentos'.")
    st.stop()

# --- LÓGICA DEL CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar historial
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada del usuario
if pregunta := st.chat_input("Haz tu pregunta aquí..."):
    st.session_state.messages.append({"role": "user", "content": pregunta})
    with st.chat_message("user"):
        st.markdown(pregunta)

    # Respuesta de Gemini
    with st.chat_message("assistant"):
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # El "System Prompt" es lo más importante aquí
        prompt_final = f"""
        Eres un asistente oficial y profesional. 
        Tu conocimiento se limita ESTRICTAMENTE al texto que se te proporciona a continuación.
        Si la respuesta no está en el texto, responde educadamente que no tienes esa información.
        
        CONOCIMIENTO OFICIAL:
        {contexto_maestro}
        
        PREGUNTA DEL USUARIO:
        {pregunta}
        """
        
        try:
            response = model.generate_content(prompt_final)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Error: {e}")
