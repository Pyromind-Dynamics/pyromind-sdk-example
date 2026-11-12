#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASKS_DIR="${DEEPSWE_TASKS:-/workspace/datasets/deep-swe/tasks}"
DATASET_DIR="$(dirname "${TASKS_DIR}")"
REVISION="${DEEPSWE_DATASET_REVISION:-0b9fabbb63b9104d678fe965e1632f2dd9eaa2ea}"

# Isolate Pier's dependencies from the existing minisweBenchmark interpreter.
uv tool install --python 3.12 --upgrade \
  --with 'mini-swe-agent==2.4.6' \
  --with 'litellm[mcp]==1.106.6' \
  --with 'docker>=7.0.0' \
  'datacurve-pier==0.3.1'

if [[ ! -e "${DATASET_DIR}" ]]; then
  mkdir -p "$(dirname "${DATASET_DIR}")"
  git clone --no-checkout https://github.com/datacurve-ai/deep-swe "${DATASET_DIR}"
  git -C "${DATASET_DIR}" checkout --detach "${REVISION}"
elif [[ "$(git -C "${DATASET_DIR}" rev-parse HEAD)" != "${REVISION}" ]]; then
  echo "Dataset revision differs from ${REVISION}; use a separate DEEPSWE_TASKS directory or set DEEPSWE_DATASET_REVISION." >&2
  exit 1
fi

[[ -d "${TASKS_DIR}" ]] || { echo "Missing tasks directory: ${TASKS_DIR}" >&2; exit 1; }
export DEEPSWE_TASKS="${TASKS_DIR}"
"${DEEPSWE_NODE_PYTHON:-/root/pyromind-sdk-example/.venv/bin/python}" \
  "${SCRIPT_DIR}/eval_benchmark.py" --check --num-tasks 113
