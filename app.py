"""
DAX 2048 - Aprenda medidas DAX (Power BI) jogando
==================================================

Mesma mecânica do 2048: junte peças iguais para evoluir. Só que aqui cada
nível representa uma função DAX cada vez mais avançada — de SUM até
CALCULATE, FILTER, SUMX... até virar "Mestre DAX".

Layout pensado para caber inteiro na tela, sem rolagem:
- Sem cabeçalho/menu/rodapé padrão do Streamlit.
- Conteúdo educativo em `st.popover` (não ocupa espaço fixo na tela).
- Notificações de progresso em `st.toast` (flutuantes, não empurram o layout).

Execute com:
    streamlit run app.py
"""

from pathlib import Path

import streamlit as st
from streamlit_shortcuts import add_shortcuts

from game.constants import SIZE
from game.dax_content import DAX_LEVELS, EMPTY_TILE_COLORS, get_level
from game.logic import (
    new_grid,
    add_random_tile,
    move_left,
    move_right,
    move_up,
    move_down,
    grids_equal,
    can_move,
    has_won,
    max_value,
)

APP_DIR = Path(__file__).parent
CSS_PATH = APP_DIR / "static" / "style.css"

# Ordem de progressão (as chaves de DAX_LEVELS já estão em ordem crescente)
LEVEL_ORDER = sorted(DAX_LEVELS.keys())


# --------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# --------------------------------------------------------------------------
st.set_page_config(page_title="DAX 2048", page_icon="🧮", layout="centered")


def load_css(path: Path) -> None:
    with open(path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_css(CSS_PATH)


# --------------------------------------------------------------------------
# ESTADO DA SESSÃO
# --------------------------------------------------------------------------
def init_state() -> None:
    if "grid" not in st.session_state:
        st.session_state.grid = new_grid()
        st.session_state.score = 0
        st.session_state.best = 0
        st.session_state.game_over = False
        st.session_state.won_shown = False
        st.session_state.unlocked = {2, 4}  # peças iniciais já "vistas"


def _maybe_toast_new_level(old_grid, new_grid_) -> None:
    """Dispara um toast educativo na primeira vez que um nível é alcançado."""
    new_max = max_value(new_grid_)
    old_max = max_value(old_grid)
    if new_max > old_max and new_max not in st.session_state.unlocked:
        st.session_state.unlocked.add(new_max)
        level = get_level(new_max)
        st.toast(f"**{level['name']}** desbloqueada!\n\n{level['desc']}", icon="📊")


def do_move(move_fn) -> None:
    if st.session_state.game_over:
        return

    old_grid = [row[:] for row in st.session_state.grid]
    new_grid_, new_score = move_fn(st.session_state.grid, st.session_state.score)

    if not grids_equal(old_grid, new_grid_):
        _maybe_toast_new_level(old_grid, new_grid_)
        add_random_tile(new_grid_)
        st.session_state.grid = new_grid_
        st.session_state.score = new_score
        st.session_state.best = max(st.session_state.best, new_score)
        if not can_move(st.session_state.grid):
            st.session_state.game_over = True
            st.toast("Fim de jogo — sem mais movimentos possíveis.", icon="💀")


def restart() -> None:
    st.session_state.grid = new_grid()
    st.session_state.score = 0
    st.session_state.game_over = False
    st.session_state.won_shown = False
    st.session_state.unlocked = {2, 4}


# --------------------------------------------------------------------------
# COMPONENTES DE UI
# --------------------------------------------------------------------------
def render_header() -> None:
    title_col, score_col, best_col = st.columns([2, 1, 1])

    with title_col:
        st.markdown('<p class="game-title">🧮 DAX 2048</p>', unsafe_allow_html=True)
        st.markdown('<p class="game-subtitle">Funda medidas iguais e evolua no DAX</p>', unsafe_allow_html=True)
        if st.session_state.game_over:
            st.markdown('<span class="status-badge over">FIM DE JOGO</span>', unsafe_allow_html=True)
        elif has_won(st.session_state.grid):
            st.markdown('<span class="status-badge won">🏆 MESTRE DAX</span>', unsafe_allow_html=True)

    with score_col:
        st.markdown(
            f'<div class="score-box"><div class="label">Pontos</div>'
            f'<div class="value">{st.session_state.score}</div></div>',
            unsafe_allow_html=True,
        )

    with best_col:
        st.markdown(
            f'<div class="score-box"><div class="label">Recorde</div>'
            f'<div class="value">{st.session_state.best}</div></div>',
            unsafe_allow_html=True,
        )


def render_board() -> None:
    for row in st.session_state.grid:
        cols = st.columns(SIZE, gap="small")
        for col, value in zip(cols, row):
            if value == 0:
                bg, fg = EMPTY_TILE_COLORS
                text = ""
                font_size = "1rem"
            else:
                level = get_level(value)
                bg, fg = level["colors"]
                text = level["abbr"]
                font_size = "1.3rem" if len(text) <= 3 else ("1.05rem" if len(text) <= 4 else "0.85rem")
            col.markdown(
                f'<div class="tile" style="background:{bg}; color:{fg}; '
                f'font-size:{font_size};">{text}</div>',
                unsafe_allow_html=True,
            )


def render_controls() -> None:
    # Botões de movimento (⬆️⬅️➡️⬇️) ficam ocultos via CSS (.st-key-*): eles
    # continuam existindo no DOM só para o streamlit_shortcuts conseguir
    # "clicar" neles quando as setas do teclado são pressionadas. O jogador
    # só enxerga o botão de reiniciar.
    with st.container(key="dpad-hidden"):
        st.button("⬆️", key="up", on_click=do_move, args=(move_up,))
        st.button("⬅️", key="left", on_click=do_move, args=(move_left,))
        st.button("➡️", key="right", on_click=do_move, args=(move_right,))
        st.button("⬇️", key="down", on_click=do_move, args=(move_down,))

    _, c2, _ = st.columns(3)
    with c2:
        st.button("🔄", key="restart", on_click=restart, use_container_width=True)

    add_shortcuts(
        up="arrowup",
        down="arrowdown",
        left="arrowleft",
        right="arrowright",
        restart="r",
    )


def render_footer_popovers() -> None:
    """Conteúdo educativo em popovers: não ocupam espaço fixo na tela."""
    c1, c2 = st.columns(2)

    with c1:
        with st.popover("📖 Dicionário DAX", use_container_width=True):
            st.caption("Trilha de níveis do jogo, do mais simples ao mais avançado:")
            for value in LEVEL_ORDER:
                level = DAX_LEVELS[value]
                unlocked = value in st.session_state.unlocked
                icon = "✅" if unlocked else "🔒"
                st.markdown(f"**{icon} {level['abbr']} — {level['name']}**")
                st.caption(level["desc"])
                if level["example"]:
                    st.code(level["example"], language="dax")

    with c2:
        with st.popover("❓ Como jogar", use_container_width=True):
            st.markdown(
                "- Use as **setas do teclado** (↑ ↓ ← →) para mover as peças.\n"
                "- Peças com a **mesma função DAX** se fundem, virando o próximo nível.\n"
                "- Pressione **R** ou clique em 🔄 para reiniciar.\n"
                "- Chegue ao 🏆 **MESTRE DAX** (peça 2048) para vencer!"
            )


# --------------------------------------------------------------------------
# PONTO DE ENTRADA
# --------------------------------------------------------------------------
def main() -> None:
    init_state()
    render_header()
    render_board()
    render_controls()
    render_footer_popovers()


if __name__ == "__main__":
    main()
