#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"

python3 -m pytest tests/test_pipeline.py -q --no-header -o addopts=""
python3 -m app.train.cli
