import streamlit as st
from google import genai
from PyPDF2 import PdfReader
import os
st.set_page_config(page_title="Gemini 2.0 Expert")
st.title("🤖 Consultas Gemini 2.0 Flash")
if "GOOGLE_API_KEY" in st.secrets:
  client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
  else:
    st.error("Falta la API Key en Secrets")
    st.stop()
def obtener_texto():
texto_acumulado = ""
if os.path.exists("documentos"):
for f in os.listdir("documentos"):
if f.endswith(".pdf"):
pdf = PdfReader(os.path.join("documentos", f))
for pagina in pdf.pages:
texto_acumulado += pagina.extract_text()
return texto_acumulado

contexto_base = obtener_texto()
if "historial" not in st.session_state:
st.session_state.historial = []

for m in st.session_state.historial:
with st.chat_message(m["role"]):
st.markdown(m["content"])

if pregunta := st.chat_input("Escribe tu duda:"):
st.session_state.historial.append({"role": "user", "content": pregunta})
with st.chat_message("user"):
st.markdown(pregunta)
