.PHONY: help install dev test lint type fmt serve clean

help:
	@echo "install dev test lint type fmt serve clean"

install:
	pip install -r requirements.txt

dev:
	pip install -r requirements-dev.txt
	pip install -e .

test:
	pytest -q

lint:
	ruff check .

type:
	mypy aiops_platform

fmt:
	ruff format .

serve:
	python3 -m aiops_platform.app.asgi

clean:
	rm -rf build dist *.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -name "*.pyc" -delete
