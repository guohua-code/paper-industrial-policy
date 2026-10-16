#!/usr/bin/env bash
# 从原始数据一键重跑全部结果。
# 用法：在仓库根目录执行 bash analysis/run_all.sh
set -euo pipefail

echo "[1/3] 数据清洗"
# 示例：stata-mp -b do analysis/01_clean/01_xxx.do
# 示例：Rscript analysis/01_clean/01_xxx.R

echo "[2/3] 变量构造"

echo "[3/3] 实证分析"

echo "完成，结果见 results/"
