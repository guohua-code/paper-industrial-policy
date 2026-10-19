#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将北京第六批早期解析结果标准化到省级汇总目录。

输入：data/interim/little_giant_batch6_beijing.csv
输出：
  data/interim/little_giant_batch6/beijing_new.csv
  data/interim/little_giant_batch6/beijing_review.csv

只处理本地文件，不联网。
"""

from pathlib import Path
import csv


ROOT = Path(__file__).resolve().parents[2]
IN_FILE = ROOT / "data" / "interim" / "little_giant_batch6_beijing.csv"
OUT_DIR = ROOT / "data" / "interim" / "little_giant_batch6"
FIELDS = [
    "province",
    "batch",
    "list_type",
    "sequence_in_source",
    "company_name",
    "source_file",
]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with IN_FILE.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    outputs = {
        "new": OUT_DIR / "beijing_new.csv",
        "review_passed": OUT_DIR / "beijing_review.csv",
    }

    for list_type, out_file in outputs.items():
        subset = [
            {field: row.get(field, "") for field in FIELDS}
            for row in rows
            if row.get("list_type") == list_type
        ]
        with out_file.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(subset)
        print(f"{out_file.relative_to(ROOT)}: {len(subset)} rows")


if __name__ == "__main__":
    main()
