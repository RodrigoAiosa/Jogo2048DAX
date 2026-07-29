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

import json
import random
from datetime import date
from pathlib import Path

import streamlit as st
from streamlit_shortcuts import add_shortcuts

from game.constants import BOARD_SIZES, SIZE
from game.dax_content import DAX_LEVELS, EMPTY_TILE_COLORS, get_level
from game.logic import (
    new_grid,
    add_random_tile,
    move_left,
    move_right,
    move_up,
    move_down,
    move_left_mask,
    move_right_mask,
    move_up_mask,
    move_down_mask,
    grids_equal,
    can_move,
    has_won,
    max_value,
)

APP_DIR = Path(__file__).parent
CSS_PATH = APP_DIR / "static" / "style.css"
HIGHSCORE_PATH = APP_DIR / "highscore.json"

# Ordem de progressão (as chaves de DAX_LEVELS já estão em ordem crescente)
LEVEL_ORDER = sorted(DAX_LEVELS.keys())

# Cada direção sabe seu par (função de movimento, função que rastreia fusões)
MOVES = {
    "up": (move_up, move_up_mask),
    "down": (move_down, move_down_mask),
    "left": (move_left, move_left_mask),
    "right": (move_right, move_right_mask),
}


# --------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# --------------------------------------------------------------------------
st.set_page_config(page_title="DAX 2048", page_icon="🧮", layout="centered")


