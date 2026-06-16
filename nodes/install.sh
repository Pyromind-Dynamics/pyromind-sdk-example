#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="/workspace/nodes"
RELOAD_URL="${PYROMIND_RELOAD_URL:-https://pre-api.pyromind.ai/api/v1/nodes/reload?allow_delete=true&allow_recreate=true}"

if [[ $# -ge 1 ]]; then
  TOKEN="$1"
else
  TOKEN="${PYROMIND_API_KEY:-${PYROMIND_TOKEN:-}}"
fi

if [[ -z "$TOKEN" ]]; then
  echo "错误: 请设置 PYROMIND_API_KEY 环境变量，或将 token 作为第一个参数传入" >&2
  echo "用法: $0 [token]" >&2
  exit 1
fi

echo ">>> 复制 nodes 到 ${TARGET_DIR} ..."
mkdir -p "${TARGET_DIR}"

if command -v rsync >/dev/null 2>&1; then
  rsync -a --delete --exclude='install.sh' "${SCRIPT_DIR}/" "${TARGET_DIR}/"
else
  find "${TARGET_DIR}" -mindepth 1 -maxdepth 1 ! -name 'install.sh' -exec rm -rf {} +
  for item in "${SCRIPT_DIR}"/*; do
    base="$(basename "${item}")"
    [[ "${base}" == "install.sh" ]] && continue
    cp -R "${item}" "${TARGET_DIR}/"
  done
fi

echo ">>> 调用 nodes reload API ..."
http_code="$(curl -sS -w '%{http_code}' -o /tmp/pyromind_reload_response.txt -X POST "${RELOAD_URL}" \
  -H "Authorization: Bearer ${TOKEN}")"

cat /tmp/pyromind_reload_response.txt
echo

if [[ "${http_code}" -lt 200 || "${http_code}" -ge 300 ]]; then
  echo "错误: reload 请求失败，HTTP ${http_code}" >&2
  exit 1
fi

echo ">>> 安装完成"
