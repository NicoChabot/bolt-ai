import pandas as pd
from typing import List, Dict, Any, Optional, cast
from bolt_exception import BoltException
from materialCriteria import MaterialCriteria
from Isap_integrator import SapIntegratorInterface
import os


class ExcelSapIntegrator(SapIntegratorInterface):
    """Integração com planilhas Excel para busca e gestão de materiais."""

    def __init__(self, material_file: str, sales_file: str):
        if not os.path.exists(material_file):
            raise BoltException(f"Arquivo de materiais não encontrado: {material_file}")
        if not os.path.exists(sales_file):
            raise BoltException(f"Arquivo de faturamento não encontrado: {sales_file}")

        self.material_file: str = material_file
        self.sales_file: str = sales_file

    def _read_materials(self) -> pd.DataFrame:
        return pd.read_excel(self.material_file)

    def _read_sales(self) -> pd.DataFrame:
        return pd.read_excel(self.sales_file)

    def search_material_code(self, criteria: MaterialCriteria) -> Optional[str]:
        df = self._read_materials()

        if criteria.espessura is None:
            raise BoltException("Espessura é obrigatória para a busca de materiais.")

        filtered = df[df["ESPESSURA"] == criteria.espessura]

        if criteria.qualidade:
            filtered = filtered[
                filtered["QUALIDADE"].astype(str).str.contains(criteria.qualidade, case=False, na=False)
            ]
        if criteria.largura is not None:
            filtered = filtered[filtered["LARGURA"] == criteria.largura]
        if criteria.comprimento is not None:
            filtered = filtered[filtered["COMPRIMENTO"] == criteria.comprimento]
        if criteria.tipo_laminacao:
            filtered = filtered[
                filtered["LAMINACAO"].astype(str).str.contains(criteria.tipo_laminacao, case=False, na=False)
            ]

        if filtered.empty:
            return None

        return str(filtered.iloc[0]["COD_MATERIAL"])

    def find_alternatives(self, criteria: MaterialCriteria) -> List[Dict[str, Any]]:
        df = self._read_materials()

        if criteria.espessura is None:
            raise BoltException("Espessura é obrigatória para buscar alternativas.")

        lower_bound = float(criteria.espessura) - 0.5
        upper_bound = float(criteria.espessura) + 0.5

        filtered = df[(df["ESPESSURA"] >= lower_bound) & (df["ESPESSURA"] <= upper_bound)]
        return cast(List[Dict[str, Any]], filtered.to_dict(orient="records"))

    def search_sales(self, code: str) -> List[Dict[str, Any]]:
        df = self._read_sales()

        try:
            code_int = int(code)
            filtered = df[df["COD_MATERIAL"] == code_int]
        except Exception:
            filtered = df[df["COD_MATERIAL"].astype(str) == str(code)]

        return cast(List[Dict[str, Any]], filtered.to_dict(orient="records"))

    def add_material(self, material_data: Dict[str, Any]) -> Optional[str]:
        """
        Adiciona um novo material ao arquivo de materiais.
        Retorna o novo código gerado (str) ou None em caso de falha.
        """
        df = self._read_materials()

        try:
            max_code = int(df["COD_MATERIAL"].max())
            novo_codigo = str(max_code + 1)
        except Exception:
            novo_codigo = "1"

        material_data["COD_MATERIAL"] = novo_codigo

        df = pd.concat([df, pd.DataFrame([material_data])], ignore_index=True)
        df.to_excel(self.material_file, index=False)
        return novo_codigo

    def assign_material_to_group(self, material_code: str, group_name: str) -> None:
        """
        Atribui o material ao grupo. Retorna None (conforme interface).
        """
        df = self._read_materials()

        if "GRUPO" not in df.columns:
            df["GRUPO"] = None

        mask = df["COD_MATERIAL"].astype(str) == str(material_code)
        if not mask.any():
            raise BoltException(f"Material {material_code} não encontrado na base.")

        df.loc[mask, "GRUPO"] = group_name
        df.to_excel(self.material_file, index=False)
        return None
