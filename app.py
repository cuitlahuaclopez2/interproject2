import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import os

# 1. Configuración de la página y Estilo
st.set_page_config(page_title="Mi IA de Documentos", page_icon="🤖")
st.title("📄 Chat con mis Documentos")
st.markdown("Sube un PDF y hazle preguntas a Gemini sobre su contenido.")

# 2. Conexión Segura con Gemini (Usando los Secrets de Streamlit)
# Esto busca la clave que pegaste en "Advanced Settings"
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Falta la configuración de la API Key en los Secrets de Streamlit.")
    st.stop()

# 3. Función para extraer texto del PDF
def leer_pdf(file):
    pdf_reader = PdfReader(file)
    texto = ""
    for page in pdf_reader.pages:
        texto += page.extract_text()
    return texto

# 4. Interfaz de subida de archivos
archivo_subido = st.file_uploader("Selecciona un archivo PDF", type="pdf")

if archivo_subido:
    # Extraemos el texto una sola vez para ahorrar memoria
    if "contexto_documento" not in st.session_state:
        with st.spinner("Leyendo el documento..."):
            st.session_state.contexto_documento = leer_pdf(archivo_subido)
            st.success("¡Documento cargado con éxito!")

    # 5. Historial del Chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostrar mensajes previos
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 6. Lógica de Preguntas y Respuestas
    if pregunta := st.chat_input("¿Qué quieres saber de este documento?"):
        # Mostrar pregunta del usuario
        st.session_state.messages.append({"role": "user", "content": pregunta})
        with st.chat_message("user"):
            st.markdown(pregunta)

        # Consultar a Gemini
        with st.chat_message("assistant"):
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Instrucción maestra (System Prompt)
            prompt_final = f"""
            Eres un asistente experto. Usa SOLO la siguiente información para responder.
            Si la respuesta no está en el texto, di que no lo sabes.
            
            INFORMACIÓN DEL DOCUMENTO:
            {st.session_state.contexto_documento}
            
            PREGUNTA DEL USUARIO:
            {pregunta}
            """
            
            try:
                response = model.generate_content(prompt_final)
                respuesta_texto = response.text
                st.markdown(respuesta_texto)
                st.session_state.messages.append({"role": "assistant", "content": respuesta_texto})
            except Exception as e:
                st.error(f"Hubo un error con Gemini: {e}")

else:
    st.info("👋 Por favor, sube un archivo PDF para comenzar a chatear.")
