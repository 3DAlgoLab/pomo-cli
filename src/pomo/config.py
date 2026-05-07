"""Configuration loader: defaults → TOML file → CLI overrides."""

import tomllib
from pathlib import Path


class Config:
    """Pomodoro configuration with layered priority.

    Priority (lowest to highest): defaults, config file values, CLI overrides.
    """

    DEFAULTS = {
        "work": 25,
        "short_break": 5,
        "long_break": 15,
        "sessions_before_long": 4,
    }

    def __init__(self, config_path=None, cli_overrides=None):
        # Start with defaults
        values = dict(self.DEFAULTS)

        # Load from TOML file (overrides defaults)
        if config_path is None:
            config_path = Path.home() / ".config" / "pomo-cli2" / "config.toml"
        else:
            config_path = Path(config_path)

        try:
            with open(config_path, "rb") as f:
                data = tomllib.load(f)
            if "session" in data:
                values.update(data["session"])
        except (FileNotFoundError, OSError, tomllib.TOMLDecodeError):
            pass

        # Apply CLI overrides (highest priority)
        if cli_overrides:
            values.update(cli_overrides)

        try:
            self.work = int(values["work"])
        except (ValueError, TypeError):
            self.work = self.DEFAULTS["work"]

        try:
            self.short_break = int(values["short_break"])
        except (ValueError, TypeError):
            self.short_break = self.DEFAULTS["short_break"]

        try:
            self.long_break = int(values["long_break"])
        except (ValueError, TypeError):
            self.long_break = self.DEFAULTS["long_break"]

        try:
            self.sessions_before_long = int(values["sessions_before_long"])
        except (ValueError, TypeError):
            self.sessions_before_long = self.DEFAULTS["sessions_before_long"]
