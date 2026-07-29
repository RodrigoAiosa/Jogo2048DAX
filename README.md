# 🧮 DAX 2048 — Aprenda medidas DAX jogando

Um jogo educativo com a mesma mecânica do **2048** clássico, mas em vez de
números, cada nível de peça representa uma **função DAX** (Power BI) cada
vez mais avançada. Ao fundir duas peças iguais, você "evolui" para o
próximo conceito da trilha de aprendizado.

## 🎯 Trilha de níveis (do básico ao avançado)

| Peça | Função DAX      | O que faz                                             |
|------|-----------------|--------------------------------------------------------|
| SUM  | `SUM`           | Soma valores de uma coluna                             |
| AVG  | `AVERAGE`       | Calcula a média                                        |
| CNT  | `COUNTROWS`     | Conta linhas de uma tabela                             |
| DCNT | `DISTINCTCOUNT` | Conta valores únicos                                   |
| CALC | `CALCULATE`     | Recalcula em novo contexto de filtro (a função-chave!) |
| FILT | `FILTER`        | Retorna uma tabela filtrada linha a linha              |
| ALL  | `ALL`           | Remove filtros — útil para % do total                  |
| SUMX | `SUMX`          | Soma iterando linha a linha (função "X")               |
| REL  | `RELATED`       | Busca valor em tabela relacionada                       |
| VAR  | `VAR / RETURN`  | Organiza cálculos complexos com variáveis               |
| 🏆   | **Mestre DAX**  | Você concluiu a trilha!                                 |

Cada função tem uma explicação curta e um exemplo de sintaxe real, acessíveis
a qualquer momento pelo botão **📖 Dicionário DAX**.

## 📁 Estrutura do projeto

```
dax2048-streamlit/
├── app.py                     # Camada de UI (Streamlit)
├── game/
│   ├── __init__.py
│   ├── constants.py            # SIZE, chance de peça nova, valor de vitória
│   ├── logic.py                 # Lógica pura de fusão (idêntica ao 2048)
│   └── dax_content.py           # Mapeamento nível -> função DAX (nome, descrição, exemplo, cor)
├── static/
│   └── style.css                # Layout compacto (cabe na tela sem rolagem)
├── tests/
│   ├── __init__.py
│   ├── test_logic.py             # Testes da mecânica de fusão
│   └── test_dax_content.py       # Testes do conteúdo educativo
├── .streamlit/
│   └── config.toml               # Tema e configuração do servidor
├── requirements.txt
├── requirements-dev.txt
├── .gitignore
└── README.md
```

A lógica de fusão (`game/logic.py`) é **idêntica** à do 2048 original —
só o conteúdo exibido nas peças muda (`game/dax_content.py`). Isso deixa
fácil criar novas variações temáticas (ex: SQL, Excel, Python) reaproveitando
a mesma engine.

## 🚀 Como rodar

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## 🎮 Como jogar

- Use as **setas do teclado** (↑ ↓ ← →) ou os botões na tela para mover as peças.
- Peças com a **mesma função DAX** se fundem, virando o próximo nível da trilha.
- Pressione **R** ou clique em 🔄 para reiniciar.
- Abra **📖 Dicionário DAX** a qualquer momento para ver a explicação e o
  exemplo de sintaxe de cada função — inclusive das que você ainda não
  desbloqueou (aparecem com 🔒).
- Ao alcançar um nível pela primeira vez, uma notificação flutuante (toast)
  explica rapidamente a função DAX daquela peça.
- Chegue à peça 🏆 (2048) para se tornar "Mestre DAX"!

## 🖥️ Por que cabe tudo na tela

O layout foi desenhado para não precisar de rolagem:
- Cabeçalho, menu e rodapé padrão do Streamlit são ocultados via CSS.
- Espaçamentos e botões são compactos (`static/style.css`).
- O conteúdo educativo (dicionário e instruções) fica em **popovers**
  (`st.popover`), que abrem por cima do conteúdo sem aumentar a altura da
  página — e as notificações de progresso usam **toasts** (`st.toast`),
  que flutuam e desaparecem sozinhos, sem empurrar o layout.

## ✅ Rodando os testes

```bash
pip install -r requirements-dev.txt
pytest
```

## 🧱 Boas práticas aplicadas

- Separação entre lógica de jogo, conteúdo educativo e camada de UI.
- CSS externo, sem estilos inline espalhados pelo Python.
- Testes unitários cobrindo tanto a mecânica quanto o conteúdo (todas as
  peças têm nome, descrição e exemplo; todas são potências de 2 válidas).
- Dependências com versão fixada (`requirements.txt`) para builds reprodutíveis.

## 📌 Possíveis melhorias futuras

- Quiz obrigatório antes da fusão (responder corretamente para "evoluir").
- Progresso persistente entre sessões (histórico de funções dominadas).
- Trilhas alternativas (ex: SQL 2048, Excel 2048) reaproveitando `game/logic.py`.

## 📄 Licença

Uso livre para fins de estudo e aprendizado.
