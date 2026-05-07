# pomo-cli2 — SSH-Friendly CLI Pomodoro Timer

## Overview

A minimal, SSH-friendly CLI pomodoro timer. Single-line countdown with `\r`, audible bell on session end, TOML config file support.

## Commands

| Command | Description |
|---------|-------------|
| `pomo work` | Run a work session (default 25 min) |
| `pomo break` | Run a short break session (default 5 min) |
| `pomo long-break` | Run a long break session (default 15 min) |
| `pomo cycle` | Run full pomodoro cycle: N work sessions with short breaks, ending with long break |
| `pomo config` | Print current effective configuration |

### CLI Flags

- `pomo work --minutes N` — override work duration
- `pomo break --minutes N` — override short break duration
- `pomo long-break --minutes N` — override long break duration
- `pomo --config /path/to/file` — custom config file path (any subcommand)

## Configuration

### Default Values

| Setting | Default |
|---------|---------|
| work | 25 minutes |
| short_break | 5 minutes |
| long_break | 15 minutes |
| sessions_before_long | 4 |

### Config File

Location: `~/.config/pomo-cli2/config.toml`

```toml
[session]
work = 25
short_break = 5
long_break = 15
sessions_before_long = 4
```

Priority (lowest to highest): defaults → config file → CLI flags.

## Timer Behavior

### Countdown Display
- Single-line output updated every second using `\r` (carriage return)
- Format: `"{label}: {MM:SS} remaining"` (e.g., `"Work session: 24:59 remaining"`)
- No curses, no full TUI — pure carriage-return overwrite

### Milestone Messages
- Every 5 minutes elapsed, print a milestone message on its own line before resuming the countdown:
  - `"[Milestone] 10 minutes remaining"` (when 10 min left, i.e., 5 min elapsed for a 15-min session)
  - General format: `"[Milestone] {remaining_minutes} minutes remaining"`

### Session End
- Print audible bell via `echo -e "\a"` (verified working over user's SSH)
- Print summary line: `"Session complete! {label} — {duration} min."`
- Exit with code 0

### Signal Handling
- SIGINT (Ctrl+C): immediate abort, print `"Session aborted. Elapsed: {MM:SS}"`, exit code 1

## Cycle Command

The `cycle` command runs a full pomodoro cycle automatically:

```
work → short_break → work → short_break → ... → work → long_break
```

- Number of work sessions determined by `sessions_before_long` config (default: 4)
- Short breaks between each work session
- Long break after the final work session
- Each sub-session shows its own countdown and end notification

## Project Structure

```
pomo-cli2/
├── pyproject.toml
├── src/
│   └── pomo/
│       ├── __init__.py
│       ├── cli.py          # argparse entry point + subcommands
│       ├── config.py       # load defaults → config file → CLI flags
│       └── timer.py        # countdown loop, display, bell, milestones
├── tests/
│   ├── test_config.py
│   ├── test_timer.py
│   └── test_cli.py
```

## Technical Decisions

- **Python ≥ 3.11** (for `tomllib` in stdlib)
- **argparse** for CLI parsing (stdlib, zero deps)
- **pytest** for testing (dev dep via uv)
- **time.sleep(1)** loop for countdown — simple blocking approach
- **Entry point:** `[project.scripts] pomo = "pomo.cli:main"`

## Test Cases

### config.py
1. Load defaults when no config file exists
2. Load and parse TOML config file correctly
3. CLI flags override config file values
4. Config file overrides defaults
5. Custom `--config` path loads correct file
6. Missing keys in config fall back to defaults (partial config)
7. Invalid config file path handled gracefully

### timer.py
8. Countdown runs for correct duration (mock time.sleep)
9. Display updates with `\r` each second
10. Milestone messages printed every 5 minutes elapsed
11. Session end prints bell + summary
12. SIGINT aborts with elapsed time and exit code 1
13. Timer handles edge case: 0-minute session (instant complete)
14. Timer handles 1-minute session correctly

### cli.py
15. `pomo work` invokes timer with correct duration from config
16. `pomo break` invokes timer with short_break duration
17. `pomo long-break` invokes timer with long_break duration
18. `pomo --minutes N` overrides duration
19. `pomo cycle` runs full cycle (work → break → work → ... → long break)
20. `pomo config` prints effective configuration
21. Unknown subcommand shows help
