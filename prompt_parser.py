import re
from materialCriteria import MaterialCriteria
from bolt_exception import BoltException

class PromptParser:
    def __init__(self):
     
        self.patterns = {
            'setor_atividade': r'setor:\s*(\w+)',
            'tipo_produto': r'tipo produto:\s*([\w\s]+)',
            'qualidade': r'qualidade:\s*([\w\s-]+)',
            'laminacao': r'laminação:\s*(\w+)',
            'espessura': r'espessura:\s*([\d.,]+(?:mm)?)',
            'largura': r'largura:\s*([\d.,]+)',
            'comprimento': r'comprimento:\s*([\d.,]+)',
            'base_maior': r'base maior:\s*([\d.,]+)',
            'base_menor': r'base menor:\s*([\d.,]+)',
        }

    def parse(self, prompt: str) -> MaterialCriteria:
        """
        Parseia o prompt do usuário para extrair critérios.
        Exemplo de prompt: "Setor: JIT, Tipo Produto: CHAPA, Qualidade: SAE-1006, Laminação: LF, Espessura: 0.6, Largura: 1200, Comprimento: 3000"
        """
        criteria_dict = {}
        for key, pattern in self.patterns.items():
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                criteria_dict[key] = match.group(1).strip()
        # Verifica obrigatórios
        if 'espessura' not in criteria_dict or 'largura' not in criteria_dict:
            raise BoltException("Espessura e Largura são obrigatórios.")
        return MaterialCriteria.from_dict(criteria_dict)