from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class SapIntegratorInterface(ABC):
    """Interface base para integradores (Excel, API, etc.)."""

    @abstractmethod
    def search_material_code(self, criteria) -> Optional[str]:
        """Busca um código de material existente baseado nos critérios."""
        raise NotImplementedError

    @abstractmethod
    def find_alternatives(self, criteria) -> List[Dict[str, Any]]:
        """Encontra alternativas para critérios não encontrados."""
        raise NotImplementedError

    @abstractmethod
    def search_sales(self, code: str) -> List[Dict[str, Any]]:
        """Busca histórico de vendas para um código."""
        raise NotImplementedError

    def add_material(self, material_data: dict) -> Optional[str]:
        """Adiciona um material. Pode retornar o código criado ou None."""
        raise NotImplementedError

    def assign_material_to_group(self, material_code: str, group_name: str) -> None:
        """Associa um material a um grupo."""
        raise NotImplementedError
