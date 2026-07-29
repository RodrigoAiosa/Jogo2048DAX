"""
Conteúdo educativo do "DAX 2048".

Cada valor de peça (potência de 2, igual ao 2048 original) representa um
nível de conhecimento em medidas DAX (Power BI). Ao fundir duas peças
iguais, o jogador "evolui" para o próximo conceito da trilha.

`abbr`   -> texto curto exibido dentro da peça no tabuleiro
`name`   -> nome completo da função/conceito
`desc`   -> explicação curta (1-2 linhas)
`example`-> exemplo de sintaxe DAX
`colors` -> (cor de fundo, cor do texto) da peça
"""

from typing import Dict, Tuple, TypedDict


class DaxLevel(TypedDict):
    abbr: str
    name: str
    desc: str
    example: str
    colors: Tuple[str, str]


DAX_LEVELS: Dict[int, DaxLevel] = {
    2: {
        "abbr": "SUM",
        "name": "SUM",
        "desc": "Soma todos os valores de uma coluna numérica.",
        "example": "Total Vendas = SUM(Vendas[Valor])",
        "colors": ("#eee4da", "#776e65"),
    },
    4: {
        "abbr": "AVG",
        "name": "AVERAGE",
        "desc": "Calcula a média aritmética dos valores de uma coluna.",
        "example": "Ticket Médio = AVERAGE(Vendas[Valor])",
        "colors": ("#ede0c8", "#776e65"),
    },
    8: {
        "abbr": "CNT",
        "name": "COUNTROWS",
        "desc": "Conta o número de linhas de uma tabela ou tabela filtrada.",
        "example": "Qtd Pedidos = COUNTROWS(Vendas)",
        "colors": ("#f2b179", "#f9f6f2"),
    },
    16: {
        "abbr": "DCNT",
        "name": "DISTINCTCOUNT",
        "desc": "Conta valores distintos (únicos) de uma coluna.",
        "example": "Clientes Únicos = DISTINCTCOUNT(Vendas[ClienteID])",
        "colors": ("#f59563", "#f9f6f2"),
    },
    32: {
        "abbr": "CALC",
        "name": "CALCULATE",
        "desc": "Recalcula uma medida em um novo contexto de filtro. A função mais importante do DAX.",
        "example": "Vendas 2024 = CALCULATE([Total Vendas], Calendario[Ano] = 2024)",
        "colors": ("#f67c5f", "#f9f6f2"),
    },
    64: {
        "abbr": "FILT",
        "name": "FILTER",
        "desc": "Retorna uma tabela filtrada linha a linha, usada dentro de CALCULATE.",
        "example": "Vendas Premium = CALCULATE([Total Vendas], FILTER(Vendas, Vendas[Valor] > 1000))",
        "colors": ("#f65e3b", "#f9f6f2"),
    },
    128: {
        "abbr": "ALL",
        "name": "ALL",
        "desc": "Remove filtros de uma coluna/tabela — essencial para calcular % do total.",
        "example": "% do Total = DIVIDE([Total Vendas], CALCULATE([Total Vendas], ALL(Vendas)))",
        "colors": ("#edcf72", "#f9f6f2"),
    },
    256: {
        "abbr": "SUMX",
        "name": "SUMX",
        "desc": "Itera linha a linha e soma uma expressão calculada (função 'X' / iteradora).",
        "example": "Receita = SUMX(Vendas, Vendas[Qtd] * Vendas[Preco])",
        "colors": ("#edcc61", "#f9f6f2"),
    },
    512: {
        "abbr": "REL",
        "name": "RELATED",
        "desc": "Busca um valor em uma tabela relacionada (lado 'um' do relacionamento).",
        "example": "Categoria = RELATED(Produtos[Categoria])",
        "colors": ("#edc850", "#f9f6f2"),
    },
    1024: {
        "abbr": "VAR",
        "name": "VAR / RETURN",
        "desc": "Cria variáveis para organizar e otimizar cálculos DAX complexos.",
        "example": "VAR TotalAtual = [Total Vendas]\nRETURN TotalAtual * 1.1",
        "colors": ("#edc53f", "#f9f6f2"),
    },
    2048: {
        "abbr": "🏆",
        "name": "MESTRE DAX",
        "desc": "Parabéns! Você percorreu do SUM básico até conceitos avançados de medidas DAX.",
        "example": "Continue praticando no Power BI Desktop 🚀",
        "colors": ("#edc22e", "#f9f6f2"),
    },
}

DEFAULT_TILE_COLORS: Tuple[str, str] = ("#3c3a32", "#f9f6f2")
EMPTY_TILE_COLORS: Tuple[str, str] = ("#cdc1b4", "#cdc1b4")


def get_level(value: int) -> DaxLevel:
    """Retorna o conteúdo educativo do nível; usa cor padrão para valores acima do mapa."""
    if value in DAX_LEVELS:
        return DAX_LEVELS[value]
    return {
        "abbr": str(value),
        "name": f"Nível {value}",
        "desc": "Nível avançado sem função específica associada.",
        "example": "",
        "colors": DEFAULT_TILE_COLORS,
    }
