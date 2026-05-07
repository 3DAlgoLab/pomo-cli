"""CLI entry point with argparse subcommands."""

import argparse
import sys

try:
    from importlib.metadata import version
    __version__ = version("pomo")
except Exception:
    __version__ = "unknown"

from pomo.art import print_banner
from pomo.config import Config
from pomo.timer import run_session


def main(argv=None):
    """Parse arguments and dispatch to the appropriate session runner."""
    parser = argparse.ArgumentParser(
        prog="pomo", description="SSH-friendly CLI pomodoro timer"
    )
    parser.add_argument("--config", default=None, help="Path to config file")
    parser.add_argument("--version", action="version", version=f"pomo {__version__}")

    subparsers = parser.add_subparsers(dest="command")

    work_parser = subparsers.add_parser("work", help="Run a work session")
    work_parser.add_argument(
        "--minutes", type=float, default=None, help="Override duration"
    )

    break_parser = subparsers.add_parser("break", help="Run a short break")
    break_parser.add_argument(
        "--minutes", type=float, default=None, help="Override duration"
    )

    long_break_parser = subparsers.add_parser(
        "long-break", help="Run a long break"
    )
    long_break_parser.add_argument(
        "--minutes", type=float, default=None, help="Override duration"
    )

    cycle_parser = subparsers.add_parser(
        "cycle", help="Run full pomodoro cycle"
    )
    cycle_parser.add_argument(
        "--minutes", type=float, default=None, help="Override work/break durations"
    )

    subparsers.add_parser("config", help="Print effective configuration")

    # Redirect help/usage output to stdout (argparse defaults to stderr)
    def error_with_stdout(message):
        parser.print_help(sys.stdout)
        sys.exit(2)
    parser.error = error_with_stdout

    args = parser.parse_args(argv)

    if args.command and args.command not in ("config", "cycle"):
        print_banner()
        print()

    cfg = Config(config_path=args.config)

    # Validate negative durations
    minutes = getattr(args, "minutes", None)
    if minutes is not None and minutes < 0:
        parser.error(f"--minutes must be >= 0, got {minutes}")

    if args.command == "work":
        duration = args.minutes if args.minutes is not None else cfg.work
        run_session(label="Work session", duration_minutes=duration)

    elif args.command == "break":
        duration = args.minutes if args.minutes is not None else cfg.short_break
        run_session(label="Short break", duration_minutes=duration)

    elif args.command == "long-break":
        duration = args.minutes if args.minutes is not None else cfg.long_break
        run_session(label="Long break", duration_minutes=duration)

    elif args.command == "cycle":
        n = cfg.sessions_before_long
        work_dur = args.minutes if args.minutes is not None else cfg.work
        short_dur = (
            args.minutes if args.minutes is not None else cfg.short_break
        )
        long_dur = args.minutes if args.minutes is not None else cfg.long_break

        for i in range(n):
            print_banner(i + 1)
            print()
            run_session(label=f"Work session {i + 1}", duration_minutes=work_dur)
            if i < n - 1:
                run_session(
                    label="Short break", duration_minutes=short_dur
                )
        run_session(label="Long break", duration_minutes=long_dur)

    elif args.command == "config":
        print(f"work: {cfg.work} min")
        print(f"short_break: {cfg.short_break} min")
        print(f"long_break: {cfg.long_break} min")
        print(
            f"sessions_before_long: {cfg.sessions_before_long}"
        )

    else:
        parser.print_help()
        sys.exit(2)


if __name__ == "__main__":
    import sys as _sys

    main(_sys.argv[1:])
