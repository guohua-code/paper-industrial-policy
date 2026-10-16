#!/usr/bin/env bash
# 从原始数据一键重跑全部结果。
# 用法：在仓库根目录执行 bash analysis/run_all.sh
set -euo pipefail

cd "$(dirname "$0")/.."

run_stage() {
  local stage="$1"
  local scripts
  scripts=$(find "analysis/${stage}" -maxdepth 1 -name '*.R' ! -name 'dependencies.R' | sort)
  if [ -n "${scripts}" ]; then
    echo "=== ${stage} ==="
    while IFS= read -r script; do
      echo "--- ${script}"
      Rscript "${script}"
    done <<< "${scripts}"
  fi
}

run_stage 01_clean
run_stage 02_build
run_stage 03_analysis

echo "完成，结果见 results/"
