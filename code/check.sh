#!/usr/bin/env bash
# The code module's one check, per AGENTS.md: no arguments, exit 0 for pass.
# A bare python on Windows may be the wrong interpreter; point PYTHON at the
# project env, or set it once with: git config hooks.python <path>
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-$(git config --get hooks.python || true)}"
exec "${PY:-python}" code/check.py
