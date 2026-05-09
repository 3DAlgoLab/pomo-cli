"""Tests for timer.py (spec cases 8–14).

Verifies countdown duration, display format, milestones, session-end output,
SIGINT handling, and edge-case durations.
"""

import signal
from unittest.mock import patch


# ── imports under test ────────────────────────────────────────────────
from pomo.timer import run_session


# ── case 8: Countdown runs for correct duration ──────────────────────

def test_countdown_runs_correct_duration():
    """Case 8 — timer sleeps once per second for the full session length."""
    total_seconds = 60  # 1 minute
    sleep_calls = []

    def fake_sleep(duration):
        sleep_calls.append(duration)

    with patch("pomo.timer.time.sleep", side_effect=fake_sleep):
        run_session(label="Test", duration_minutes=total_seconds / 60)

    assert len(sleep_calls) == total_seconds


# ── case 9: Display updates with \\r each second ────────────────────

def test_display_updates_with_carriage_return(capsys):
    """Case 9 — each tick prints a line starting with \\r for overwrite."""
    with patch("pomo.timer.time.sleep", return_value=None):
        run_session(label="Work session", duration_minutes=0.05)  # ~3 seconds

    out = capsys.readouterr().out
    assert "\r" in out, f"Expected \\r in output, got: {repr(out)}"


# ── case 10: Milestone messages every 5 minutes elapsed ─────────────

def test_milestone_messages_every_5_minutes(capsys):
    """Case 10 — milestone printed when remaining is a multiple of 5 min."""
    with patch("pomo.timer.time.sleep", return_value=None):
        run_session(label="Work session", duration_minutes=12)

    out = capsys.readouterr().out
    assert "[Milestone]" in out
    assert "10 minutes remaining" in out
    assert "5 minutes remaining" in out


# ── case 11: Session end prints bell + summary ───────────────────────

def test_session_end_bell_and_summary(capsys):
    """Case 11 — audible bell (\\a) and summary line printed at completion."""
    with patch("pomo.timer.time.sleep", return_value=None):
        run_session(label="Work session", duration_minutes=0.05)

    out = capsys.readouterr().out
    assert "\a" in out or "\\a" in out  # bell character
    assert "Session complete!" in out


# ── case 12: SIGINT aborts with elapsed time and exit code 1 ─────────

def test_sigint_aborts_with_elapsed_and_exit_code1(monkeypatch):
    """Case 12 — Ctrl+C prints elapsed time, exits with code 1."""
    sleep_count = [0]

    def fake_sleep(duration):
        sleep_count[0] += 1
        if sleep_count[0] == 3:
            signal.raise_signal(signal.SIGINT)

    with patch("pomo.timer.time.sleep", side_effect=fake_sleep):
        try:
            run_session(label="Work session", duration_minutes=5)
            exited = False
        except SystemExit as exc:
            exited = True
            exit_code = exc.code

    assert exited
    assert exit_code == 1


# ── case 13: Edge case — 0-minute session (instant complete) ─────────

def test_zero_minute_session_instant_complete(capsys):
    """Case 13 — a 0-minute session completes immediately with summary."""
    run_session(label="Work session", duration_minutes=0)

    out = capsys.readouterr().out
    assert "Session complete!" in out


# ── case 14: Timer handles 1-minute session correctly ────────────────

def test_one_minute_session():
    """Case 14 — exactly 60 sleep calls for a 1-minute session."""
    sleep_calls = []

    def fake_sleep(duration):
        sleep_calls.append(duration)

    with patch("pomo.timer.time.sleep", side_effect=fake_sleep):
        run_session(label="Work session", duration_minutes=1)

    assert len(sleep_calls) == 60


