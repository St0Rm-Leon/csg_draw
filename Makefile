.PHONY: setup run demo example conflict test lint format

setup:
	uv sync

run:
	uv run python -m examples.basic

demo:
	uv run python -m examples.slice

example:
	uv run python -m examples.shielded

conflict:
	uv run python -m examples.conflict

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .
