import streamlit as st
import openai
from PyPDF2 import PdfReader
import os
import json
from dotenv import load_dotenv

# --- 1. CONFIGURAÇÕES INICIAIS E SEGURANÇA ---
load_dotenv()
# Se estiver usando Streamlit Cloud/Render, ele buscará em secrets/env vars
api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)

st.set_page_config(page_title="AutoU | Classificador Inteligente", page_icon="🤖", layout="wide")

# --- 2. FUNÇÕES LÓGICAS (BACKEND) ---

def extrair_texto(arquivo):
    """Extrai texto de arquivos TXT ou PDF."""
    try:
        if arquivo.type == "text/plain":
            return str(arquivo.read(), "utf-8")
        elif arquivo.type == "application/pdf":
            reader = PdfReader(arquivo)
            texto = ""
            for page in reader.pages:
                texto += page.extract_text()
            return texto
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
    return None

def classificar_email(texto_email):
    """Envia o texto para a OpenAI e retorna a classificação e resposta."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "Você é um assistente especialista em triagem de e-mails financeiros. "
                        "Classifique o e-mail em [Produtivo] ou [Improdutivo]. "
                        "Produtivo: Solicitações, boletos, dúvidas, suporte. "
                        "Improdutivo: Agradecimentos, saudações, spam. "
                        "Retorne APENAS um JSON com as chaves 'categoria' e 'resposta'."
                    )
                },
                {"role": "user", "content": texto_email}
            ],
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    except Exception as e:
        return json.dumps({"categoria": "Erro", "resposta": f"Falha na comunicação com a IA: {str(e)}"})

# --- 3. ESTILIZAÇÃO CSS (O diferencial visual) ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007BFF; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #0056b3; border: none; }
    .result-card { background-color: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 20px; border: 1px solid #e1e4e8; }
    .category-tag { padding: 6px 14px; border-radius: 20px; font-weight: bold; font-size: 0.85em; text-transform: uppercase; }
    .produtivo { background-color: #d4edda; color: #155724; }
    .improdutivo { background-color: #f8d7da; color: #721c24; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. INTERFACE (FRONTEND) ---
st.title("📧 Smart Mail Sorter - AutoU")
st.subheader("Análise inteligente de e-mails para o setor financeiro")
st.markdown("---")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 📥 Entrada de Dados")
    metodo = st.radio("Escolha o método de entrada:", ("Upload de Arquivo", "Colar Texto manualmente"))
    
    email_text = ""
    
    if metodo == "Upload de Arquivo":
        arquivo = st.file_uploader("Arraste seu arquivo (.txt ou .pdf)", type=["txt", "pdf"])
        if arquivo:
            email_text = extrair_texto(arquivo)
            if email_text:
                st.info(f"Conteúdo extraído com sucesso ({len(email_text)} caracteres).")
    else:
        email_text = st.text_area("Cole o conteúdo do e-mail aqui:", height=250, placeholder="Ex: Segue em anexo o comprovante de pagamento...")

    analisar_btn = st.button("🚀 Analisar E-mail")

with col2:
    st.markdown("### 📊 Resultado da Análise")
    
    if analisar_btn:
        if email_text.strip():
            with st.spinner('A IA da AutoU está processando...'):
                resultado_bruto = classificar_email(email_text)
                
                try:
                    dados = json.loads(resultado_bruto)
                    categoria = dados.get("categoria", "N/A")
                    resposta = dados.get("resposta", "Sem resposta gerada.")

                    # Estilização dinâmica baseada na categoria
                    classe_css = "produtivo" if categoria.lower() == "produtivo" else "improdutivo"
                    
                    st.markdown(f"""
                    <div class="result-card">
                        <h4>Status: <span class="category-tag {classe_css}">{categoria}</span></h4>
                        <hr>
                        <p style="color: #444; margin-top: 10px;"><b>Sugestão de Resposta Automática:</b></p>
                        <div style="background-color: #f8f9fa; padding: 15px; border-left: 5px solid #007BFF; font-style: italic; color: #333; border-radius: 4px;">
                            "{resposta}"
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("📋 Simular Cópia da Resposta"):
                        st.toast("Resposta copiada para a área de transferência!", icon="✅")
                        
                except Exception as e:
                    st.error(f"Erro ao interpretar dados da IA: {e}")
        else:
            st.warning("⚠️ Por favor, forneça o conteúdo do e-mail antes de analisar.")
    else:
        st.info("Aguardando entrada de dados para iniciar a triagem.")

# --- 5. RODAPÉ ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.caption("AutoU Processo Seletivo | Desenvolvido por Ana Clara Nery e Mello Figueiredo")
