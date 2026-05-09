"""Tests for config.py (spec cases 1–7).

Verifies default loading, TOML parsing, CLI flag overrides, partial configs,
custom paths, and graceful error handling.
"""

from textwrap import dedent


# ── imports under test ────────────────────────────────────────────────
from pomo.config import Config


# ── helpers ───────────────────────────────────────────────────────────

DEFAULT_CONFIG = {
    "work": 25,
    "short_break": 5,
    "long_break": 15,
    "sessions_before_long": 4,
}

FULL_TOML = dedent("""\
[session]
work = 30
short_break = 7
long_break = 20
sessions_before_long = 6
""")

PARTIAL_TOML = dedent("""\
[session]
work = 40
""")


# ── case 1: Load defaults when no config file exists ─────────────────

def test_defaults_when_no_config_file(tmp_path, monkeypatch):
    """Case 1 — defaults returned when ~/.config/pomo-cli2/config.toml is absent."""
    # Place a fresh home dir with no pomo-cli2 folder
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    monkeypatch.setenv("HOME", str(fake_home))

    cfg = Config(config_path=None)
    assert cfg.work == DEFAULT_CONFIG["work"]
    assert cfg.short_break == DEFAULT_CONFIG["short_break"]
    assert cfg.long_break == DEFAULT_CONFIG["long_break"]
    assert cfg.sessions_before_long == DEFAULT_CONFIG["sessions_before_long"]


# ── case 2: Load and parse TOML config file correctly ────────────────

def test_parse_full_toml_config(tmp_path):
    """Case 2 — all session values loaded from a complete config file."""
    cfg_file = tmp_path / "config.toml"
    cfg_file.write_text(FULL_TOML)

    cfg = Config(config_path=str(cfg_file))
    assert cfg.work == 30
    assert cfg.short_break == 7
    assert cfg.long_break == 20
    assert cfg.sessions_before_long == 6


# ── case 3: CLI flags override config file values ────────────────────

def test_cli_flags_override_config(tmp_path):
    """Case 3 — CLI-provided values take precedence over config file."""
    cfg_file = tmp_path / "config.toml"
    cfg_file.write_text(FULL_TOML)

    cfg = Config(
        config_path=str(cfg_file),
        cli_overrides={"work": 10, "short_break": 3},
    )
    assert cfg.work == 10
    assert cfg.short_break == 3
    # Non-overridden keys still come from config file
    assert cfg.long_break == 20
    assert cfg.sessions_before_long == 6


# ── case 4: Config file overrides defaults ───────────────────────────

def test_config_overrides_defaults(tmp_path):
    """Case 4 — values in config file replace the built-in defaults."""
    cfg_file = tmp_path / "config.toml"
    cfg_file.write_text(FULL_TOML)

    cfg = Config(config_path=str(cfg_file))
    # All values differ from DEFAULT_CONFIG
    assert cfg.work != DEFAULT_CONFIG["work"]
    assert cfg.short_break != DEFAULT_CONFIG["short_break"]
    assert cfg.long_break != DEFAULT_CONFIG["long_break"]
    assert cfg.sessions_before_long != DEFAULT_CONFIG["sessions_before_long"]


# ── case 5: Custom --config path loads correct file ─────────────────

def test_custom_config_path(tmp_path):
    """Case 5 — --config flag points to an arbitrary file that is loaded."""
    nested = tmp_path / "custom" / "my_pomo.toml"
    nested.parent.mkdir()
    nested.write_text(dedent("""\
[session]
work = 50
short_break = 10
long_break = 25
sessions_before_long = 8
"""))

    cfg = Config(config_path=str(nested))
    assert cfg.work == 50
    assert cfg.short_break == 10
    assert cfg.long_break == 25
    assert cfg.sessions_before_long == 8


# ── case 6: Missing keys in config fall back to defaults ─────────────

def test_partial_config_falls_back_to_defaults(tmp_path):
    """Case 6 — only 'work' provided; other keys come from defaults."""
    cfg_file = tmp_path / "config.toml"
    cfg_file.write_text(PARTIAL_TOML)

    cfg = Config(config_path=str(cfg_file))
    assert cfg.work == 40  # from file
    assert cfg.short_break == DEFAULT_CONFIG["short_break"]
    assert cfg.long_break == DEFAULT_CONFIG["long_break"]
    assert cfg.sessions_before_long == DEFAULT_CONFIG["sessions_before_long"]


# ── case 7: Invalid config file path handled gracefully ───────────────

def test_invalid_config_path_graceful(tmp_path):
    """Case 7 — nonexistent or unreadable path falls back to defaults (or raises)."""
    cfg = Config(config_path=str(tmp_path / "nonexistent.toml"))
    # Should fall back to all defaults rather than crash
    assert cfg.work == DEFAULT_CONFIG["work"]
    assert cfg.short_break == DEFAULT_CONFIG["short_break"]
    assert cfg.long_break == DEFAULT_CONFIG["long_break"]
    assert cfg.sessions_before_long == DEFAULT_CONFIG["sessions_before_long"]


# ── case 8: Malformed TOML falls back to defaults ────────────────────

def test_malformed_toml_falls_back_to_defaults(tmp_path):
    """Case 8 — invalid TOML content causes fallback to all defaults."""
    cfg_file = tmp_path / "config.toml"
    cfg_file.write_text("[session\nwork = }not_valid\n")

    cfg = Config(config_path=str(cfg_file))
    assert cfg.work == DEFAULT_CONFIG["work"]
    assert cfg.short_break == DEFAULT_CONFIG["short_break"]
    assert cfg.long_break == DEFAULT_CONFIG["long_break"]
    assert cfg.sessions_before_long == DEFAULT_CONFIG["sessions_before_long"]
