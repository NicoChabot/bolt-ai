import streamlit as st
from pathlib import Path
from prompt_parser import PromptParser
from bolt_agent import BoltAgent
from excel_sap_integrator import ExcelSapIntegrator
from bolt_exception import BoltException
from materialCriteria import MaterialCriteria

MATERIAL_FILE = r"AGENTE_BaseCaracteristicasDosMateriais (1).XLSX"
SALES_FILE = r"AGENTE_BaseCaracteristicasDosMateriais (1).XLSX"
AGENT_IMAGE = Path(r"bolt.png")

st.set_page_config(page_title="Bolt AI Agent", page_icon="🤖", layout="centered")
st.title("Agente Bolt 🤖")

if AGENT_IMAGE.exists():
    st.image(str(AGENT_IMAGE), width=90)
else:
    st.info("Imagem do agente não encontrada. Continuando sem avatar.")

if not Path(MATERIAL_FILE).exists() or not Path(SALES_FILE).exists():
    st.error("Arquivos base (materiais / faturamento) não encontrados. Ajuste os caminhos no topo do app.")
    st.stop()

parser = PromptParser()
sap_integrator = ExcelSapIntegrator(material_file=MATERIAL_FILE, sales_file=SALES_FILE)
agent = BoltAgent(parser, sap_integrator)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "bot", "content": "Olá! Sou o Agente Bolt. Escolha: 1) Pesquisar material 2) Cadastrar 3) Agrupar 4) Pesquisar venda"}
    ]
    st.session_state.step = "menu"

def append(role: str, text: str):
    st.session_state.messages.append({"role": role, "content": text})

for m in st.session_state.messages:
    if m["role"] == "bot":
        st.markdown(f"**Bot:** {m['content']}")
    else:
        st.markdown(f"**Você:** {m['content']}")

user_input = st.text_input("Digite sua opção ou mensagem:")

if st.button("Enviar") and user_input.strip():
    append("user", user_input)
    step = st.session_state.step

    try:
        if step == "menu":
            opt = user_input.strip().lower()
            if opt in ["1", "pesquisar material", "buscar material"]:
                append("bot", "OK. Informe os dados (ex: Qualidade: SAE1006, Espessura:0.6, Largura:1200, Laminação:LF)")
                st.session_state.step = "pesquisa_material"
            elif opt in ["2", "cadastrar", "cadastrar material"]:
                append("bot", "Ok. Informe novo material no formato JSON ou key:value separados por vírgula.")
                st.session_state.step = "cadastro"
            elif opt in ["3", "agrupar", "agrupar material"]:
                append("bot", "Informe: codigo, nome_do_grupo")
                st.session_state.step = "agrupar"
            elif opt in ["4", "pesquisar venda", "venda"]:
                append("bot", "Informe o código do material para buscar vendas.")
                st.session_state.step = "venda"
            else:
                append("bot", "Opção inválida. Escolha 1,2,3 ou 4.")
        elif step == "pesquisa_material":
            result = agent.process_prompt(user_input)
            if result.get("status") == "found_material":
                append("bot", f"Código encontrado: {result.get('code')}")
            elif result.get("status") == "alternatives":
                append("bot", f"Alternativas encontradas: {len(result.get('alternatives',[]))}")
            else:
                append("bot", result.get("message", "Nenhum resultado."))
            st.session_state.step = "menu"
        elif step == "cadastro":
            raw = user_input.strip()
            try:
                if raw.startswith("{") and raw.endswith("}"):
                    import json
                    material_data = json.loads(raw)
                else:
                    material_data = {}
                    for pair in raw.split(","):
                        if ":" in pair:
                            k, v = pair.split(":", 1)
                        elif "=" in pair:
                            k, v = pair.split("=", 1)
                        else:
                            continue
                        material_data[k.strip().upper()] = v.strip()
                new_code = sap_integrator.add_material(material_data)
                append("bot", f"Material cadastrado com código: {new_code}")
            except Exception as e:
                append("bot", f"Erro ao cadastrar: {e}")
            st.session_state.step = "menu"
        elif step == "agrupar":
            parts = [p.strip() for p in user_input.split(",")]
            if len(parts) != 2:
                append("bot", "Formato inválido. Use: codigo, grupo")
            else:
                codigo, grupo = parts
                try:
                    sap_integrator.assign_material_to_group(codigo, grupo)
                    append("bot", f"Material {codigo} adicionado ao grupo {grupo}.")
                except Exception as e:
                    append("bot", f"Erro: {e}")
            st.session_state.step = "menu"
        elif step == "venda":
            codigo = "".join(ch for ch in user_input if ch.isdigit())
            try:
                vendas = sap_integrator.search_sales(codigo)
                if not vendas:
                    append("bot", f"Nenhuma venda encontrada para {codigo}.")
                else:
                    append("bot", f"{len(vendas)} registros encontrados. Você pode baixá-los pelo botão abaixo.")
                    st.session_state["last_sales"] = vendas
            except Exception as e:
                append("bot", f"Erro ao buscar vendas: {e}")
            st.session_state.step = "menu"
    except BoltException as be:
        append("bot", f"Erro Bolt: {be}")
        st.session_state.step = "menu"
    except Exception as e:
        append("bot", f"Erro inesperado: {e}")
        st.session_state.step = "menu"

if "last_sales" in st.session_state:
    import pandas as pd, io
    df = pd.DataFrame(st.session_state["last_sales"])
    st.dataframe(df)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Baixar CSV de vendas", data=csv, file_name="vendas.csv", mime="text/csv")
