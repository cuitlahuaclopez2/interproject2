import streamlit as st
from google import genai
from PyPDF2 import PdfReader
import os

# 1. Configuración de la página
st.set_page_config(page_title="Gemini 2.0 Expert")
st.title("🤖 Consultas Gemini 2.0 Flash")

# 2. Manejo de Credenciales (Corregida la indentación del if/else)
if "GOOGLE_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Falta la API Key en Secrets")
    st.stop()

# 3. Función para extraer texto (Corregida la estructura de bucles)
def obtener_texto():
    texto_acumulado = ""
    if os.path.exists("documentos"):
        for f in os.listdir("documentos"):
            if f.endswith(".pdf"):
                pdf = PdfReader(os.path.join("documentos", f))
                for pagina in pdf.pages:
                    texto_acumulado += pagina.extract_text()
    return texto_acumulado

# 4. Carga de contexto y estado de sesión
contexto_base = obtener_texto()

if "historial" not in st.session_state:
    st.session_state.historial = []

# 5. Mostrar historial de chat
for m in st.session_state.historial:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# 6. Lógica de entrada y respuesta
if pregunta := st.chat_input("Escribe tu duda:"):
    # Agregar pregunta del usuario
    st.session_state.historial.append({"role": "user", "content": pregunta})
    with st.chat_message("user"):
        st.markdown(pregunta)
    
    # Aquí faltaría la llamada a Gemini para generar la respuesta:
    # prompt_final = f"Contexto: {contexto_base}\n\nPregunta: {pregunta}"
    # response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt_final)
    # ... (agregar respuesta al historial)
