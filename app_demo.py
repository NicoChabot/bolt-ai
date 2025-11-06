import streamlit as st
from prompt_parser import PromptParser
from bolt_agent import BoltAgent
from excel_sap_integrator import ExcelSapIntegrator
from bolt_exception import BoltException
import base64
import os

# ===========================
# Configuração da página
# ===========================
st.set_page_config(page_title="Agente Bolt", page_icon="🤖", layout="wide")

# ===========================
# Cabeçalho com imagem e título
# ===========================
bolt_image_path = "bolt.png"  

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

if os.path.exists(bolt_image_path):
    bolt_image_base64 = get_base64_image(bolt_image_path)
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 15px;">
            <img src="data:image/png;base64,{bolt_image_base64}" width="70" style="border-radius: 10px;">
            <h1 style="margin: 0;">Agente Bolt - Sistema de Materiais</h1>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown("## 🤖 Agente Bolt - Sistema de Materiais")

# ===========================
# Estado do chat
# ===========================
if "state" not in st.session_state:
    st.session_state.state = "menu"
if "choice" not in st.session_state:
    st.session_state.choice = None

# ===========================
# Inicialização do agente
# ===========================
integrator = ExcelSapIntegrator(
    material_file="AGENTE_BaseCaracteristicasDosMateriais (1).XLSX",
    sales_file="AGENTE_BaseFaturamento (1).XLSX"
)
parser = PromptParser()
agent = BoltAgent(parser, integrator)

# ===========================
# Interface do agente (chat)
# ===========================
st.markdown("**Bolt:** Olá! Sou o Agente Bolt. Escolha uma opção:")
st.markdown("1️⃣ Pesquisar material  \n2️⃣ Cadastrar novo material  \n3️⃣ Agrupar material  \n4️⃣ Pesquisar venda")

user_input = st.chat_input("Digite sua opção ou mensagem:", key="user_input", disabled=False)

if user_input:
    try:
        # MENU PRINCIPAL
        if st.session_state.state == "menu":
            if user_input.strip() in ["1", "2", "3", "4"]:
                st.session_state.choice = user_input.strip()
                if user_input.strip() == "1":
                    st.session_state.state = "search"
                    st.markdown("**Bot:** OK. Informe os dados (ex: Qualidade: SAE1006, Espessura:0.6, Largura:1200, Laminação:LF)**")
                elif user_input.strip() == "2":
                    st.session_state.state = "add"
                    st.markdown("**Bot:** Informe os dados do novo material (JSON ou texto estruturado).")
                elif user_input.strip() == "3":
                    st.session_state.state = "group"
                    st.markdown("**Bot:** Informe o código do material e o grupo desejado.")
                elif user_input.strip() == "4":
                    st.session_state.state = "sales"
                    st.markdown("**Bot:** Informe o código do material para buscar histórico de vendas.")
            else:
                st.markdown("**Bot:** Opção inválida. Escolha 1, 2, 3 ou 4.")

        # PESQUISAR MATERIAL
        elif st.session_state.state == "search":
            response = agent.process_prompt(user_input)
            if response["status"] == "found_material":
                st.success(f"**Bot:** Código encontrado: {response['code']}")
                st.session_state.state = "menu"
            elif response["status"] == "alternatives":
                st.warning("**Bot:** Nenhum material exato encontrado. Alternativas próximas:")
                st.dataframe(response["alternatives"])
                st.session_state.state = "menu"
            elif response["status"] == "not_found":
                st.error("**Bot:** Material não encontrado.")
                st.session_state.state = "menu"
            else:
                st.error(f"**Bot:** {response['message']}")
                st.session_state.state = "menu"

        # CADASTRAR MATERIAL
        elif st.session_state.state == "add":
            st.success("**Bot:** Novo material adicionado com sucesso!")
            st.session_state.state = "menu"

        # AGRUPAR MATERIAL
        elif st.session_state.state == "group":
            st.success("**Bot:** Material atribuído ao grupo com sucesso!")
            st.session_state.state = "menu"

        # PESQUISAR VENDA
        elif st.session_state.state == "sales":
            response = agent.process_prompt(f"oportunidade de venda código {user_input}")
            if response["status"] == "sales_opportunity":
                st.markdown(response["response"])
            else:
                st.error(response["message"])
            st.session_state.state = "menu"

    except BoltException as e:
        st.error(f"**Erro:** {e}")
        st.session_state.state = "menu"
    except Exception as e:
        st.error(f"**Erro inesperado:** {e}")
        st.session_state.state = "menu"
