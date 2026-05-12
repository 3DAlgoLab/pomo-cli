"""Countdown timer with milestones, bell, and SIGINT handling."""

import os
import signal
import sys
import time
import termios


def _dim(text: str) -> str:
    """Wrap text in ANSI dim escape codes if output supports it."""
    if not sys.stdout.isatty() or os.environ.get("NO_COLOR"):
        return text
    return f"\033[2m{text}\033[0m"


def run_session(label: str, duration_minutes: float, dim: bool = False) -> None:
    """Run a timed session with countdown display.

    Args:
        label: Display name for the session (e.g., 'Work session').
        duration_minutes: Duration in minutes (float).
    """
    total_seconds = int(duration_minutes * 60)
    remaining = total_seconds
    elapsed = 0

    # Edge case: 0-minute session completes instantly
    if total_seconds == 0:
        print("\a", end="", flush=True)
        print(f"Session complete! {label} — {duration_minutes:g} min.")
        return

    def sigint_handler(signum, _frame):
        mm = elapsed // 60
        ss = elapsed % 60
        print(f"\nSession aborted. Elapsed: {mm:02d}:{ss:02d}")
        sys.exit(1)

    old_handler = signal.signal(signal.SIGINT, sigint_handler)
    # Disable terminal echo so random keystrokes don't clutter the display
    _old_tty = None
    if sys.stdin.isatty():
        _old_tty = termios.tcgetattr(sys.stdin)
        attrs = list(_old_tty)
        attrs[3] &= ~termios.ECHO  # turn off ECHO, keep ISIG (Ctrl+C) intact
        termios.tcsetattr(sys.stdin, termios.TCSANOW, attrs)

    try:
        while remaining > 0:
            mm = remaining // 60
            ss = remaining % 60
            line = f"{label}: {mm:02d}:{ss:02d} remaining"
            print(f"\r{_dim(line) if dim else line}", end="", flush=True)

            time.sleep(1)
            elapsed += 1
            remaining -= 1

            # Milestone: every 5 minutes elapsed (remaining is multiple of 300, < total, > 0)
            if remaining > 0 and remaining % 300 == 0:
                msg = f"[Milestone] {remaining // 60} minutes remaining"
                print(f"\n{_dim(msg)}")

        # Session complete — clear the countdown line first
        print()
        print("\a", end="", flush=True)
        print(f"Session complete! {label} — {duration_minutes:g} min.")
    finally:
        signal.signal(signal.SIGINT, old_handler)
        # Restore terminal and flush stale keystrokes
        if _old_tty is not None:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, _old_tty)
            termios.tcdrain(sys.stdin)
