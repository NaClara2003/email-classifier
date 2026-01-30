import streamlit as st
import openai
from PyPDF2 import PdfReader
import os
from dotenv import load_dotenv

# Carrega a chave da API do arquivo .env
load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- FUNÇÃO PARA EXTRAIR TEXTO ---
def extrair_texto(arquivo):
    if arquivo.type == "text/plain":
        return str(arquivo.read(), "utf-8")
    elif arquivo.type == "application/pdf":
        reader = PdfReader(arquivo)
        texto = ""
        for page in reader.pages:
            texto += page.extract_text()
        return texto
    return None

# --- FUNÇÃO DE IA (PROMPT MESTRE) ---
def classificar_email(texto_email):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um assistente financeiro. Classifique o email em [Produtivo] ou [Improdutivo]. Retorne JSON: {'categoria': '...', 'resposta': '...'}"},
                {"role": "user", "content": texto_email}
            ],
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro na API: {e}"
