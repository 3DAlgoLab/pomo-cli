"""Countdown timer with milestones, bell, SIGINT handling, and pause (Space)."""

import os
import select
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
    paused = False

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

    old_sigint = signal.signal(signal.SIGINT, sigint_handler)

    # Terminal setup: disable ECHO + ICANON so keystrokes are available
    # immediately via select(), but keep ISIG so Ctrl+C still works.
    _old_tty = None
    _tty_mode = sys.stdin.isatty()
    if _tty_mode:
        _old_tty = termios.tcgetattr(sys.stdin)
        attrs = list(_old_tty)
        attrs[3] &= ~(termios.ECHO | termios.ICANON)  # no echo, no canonical
        termios.tcsetattr(sys.stdin, termios.TCSANOW, attrs)

    def _handle_keypress():
        nonlocal paused
        try:
            key = sys.stdin.read(1)
        except (EOFError, OSError):
            return
        if key == " ":  # space bar toggles pause/resume
            if not paused:
                paused = True
                mm = remaining // 60
                ss = remaining % 60
                print(f"\n[Paused] {mm:02d}:{ss:02d} remaining (Space to resume)")
            else:
                paused = False
                mm = remaining // 60
                ss = remaining % 60
                print(f"\r{label}: {mm:02d}:{ss:02d} remaining", end="", flush=True)
        # Drain any remaining buffered input
        if _tty_mode:
            try:
                while True:
                    r, _, _ = select.select([sys.stdin], [], [], 0)
                    if not r:
                        break
                    sys.stdin.read(1)
            except (ValueError, OSError, EOFError):
                pass

    def _wait_one_second():
        """Wait exactly 1 real second, processing keypresses along the way.

        Uses monotonic clock so keypresses don't speed up the countdown.
        """
        deadline = time.monotonic() + 1.0
        while True:
            left = deadline - time.monotonic()
            if left <= 0:
                return
            if _tty_mode:
                try:
                    ready, _, _ = select.select([sys.stdin], [], [], left)
                except (ValueError, OSError):
                    time.sleep(left)
                    return
                if ready:
                    _handle_keypress()
            else:
                time.sleep(left)
                return

    try:
        while remaining > 0:
            if not paused:
                mm = remaining // 60
                ss = remaining % 60
                line = f"{label}: {mm:02d}:{ss:02d} remaining"
                print(f"\r{_dim(line) if dim else line}", end="", flush=True)

                _wait_one_second()
                elapsed += 1
                remaining -= 1

                # Milestone: every 5 minutes elapsed
                if remaining > 0 and remaining % 300 == 0:
                    msg = f"[Milestone] {remaining // 60} minutes remaining"
                    print(f"\n{_dim(msg)}")
            else:
                # While paused: wait and process keys, don't decrement
                _wait_one_second()

        # Session complete — clear the countdown line first
        print()
        print("\a", end="", flush=True)
        print(f"Session complete! {label} — {duration_minutes:g} min.")
    finally:
        signal.signal(signal.SIGINT, old_sigint)
        # Restore terminal and flush stale keystrokes
        if _old_tty is not None:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, _old_tty)
            termios.tcdrain(sys.stdin)