def load_css(path: Path) -> None:
    with open(path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_css(CSS_PATH)


# --------------------------------------------------------------------------
# RECORDE PERSISTIDO EM DISCO (sobrevive a reinícios do app, não só da sessão)
# --------------------------------------------------------------------------
def load_highscores() -> dict:
    try:
        return json.loads(HIGHSCORE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_highscores(scores: dict) -> None:
    try:
        HIGHSCORE_PATH.write_text(json.dumps(scores), encoding="utf-8")
    except Exception:
        pass


# --------------------------------------------------------------------------
# ESTADO DA SESSÃO
# --------------------------------------------------------------------------
def _new_board(size: int) -> None:
    st.session_state.size = size
    st.session_state.grid = new_grid(size, st.session_state.rng)
    st.session_state.score = 0
    st.session_state.moves = 0
    st.session_state.game_over = False
    st.session_state.won_shown = False
    st.session_state.unlocked = {2, 4}
    st.session_state.merged_mask = None
    st.session_state.undo_snapshot = None
    scores = load_highscores()
    st.session_state.best = scores.get(str(size), 0)


def init_state() -> None:
    if "grid" not in st.session_state:
        st.session_state.rng = random.Random()
        st.session_state.daily_mode = False
        _new_board(SIZE)


def _persist_best_if_needed() -> None:
    scores = load_highscores()
    key = str(st.session_state.size)
    if st.session_state.score > scores.get(key, 0):
        scores[key] = st.session_state.score
        save_highscores(scores)
        st.session_state.best = st.session_state.score


def _maybe_toast_new_level(old_grid, new_grid_) -> None:
    """Dispara um toast educativo na primeira vez que um nível é alcançado."""
    new_max = max_value(new_grid_)
    old_max = max_value(old_grid)
    if new_max > old_max and new_max not in st.session_state.unlocked:
        st.session_state.unlocked.add(new_max)
        level = get_level(new_max)
        st.toast(f"**{level['name']}** desbloqueada!\n\n{level['desc']}", icon="📊")


def do_move(direction: str) -> None:
    if st.session_state.game_over:
        return

    move_fn, mask_fn = MOVES[direction]
    old_grid = [row[:] for row in st.session_state.grid]
    new_grid_, new_score = move_fn(st.session_state.grid, st.session_state.score)

    if not grids_equal(old_grid, new_grid_):
        # snapshot para permitir desfazer esta jogada
        st.session_state.undo_snapshot = {
            "grid": old_grid,
            "score": st.session_state.score,
            "moves": st.session_state.moves,
            "unlocked": set(st.session_state.unlocked),
        }
        _maybe_toast_new_level(old_grid, new_grid_)
        _, merged_mask = mask_fn(old_grid)
        add_random_tile(new_grid_, st.session_state.rng)
        st.session_state.grid = new_grid_
        st.session_state.score = new_score
        st.session_state.moves += 1
        st.session_state.merged_mask = merged_mask
        _persist_best_if_needed()

        if has_won(st.session_state.grid) and not st.session_state.won_shown:
            st.session_state.won_shown = True
            st.balloons()
            st.toast("🏆 Você alcançou MESTRE DAX! Pode continuar jogando.", icon="🎉")

        if not can_move(st.session_state.grid):
            st.session_state.game_over = True
            st.toast("Fim de jogo — sem mais movimentos possíveis.", icon="💀")
    else:
        st.session_state.merged_mask = None


def undo() -> None:
    snap = st.session_state.undo_snapshot
    if snap is None:
        return
    st.session_state.grid = snap["grid"]
    st.session_state.score = snap["score"]
    st.session_state.moves = snap["moves"]
    st.session_state.unlocked = snap["unlocked"]
    st.session_state.merged_mask = None
    st.session_state.undo_snapshot = None
    st.session_state.game_over = False


def restart() -> None:
    _new_board(st.session_state.size)


def change_size(new_size: int) -> None:
    _new_board(new_size)


def toggle_daily() -> None:
    st.session_state.daily_mode = not st.session_state.daily_mode
    if st.session_state.daily_mode:
        seed = date.today().isoformat()
        st.session_state.rng = random.Random(seed)
    else:
        st.session_state.rng = random.Random()
    _new_board(st.session_state.size)


# --------------------------------------------------------------------------
# COMPONENTES DE UI
# --------------------------------------------------------------------------
def render_header() -> None:
    title_col, score_col, best_col = st.columns([2, 1, 1])

    with title_col:
        st.markdown('<p class="game-title">🧮 DAX 2048</p>', unsafe_allow_html=True)
        st.markdown('<p class="game-subtitle">Funda medidas iguais e evolua no DAX</p>', unsafe_allow_html=True)
        badges = []
        if st.session_state.game_over:
            badges.append('<span class="status-badge over">FIM DE JOGO</span>')
        elif has_won(st.session_state.grid):
            badges.append('<span class="status-badge won">🏆 MESTRE DAX</span>')
        if st.session_state.daily_mode:
            badges.append('<span class="status-badge daily">🗓️ Desafio diário</span>')
        if badges:
            st.markdown(" ".join(badges), unsafe_allow_html=True)

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

    st.caption(f"Movimentos: {st.session_state.moves}")
    progress = len(st.session_state.unlocked) / len(LEVEL_ORDER)
    st.progress(min(progress, 1.0), text="Progresso na trilha DAX")


def render_board() -> None:
    mask = st.session_state.merged_mask
    for r, row in enumerate(st.session_state.grid):
        cols = st.columns(st.session_state.size, gap="small")
        for c, (col, value) in enumerate(zip(cols, row)):
            if value == 0:
                bg, fg = EMPTY_TILE_COLORS
                text = ""
                font_size = "1rem"
            else:
                level = get_level(value)
                bg, fg = level["colors"]
                text = level["abbr"]
                font_size = "1.3rem" if len(text) <= 3 else ("1.05rem" if len(text) <= 4 else "0.85rem")
            merged_class = " merged" if mask and mask[r][c] else ""
            col.markdown(
                f'<div class="tile{merged_class}" style="background:{bg}; color:{fg}; '
                f'font-size:{font_size};">{text}</div>',
                unsafe_allow_html=True,
            )


def render_controls() -> None:
    # Botões de movimento (⬆️⬅️➡️⬇️) ficam ocultos via CSS (.st-key-*): eles
    # continuam existindo no DOM só para o streamlit_shortcuts conseguir
    # "clicar" neles quando as setas do teclado são pressionadas. O jogador
    # só enxerga os botões de reiniciar/desfazer.
    with st.container(key="dpad-hidden"):
        st.button("⬆️", key="up", on_click=do_move, args=("up",))
        st.button("⬅️", key="left", on_click=do_move, args=("left",))
        st.button("➡️", key="right", on_click=do_move, args=("right",))
        st.button("⬇️", key="down", on_click=do_move, args=("down",))

    c1, c2 = st.columns(2)
    with c1:
        st.button(
            "↩️ Desfazer",
            key="undo",
            on_click=undo,
            use_container_width=True,
            disabled=st.session_state.undo_snapshot is None,
        )
    with c2:
        st.button("🔄 Reiniciar", key="restart", on_click=restart, use_container_width=True)

    add_shortcuts(
        up="arrowup",
        down="arrowdown",
        left="arrowleft",
        right="arrowright",
        restart="r",
        undo="z",
    )


def render_footer_popovers() -> None:
    """Conteúdo educativo e configurações em popovers: não ocupam espaço fixo na tela."""
    c1, c2, c3 = st.columns(3)

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
        with st.popover("⚙️ Opções", use_container_width=True):
            st.caption("Tamanho do tabuleiro (dificuldade)")
            new_size = st.radio(
                "Tamanho",
                BOARD_SIZES,
                index=BOARD_SIZES.index(st.session_state.size),
                horizontal=True,
                label_visibility="collapsed",
                key="size_radio",
            )
            if new_size != st.session_state.size:
                change_size(new_size)
                st.rerun()

            st.caption("Modo diário (mesmo tabuleiro pra todo mundo hoje)")
            daily_label = "🗓️ Desativar desafio diário" if st.session_state.daily_mode else "🗓️ Jogar desafio de hoje"
            if st.button(daily_label, key="daily_toggle", use_container_width=True):
                toggle_daily()
                st.rerun()

    with c3:
        with st.popover("❓ Como jogar", use_container_width=True):
            st.markdown(
                "- Use as **setas do teclado** (↑ ↓ ← →) para mover as peças.\n"
                "- Peças com a **mesma função DAX** se fundem, virando o próximo nível.\n"
                "- **Z** ou ↩️ desfaz a última jogada (uma vez).\n"
                "- Pressione **R** ou clique em 🔄 para reiniciar.\n"
                "- Chegue ao 🏆 **MESTRE DAX** (peça 2048) — e pode continuar jogando depois!\n"
                "- Em ⚙️ Opções dá pra mudar o tamanho do tabuleiro ou jogar o desafio diário."
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
