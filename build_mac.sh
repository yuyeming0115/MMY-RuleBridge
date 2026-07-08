#!/usr/bin/env bash
# RuleBridge macOS 一键打包入口。
# 直接转发到跨平台 build.py（自动走 macOS 流程）。
set -euo pipefail

cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
  echo "未找到 python3，请先安装 Python 3.11+（建议用 pyenv 或官方安装包）。" >&2
  exit 1
fi

exec python3 build.py --platform mac "$@"
