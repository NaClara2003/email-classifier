import streamlit as st
import requests
import json
import os
from PyPDF2 import PdfReader
from dotenv import load_dotenv

# --- 1. CONFIGURAÇÕES ---
load_dotenv()
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

# URL Direta da API (Usando v1 estável para evitar o erro 404 da v1beta)
API_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"

def classificar_email(texto_email):
    # Prompt técnico para garantir retorno JSON
    prompt = (
        "Você é um assistente financeiro da AutoU. Classifique o e-mail abaixo em "
        "[Produtivo] ou [Improdutivo] e sugira uma resposta. "
        "Retorne APENAS um JSON com as chaves 'categoria' e 'resposta'.\n\n"
        f"E-mail: {texto_email}"
    )

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "response_mime_type": "application/json"
        }
    }

    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status() # Vai gerar erro se não for 200 OK
        
        result = response.json()
        # Extrai o texto JSON da estrutura de resposta do Google
        return result['candidates'][0]['content']['parts'][0]['text']
    
    except Exception as e:
        # Se der erro 404 aqui, saberemos que é a URL ou a Chave
        return json.dumps({"categoria": "Erro", "resposta": f"Erro na API Direta: {str(e)}"})

# --- 3. ESTILIZAÇÃO CSS ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007BFF; color: white; font-weight: bold; border: none; }
    .result-card { background-color: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 20px; border: 1px solid #e1e4e8; }
    .category-tag { padding: 6px 14px; border-radius: 20px; font-weight: bold; font-size: 0.85em; text-transform: uppercase; }
    .produtivo { background-color: #d4edda; color: #155724; }
    .improdutivo { background-color: #f8d7da; color: #721c24; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. INTERFACE ---
st.title("📧 Smart Mail Sorter - AutoU")
st.subheader("Análise inteligente de e-mails para o setor financeiro")
st.markdown("---")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 📥 Entrada de Dados")
    metodo = st.radio("Escolha o método:", ("Upload de Arquivo", "Colar Texto manualmente"))
    
    email_text = ""
    if metodo == "Upload de Arquivo":
        arquivo = st.file_uploader("Suba seu .txt ou .pdf", type=["txt", "pdf"])
        if arquivo:
            email_text = extrair_texto(arquivo)
    else:
        email_text = st.text_area("Cole o e-mail aqui:", height=250)

    analisar_btn = st.button("🚀 Analisar E-mail")

with col2:
    st.markdown("### 📊 Resultado da Análise")
    
    if analisar_btn and email_text.strip():
        with st.spinner('Processando com Gemini AI...'):
            res_json = classificar_email(email_text)
            try:
                dados = json.loads(res_json)
                cat = dados.get("categoria", "N/A")
                resp = dados.get("resposta", "")
                cor = "produtivo" if cat.lower() == "produtivo" else "improdutivo"
                
                st.markdown(f"""
                <div class="result-card">
                    <h4>Status: <span class="category-tag {cor}">{cat}</span></h4>
                    <hr>
                    <p><b>Sugestão:</b></p>
                    <div style="background-color:#f8f9fa; padding:15px; border-left:5px solid #007BFF;">{resp}</div>
                </div>
                """, unsafe_allow_html=True)
            except:
                st.error("Erro ao processar resposta.")
    else:
        st.info("Aguardando entrada...")

st.markdown("---")
st.caption("AutoU Processo Seletivo | Desenvolvido por Ana Clara Nery e Mello Figueiredo")