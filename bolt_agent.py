import re
from typing import Dict, Any, Optional
import pandas as pd
from prompt_parser import PromptParser
from Isap_integrator import SapIntegratorInterface
from materialCriteria import MaterialCriteria
from bolt_exception import BoltException


class BoltAgent:
    def __init__(self, parser: PromptParser, sap_integrator: SapIntegratorInterface):
        self.parser = parser
        self.sap_integrator = sap_integrator

    def process_prompt(self, prompt: str) -> Dict[str, Any]:
        try:
            prompt_lower = (prompt or "").lower().strip()

            if "oportunidade de venda" in prompt_lower or "venda" in prompt_lower:
                match = re.search(r'(\d{4,})', prompt)
                if not match:
                    raise BoltException("Código de material não identificado na solicitação de venda.")
                code = match.group(1)
                sales = self.sap_integrator.search_sales(code)
                if not sales:
                    return {"status": "no_sales", "message": f"Nenhuma venda encontrada para {code}"}
                df = pd.DataFrame(sales)
                total_peso = df["PESO"].sum() if "PESO" in df.columns else 0
                total_valor = df["VALOR_LIQ"].sum() if "VALOR_LIQ" in df.columns else 0
                response = f"Histórico de vendas (Total Peso: {total_peso} TN, Total Valor: {total_valor}):\n"
                for sale in sales:
                    response += f"- Cliente: {sale.get('DESC_CLIENTE','N/A')}, Peso: {sale.get('PESO',0)}, Data: {sale.get('DATA_FAT','')}\n"
                return {"status": "sales_opportunity", "code": code, "sales": sales, "response": response}

            criteria = self.parser.parse(prompt)
            if not isinstance(criteria, MaterialCriteria):
                raise BoltException("Critérios inválidos.")

            code = self.sap_integrator.search_material_code(criteria)
            if code:
                return {"status": "found_material", "code": code, "criteria": criteria}

            alternatives = self.sap_integrator.find_alternatives(criteria)
            if alternatives:
                return {"status": "alternatives", "alternatives": alternatives, "criteria": criteria}

            return {"status": "not_found", "message": "Material não encontrado. Deseja criar um novo?"}

        except ValueError as ve:
            return {"status": "error", "message": f"Erro de validação: {ve}"}
        except BoltException as be:
            return {"status": "error", "message": f"Erro: {be}"}
        except Exception as e:
            return {"status": "error", "message": f"Erro inesperado: {e}"}
