"""Tests for cli.py (spec cases 15–21).

Verifies subcommand routing, duration overrides, cycle execution, config
display, and unknown-subcommand behaviour.
"""

from unittest.mock import MagicMock

import pytest

# ── imports under test ────────────────────────────────────────────────
from pomo.cli import main


# ── case 15: `pomo work` invokes timer with correct duration ─────────

def test_work_uses_config_duration(monkeypatch):
    """Case 15 — 'work' subcommand passes work duration from config to timer."""
    run_mock = MagicMock()
    monkeypatch.setattr("pomo.cli.run_session", run_mock)

    main(["work"])

    assert run_mock.call_count == 1
    call_kwargs = run_mock.call_args[1]
    assert call_kwargs["duration_minutes"] == 25  # default work duration
    assert call_kwargs["dim"] is False


# ── case 16: `pomo break` invokes timer with short_break duration ───

def test_break_uses_short_break_duration(monkeypatch):
    """Case 16 — 'break' subcommand passes short_break duration with dim=True."""
    run_mock = MagicMock()
    monkeypatch.setattr("pomo.cli.run_session", run_mock)

    main(["break"])

    assert run_mock.call_count == 1
    call_kwargs = run_mock.call_args[1]
    assert call_kwargs["duration_minutes"] == 5
    assert call_kwargs["dim"] is True


# ── case 17: `pomo long-break` invokes timer with long_break duration ─

def test_long_break_uses_long_break_duration(monkeypatch):
    """Case 17 — 'long-break' subcommand passes long_break duration with dim=True."""
    run_mock = MagicMock()
    monkeypatch.setattr("pomo.cli.run_session", run_mock)

    main(["long-break"])

    assert run_mock.call_count == 1
    call_kwargs = run_mock.call_args[1]
    assert call_kwargs["duration_minutes"] == 15
    assert call_kwargs["dim"] is True


# ── case 18: `pomo --minutes N` overrides duration ──────────────────

def test_minutes_flag_overrides_duration(monkeypatch):
    """Case 18 — --minutes flag on a subcommand sets custom duration."""
    run_mock = MagicMock()
    monkeypatch.setattr("pomo.cli.run_session", run_mock)

    main(["work", "--minutes", "10"])

    assert run_mock.call_count == 1
    call_kwargs = run_mock.call_args[1]
    assert call_kwargs["duration_minutes"] == 10
    assert call_kwargs["dim"] is False


# ── case 19: `pomo cycle` runs full pomodoro cycle ───────────────────

def test_cycle_runs_full_pomodoro_sequence(monkeypatch):
    """Case 19 — 'cycle' runs work→break→work→break→…→long-break."""
    run_mock = MagicMock()
    monkeypatch.setattr("pomo.cli.run_session", run_mock)

    main(["cycle"])

    # Default: 2 rounds of 4 sessions → 8 works, 6 short breaks, 1 long break
    # (the long break separates rounds; none follows the final round)
    assert run_mock.call_count == 15  # 2 * (4 + 3) + 1
    durations = [c[1]["duration_minutes"] for c in run_mock.call_args_list]
    expected = [25, 5, 25, 5, 25, 5, 25, 15, 25, 5, 25, 5, 25, 5, 25]
    assert durations == expected

    # Breaks should have dim=True, work sessions dim=False
    dims = [c[1]["dim"] for c in run_mock.call_args_list]
    expected_dims = [False, True] * 7 + [False]
    assert dims == expected_dims


# ── rounds: the long break only separates rounds ────────────────────

def test_cycle_single_round_has_no_long_break(monkeypatch):
    """--rounds 1 ends on the last work session; no rest before exit."""
    run_mock = MagicMock()
    monkeypatch.setattr("pomo.cli.run_session", run_mock)

    main(["cycle", "--rounds", "1"])

    durations = [c[1]["duration_minutes"] for c in run_mock.call_args_list]
    assert durations == [25, 5, 25, 5, 25, 5, 25]
    labels = [c[1]["label"] for c in run_mock.call_args_list]
    assert "Long break" not in labels


def test_cycle_rounds_from_config_file(tmp_path, monkeypatch):
    """rounds in config.toml drives the cycle length."""
    run_mock = MagicMock()
    monkeypatch.setattr("pomo.cli.run_session", run_mock)
    cfg_path = tmp_path / "cfg.toml"
    cfg_path.write_text("[session]\nrounds = 3\n", encoding="utf-8")

    main(["--config", str(cfg_path), "cycle"])

    # 3 rounds of 4 sessions + 2 separating long breaks
    assert run_mock.call_count == 23
    labels = [c[1]["label"] for c in run_mock.call_args_list]
    assert labels.count("Long break") == 2


def test_cycle_banner_matches_work_session_number(monkeypatch):
    """The tomato count tracks the global work session number, not round position."""
    monkeypatch.setattr("pomo.cli.run_session", MagicMock())
    banners = []
    monkeypatch.setattr("pomo.cli.print_banner", lambda n=1: banners.append(n))

    main(["cycle"])

    assert banners == [1, 2, 3, 4, 5, 6, 7, 8]


def test_cycle_rejects_nonpositive_rounds(capsys):
    """--rounds 0 is a usage error, not a silent no-op."""
    with pytest.raises(SystemExit) as exc_info:
        main(["cycle", "--rounds", "0"])

    assert exc_info.value.code != 0
    assert "usage" in capsys.readouterr().out.lower()


# ── case 20: `pomo config` prints effective configuration ────────────

def test_config_prints_effective_configuration(capsys, monkeypatch):
    """Case 20 — 'config' subcommand prints current settings."""
    # Prevent timer import side-effects
    monkeypatch.setattr("pomo.cli.run_session", MagicMock())

    main(["config"])

    out = capsys.readouterr().out
    assert "work" in out.lower()
    assert "break" in out.lower()


# ── case 21: Unknown subcommand shows help ───────────────────────────

def test_unknown_subcommand_shows_help(capsys, monkeypatch):
    """Case 21 — unrecognized subcommand prints usage and exits non-zero."""
    # Prevent timer import side-effects
    monkeypatch.setattr("pomo.cli.run_session", MagicMock())

    with pytest.raises(SystemExit) as exc_info:
        main(["foobar"])

    assert exc_info.value.code != 0

    out = capsys.readouterr().out
    assert "usage" in out.lower() or "help" in out.lower()
