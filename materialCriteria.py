from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class MaterialCriteria:
    setor_atividade: Optional[str] = None
    tipo_produto: Optional[str] = None
    qualidade: Optional[str] = None
    tipo_laminacao: Optional[str] = None
    espessura: Optional[float] = None
    largura: Optional[float] = None
    comprimento: Optional[float] = None
    base_maior: Optional[float] = None
    base_menor: Optional[float] = None

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "MaterialCriteria":
        def parse_float(s: Optional[str]) -> Optional[float]:
            if s is None or s == "":
                return None
            try:
                s2 = str(s).strip().rstrip(".,").replace(",", ".").replace("mm", "")
                return float(s2)
            except Exception:
                return None

        setor = (data.get("setor_atividade") or data.get("setor") or "").upper() or None
        tipo_produto = (data.get("tipo_produto") or data.get("tipo") or "").upper() or None
        qualidade = (data.get("qualidade") or "").strip() or None

        tipo_laminacao = (data.get("tipo_laminacao") or data.get("laminacao") or "").strip() or None
        if tipo_laminacao:
            tipo_laminacao = tipo_laminacao.upper()

        espessura = parse_float(data.get("espessura") or data.get("esp"))
        largura = parse_float(data.get("largura") or data.get("larg"))
        comprimento = parse_float(data.get("comprimento") or data.get("comp"))
        base_maior = parse_float(data.get("base_maior") or data.get("baseMaior"))
        base_menor = parse_float(data.get("base_menor") or data.get("baseMenor"))

        return cls(
            setor_atividade=setor,
            tipo_produto=tipo_produto,
            qualidade=(qualidade.replace(" ", "").replace("-", "").upper() if qualidade else None),
            tipo_laminacao=tipo_laminacao,
            espessura=espessura,
            largura=largura,
            comprimento=comprimento,
            base_maior=base_maior,
            base_menor=base_menor
        )
