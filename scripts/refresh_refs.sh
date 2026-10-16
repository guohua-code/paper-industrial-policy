#!/usr/bin/env bash
# 从本机 Zotero 的 paper-industrial-policy 分类重新导出 refs.bib。
# 前提：Zotero 正在运行，且已安装 Better BibTeX。
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${ROOT}/references/refs.bib"

curl -sS --fail --get --max-time 60 \
  'http://127.0.0.1:23119/better-bibtex/export' \
  --data-urlencode '/library;id:1/collection/paper-industrial-policy.biblatex' \
  -o "${OUT}.tmp"

# Better BibTeX sometimes double-escapes ampersands in journal titles.
perl -0pi -e 's/\\&amp;/\\&/g' "${OUT}.tmp"
mv "${OUT}.tmp" "${OUT}"

echo "已刷新 ${OUT}"
