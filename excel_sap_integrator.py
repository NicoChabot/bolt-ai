import pandas as pd
from typing import Dict, Any, List, Optional
from Isap_integrator import SapIntegratorInterface
from materialCriteria import MaterialCriteria
from bolt_exception import BoltException


class ExcelSapIntegrator(SapIntegratorInterface):
    def __init__(self, material_file: str, sales_file: str):
        self.material_file = material_file
        self.sales_file = sales_file

    def load_materials(self) -> pd.DataFrame:
        try:
            df = pd.read_excel(self.material_file)
            df.columns = df.columns.str.strip().str.upper()
            return df
        except Exception as e:
            raise BoltException(f"Erro ao carregar materiais: {e}")

    def load_sales(self) -> pd.DataFrame:
        try:
            df = pd.read_excel(self.sales_file)
            df.columns = df.columns.str.strip().str.upper()
            return df
        except Exception as e:
            raise BoltException(f"Erro ao carregar vendas: {e}")

    def search_material_code(self, criteria: MaterialCriteria) -> Optional[str]:
        try:
            df = self.load_materials()
            required_columns = ["ESPESSURA", "LARGURA", "LAMINAÇÃO", "QUALIDADE", "MATERIAL"]

            for col in required_columns:
                if col not in df.columns:
                    raise BoltException(f"Coluna obrigatória '{col}' ausente no arquivo Excel.")

            filtro = (
                (df["ESPESSURA"].astype(str).str.contains(str(criteria.espessura), case=False, na=False)) &
                (df["LARGURA"].astype(str).str.contains(str(criteria.largura), case=False, na=False)) &
                (df["LAMINAÇÃO"].astype(str).str.contains(str(criteria.tipo_laminacao), case=False, na=False)) &
                (df["QUALIDADE"].astype(str).str.contains(str(criteria.qualidade), case=False, na=False))
            )

            resultados = df[filtro]
            if not resultados.empty:
                return str(resultados.iloc[0]["MATERIAL"])
            return None

        except Exception as e:
            raise BoltException(f"Erro na busca de material: {e}")

    def find_alternatives(self, criteria: MaterialCriteria) -> List[Dict[str, Any]]:
        try:
            df = self.load_materials()

            if "ESPESSURA" not in df.columns:
                raise BoltException("Coluna 'ESPESSURA' não encontrada.")

            esp_min = float(criteria.espessura) - 0.5 if criteria.espessura else 0
            esp_max = float(criteria.espessura) + 0.5 if criteria.espessura else 0

            similares = df[df["ESPESSURA"].astype(float).between(esp_min, esp_max, inclusive="both")]

            result = [{str(k): v for k, v in row.items()} for row in similares.to_dict(orient="records")]
            return result

        except Exception as e:
            raise BoltException(f"Erro ao buscar alternativas: {e}")

    def search_sales(self, code: str) -> List[Dict[str, Any]]:
        try:
            df = self.load_sales()

            if "MATERIAL" not in df.columns:
                raise BoltException("Coluna 'MATERIAL' não encontrada em vendas.")

            results = df[df["MATERIAL"].astype(str) == str(code)]

            result = [{str(k): v for k, v in row.items()} for row in results.to_dict(orient="records")]
            return result

        except Exception as e:
            raise BoltException(f"Erro ao buscar vendas: {e}")

    def add_material(self, material_data: Dict[str, Any]) -> None:
        try:
            df = self.load_materials()
            new_entry = pd.DataFrame([material_data])
            df = pd.concat([df, new_entry], ignore_index=True)
            df.to_excel(self.material_file, index=False)
        except Exception as e:
            raise BoltException(f"Erro ao adicionar novo material: {e}")

    def assign_material_to_group(self, material_code: str, group_name: str) -> None:
        try:
            df = self.load_materials()
            if "GRUPO" not in df.columns:
                df["GRUPO"] = ""

            df.loc[df["MATERIAL"] == material_code, "GRUPO"] = group_name
            df.to_excel(self.material_file, index=False)
        except Exception as e:
            raise BoltException(f"Erro ao atribuir material a grupo: {e}")
