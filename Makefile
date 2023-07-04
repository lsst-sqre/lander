.PHONY: help
help:
	@echo "Make command reference"
	@echo "  make init ........ (initialize for development)"

.PHONY: init
init:
	pip install -e ".[dev]"
	pip install tox pre-commit
	pre-commit install
