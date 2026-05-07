.PHONY: lint test install

lint:
	uv run ruff check src/ tests/

test:
	uv run pytest tests/ -v

install:
	uv tool install .
