"""Banner for the pomodoro timer."""

TOMATO = "🍅"
GROUP_SIZE = 4


def format_banner(n: int) -> str:
    """Return n tomatoes, separated by a space every GROUP_SIZE for easy counting."""
    if n <= 0:
        return ""
    rows = [TOMATO * min(GROUP_SIZE, n - i) for i in range(0, n, GROUP_SIZE)]
    return " ".join(rows)


def print_banner(n=1):
    """Print the session banner."""
    print(format_banner(n), end=" ")
