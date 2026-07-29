import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from game.dax_content import DAX_LEVELS, get_level


def test_all_levels_are_powers_of_two():
    for value in DAX_LEVELS:
        assert value > 0 and (value & (value - 1)) == 0


def test_all_levels_have_required_fields():
    required = {"abbr", "name", "desc", "example", "colors"}
    for value, level in DAX_LEVELS.items():
        assert required.issubset(level.keys()), f"Nível {value} incompleto"
        assert level["abbr"], f"Nível {value} sem abreviação"
        assert level["name"], f"Nível {value} sem nome"


def test_get_level_known_value():
    level = get_level(32)
    assert level["name"] == "CALCULATE"


def test_get_level_unknown_value_falls_back_gracefully():
    level = get_level(4096)
    assert level["abbr"] == "4096"
    assert "avançado" in level["desc"].lower()


def test_final_level_is_win_tile():
    assert DAX_LEVELS[2048]["name"] == "MESTRE DAX"
