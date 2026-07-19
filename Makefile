.PHONY: lint test install uninstall

lint:
	uv run ruff check src/ tests/

test:
	uv run pytest tests/ -v

install:
	uv tool install .

uninstall:
	uv tool uninstall pomo
