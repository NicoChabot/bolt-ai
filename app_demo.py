import streamlit as st
from bolt_agent import BoltAgent
from excel_sap_integrator import ExcelSapIntegrator
import os

st.set_page_config(page_title="Bolt AI Agent", page_icon="🤖", layout="centered")

BASE_DIR = os.path.dirname(__file__)

MATERIAL_FILE = os.path.join(BASE_DIR, "bolt-ai", "AGENTE_BaseCaracteristicasDosMateriais (1).XLSX")
SALES_FILE = os.path.join(BASE_DIR, "bolt-ai", "AGENTE_BaseFaturamento (1).XLSX")

if not os.path.exists(MATERIAL_FILE):
    st.error(f"❌ Arquivo de materiais não encontrado em: {MATERIAL_FILE}")
    st.stop()

if not os.path.exists(SALES_FILE):
    st.error(f"❌ Arquivo de faturamento não encontrado em: {SALES_FILE}")
    st.stop()

sap_integrator = ExcelSapIntegrator(
    material_file=MATERIAL_FILE,
    sales_file=SALES_FILE
)
bot = BoltAgent(sap_integrator)

st.markdown(
    """
    <style>
    .chat-bubble {
        padding: 0.8em 1.2em;
        border-radius: 12px;
        margin-bottom: 0.6em;
        max-width: 85%;
    }
    .bot {
        background-color: #f0f2f6;
        border-left: 4px solid #4a90e2;
    }
    .user {
        background-color: #DCF8C6;
        margin-left: auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

col1, col2 = st.columns([0.15, 0.85])
with col1:
    st.image("D:\\BoltAI\\bolt.png", width=90)
with col2:
    st.markdown("## 🤖 Olá! Eu sou o assistente Bolt AI")
    st.markdown("Como posso te ajudar hoje? Escolha uma das opções abaixo 👇")

opcao = st.selectbox(
    "Selecione uma ação:",
    ["🔍 Buscar Material", "➕ Cadastrar Novo Material", "🧩 Agrupar Materiais"]
)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def add_message(sender: str, message: str):
    bubble_class = "user" if sender == "Você" else "bot"
    st.markdown(f"<div class='chat-bubble {bubble_class}'><b>{sender}:</b><br>{message}</div>", unsafe_allow_html=True)

for msg in st.session_state.chat_history:
    add_message(msg["sender"], msg["message"])
if opcao == "🔍 Buscar Material":
    user_input = st.text_input("Digite os critérios para busca de material:")
    if st.button("Pesquisar"):
        if user_input.strip():
            try:
                resultado = bot.process_prompt(user_input)
                st.session_state.chat_history.append({"sender": "Você", "message": user_input})
                st.session_state.chat_history.append({"sender": "Bolt AI", "message": str(resultado)})
                st.experimental_rerun()
            except Exception as e:
                st.error(f"⚠️ Erro na busca: {str(e)}")

elif opcao == "➕ Cadastrar Novo Material":
    st.subheader("Cadastro de Novo Material")
    new_data = {
        "Código": st.text_input("Código do Material"),
        "Setor": st.selectbox("Setor de Atividade", ["JIT", "SERV", "DIST"]),
        "Tipo": st.text_input("Tipo de Produto"),
        "Qualidade": st.text_input("Qualidade"),
        "Laminação": st.text_input("Laminação"),
        "Espessura": st.text_input("Espessura"),
        "Largura": st.text_input("Largura"),
        "Comprimento": st.text_input("Comprimento"),
    }

    if st.button("Salvar Material"):
        try:
            bot.sap_integrator.add_material(new_data)
            st.success("✅ Material cadastrado com sucesso!")
        except Exception as e:
            st.error(f"⚠️ Erro ao cadastrar: {str(e)}")


elif opcao == "🧩 Agrupar Materiais":
    st.subheader("Agrupar Materiais em um Grupo")
    group_name = st.text_input("Nome do Grupo")
    material_codes = st.text_area("Códigos dos Materiais (separados por vírgula)")
    if st.button("Criar Grupo"):
        try:
            codes = [code.strip() for code in material_codes.split(",") if code.strip()]
            bot.sap_integrator.assign_material_to_group(group_name, codes)
            st.success(f"✅ Grupo '{group_name}' criado com {len(codes)} materiais.")
        except Exception as e:
            st.error(f"⚠️ Erro ao criar grupo: {str(e)}")
