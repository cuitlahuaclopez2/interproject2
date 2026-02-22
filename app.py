import streamlit as st
from google import genai
from PyPDF2 import PdfReader
import os

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Asistente Gemini 2.0", page_icon="🚀", layout="centered")
st.title("🤖 Consultas con Gemini 2.0 Flash")
st.markdown("---")

# --- 2. CONFIGURACIÓN DEL CLIENTE (API v1) ---
# Asegúrate de configurar GOOGLE_API_KEY en los Secrets de Streamlit Cloud
if "GOOGLE_API_KEY" in st.secrets:
    try:
        # El SDK moderno usa la versión estable v1 automáticamente
        client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
    except Exception as e:
        st.error(f"Error al conectar con la API de Google: {e}")
        st.stop()
else:
    st.error("⚠️ No se encontró la clave 'GOOGLE_API_KEY' en los Secrets de Streamlit.")
    st.info("Ve a Settings > Secrets en Streamlit Cloud y agrega tu clave.")
    st.stop()

# --- 3. PROCESAMIENTO DE DOCUMENTOS PDF ---
@st.cache_resource
def cargar_contexto_pdfs():
    texto_acumulado = ""
    carpeta_docs = "documentos"
    
    if os.path.exists(carpeta_docs):
        archivos = [f for f in os.listdir(carpeta_docs) if f.endswith('.pdf')]
        if not archivos:
            return None
        
        for nombre_archivo in archivos:
            try:
                ruta_completa = os.path.join(carpeta_docs, nombre_archivo)
                reader = PdfReader(ruta_completa)
                for page in reader.pages:
                    texto_extraido = page.extract_text()
                    if texto_extraido:
                        texto_acumulado += texto_extraido + "\n"
            except Exception as e:
                st.warning(f"Error al leer el archivo {nombre_archivo}: {e}")
    else:
        return None
    
    return texto_acumulado

# Cargamos el contenido de la carpeta 'documentos'
contexto_maestro = cargar_contexto_pdfs()

if not contexto_maestro:
    st.warning("📂 No se encontraron archivos PDF en la carpeta 'documentos'.")
    st.info("Asegúrate de que tu repositorio en GitHub tenga una carpeta llamada 'documentos' con tus PDFs.")
    st.stop()

# --- 4. LÓGICA DEL CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar historial de mensajes
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada de usuario
if prompt := st.chat_input("¿Qué deseas consultar sobre tus documentos?"):
    # Guardar y mostrar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generar respuesta de la IA
    with st.chat_message("assistant"):
        try:
            # Instrucción con el contexto de los PDFs
            prompt_final = f"Contexto de los documentos:\n{contexto_maestro}\n\nPregunta: {prompt}"
            
            # Llamada al nuevo modelo Gemini 2.0 Flash
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt_final
            )
            
            respuesta_texto = response.text
            st.markdown(respuesta_texto)
            
            # Guardar respuesta en el historial
            st.session_state.messages.append({"role": "assistant", "content": respuesta_texto})
            
        except Exception as e:
            st.error(f"Hubo un error al generar la respuesta: {e}")
