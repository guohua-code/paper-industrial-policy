#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于本地已解析的第六批省级“小巨人”名单与沪深 A 股公司表，生成：
1. 第六批上市公司匹配快照；
2. 宽松匹配人工核验清单；
3. 数据覆盖核对报告。

该脚本只读取本地文件，不联网下载。
"""

from __future__ import annotations

import csv
import collections
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ROSTER_DIR = ROOT / "data" / "interim" / "little_giant_batch6"
MATCHED_FILE = ROSTER_DIR / "matched_listed.csv"
LISTED_FILE = ROOT / "data" / "interim" / "listed_companies_szse_sse.csv"
PROCESSED_DIR = ROOT / "data" / "processed"

SNAPSHOT_FILE = PROCESSED_DIR / "xiaojuren_batch6_matched_listed_snapshot.csv"
MANUAL_CHECK_FILE = PROCESSED_DIR / "xiaojuren_batch6_match_manual_check.csv"
REPORT_FILE = PROCESSED_DIR / "xiaojuren_batch6_reconciliation.md"

MISSING_REGIONS = [
    "天津市",
    "山西省",
    "福建省",
    "江西省",
    "海南省",
    "西藏自治区",
    "青海省",
    "宁夏回族自治区",
    "新疆维吾尔自治区",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    roster = []
    for path in sorted(ROSTER_DIR.glob("*.csv")):
        if path.name == MATCHED_FILE.name:
            continue
        for row in read_csv(path):
            row["source_csv"] = path.name
            roster.append(row)

    seen: set[tuple[str, str, str]] = set()
    dedup = []
    for row in roster:
        key = (row.get("province", ""), row.get("list_type", ""),
               row.get("company_name", ""))
        if key not in seen:
            seen.add(key)
            dedup.append(row)

    listed = read_csv(LISTED_FILE)
    matched = read_csv(MATCHED_FILE)
    listed_by_code = {row["stock_code"]: row for row in listed}

    grouped: dict[str, list[dict[str, str]]] = collections.defaultdict(list)
    for row in matched:
        grouped[row["stock_code"]].append(row)

    snapshot_fields = [
        "stock_code",
        "stock_name",
        "company_full_name",
        "exchange",
        "market_board",
        "industry_name",
        "province_listed",
        "is_new_batch6",
        "is_batch6_review_passed",
        "policy_provinces",
        "policy_records",
        "match_methods",
    ]

    snapshot = []
    for code in sorted(grouped):
        records = grouped[code]
        listed_row = listed_by_code[code]
        snapshot.append({
            "stock_code": code,
            "stock_name": listed_row["stock_name"],
            "company_full_name": listed_row["company_full_name"],
            "exchange": listed_row["exchange"],
            "market_board": listed_row["market_board"],
            "industry_name": listed_row["industry_name"],
            "province_listed": listed_row["province"],
            "is_new_batch6": "1"
            if any(row["list_type"] == "new" for row in records) else "0",
            "is_batch6_review_passed": "1"
            if any(row["list_type"] == "review_passed" for row in records) else "0",
            "policy_provinces": ";".join(
                sorted({row["province"] for row in records})),
            "policy_records": ";".join(
                f"{row['province']}|{row['list_type']}|{row['company_name']}"
                for row in records
            ),
            "match_methods": ";".join(
                sorted({row["match"] for row in records})),
        })

    write_csv(SNAPSHOT_FILE, snapshot, snapshot_fields)

    manual = []
    for row in matched:
        if row.get("match") != "full":
            manual.append({
                **row,
                "manual_check_status": "pending",
                "check_note": "核心名匹配；需核验企业更名、股改或母子公司关系",
            })
    manual_fields = list(matched[0].keys()) + [
        "manual_check_status",
        "check_note",
    ]
    write_csv(MANUAL_CHECK_FILE, manual, manual_fields)

    new_by = collections.Counter(
        row["province"] for row in dedup if row["list_type"] == "new")
    review_by = collections.Counter(
        row["province"] for row in dedup if row["list_type"] == "review_passed")
    match_by = collections.Counter(row["province"] for row in matched)
    match_type = collections.Counter(row["list_type"] for row in matched)
    board_by = collections.Counter(
        (row["exchange"], row["market_board"]) for row in matched)

    report = []
    report.append("# 第六批小巨人本地数据处理核对报告\n")
    report.append("生成时间：2026-10-19（离线本地处理，未联网下载）\n")
    report.append("## 一、总体结果\n")
    report.append(
        f"- 已解析省级 CSV 原始记录：{len(roster)} 行；"
        f"按省份-类型-企业名称去重后：{len(dedup)} 行。")
    report.append(
        f"- 已解析第六批新增企业：{sum(new_by.values())} 家；"
        f"距公开总数 3012 家还差 {3012 - sum(new_by.values())} 家。")
    report.append(
        f"- 已解析第三批复核通过企业：{sum(review_by.values())} 家。")
    report.append(
        f"- 沪深 A 股上市公司基础表：{len(listed)} 家（不含北交所）。")
    report.append(
        f"- 当前匹配到沪深 A 股记录：{len(matched)} 条；"
        f"不重复股票：{len(grouped)} 只。")
    report.append(
        f"- 其中第六批新增匹配：{match_type['new']} 条；"
        f"复核通过匹配：{match_type['review_passed']} 条。\n")

    report.append("## 二、按省份匹配结果\n")
    report.append("| 省份 | 已解析新增 | 已解析复核 | 当前匹配记录 |")
    report.append("| --- | ---: | ---: | ---: |")
    for province in sorted(set(new_by) | set(review_by) | set(match_by)):
        report.append(
            f"| {province} | {new_by[province]} | "
            f"{review_by[province]} | {match_by[province]} |")

    report.append("\n## 三、板块分布\n")
    for (exchange, board), count in sorted(board_by.items()):
        report.append(f"- {exchange} / {board}：{count} 只")

    report.append("\n## 四、尚未解析新增名单的地区\n")
    for region in MISSING_REGIONS:
        report.append(f"- {region}")
    report.append(
        "\n这些地区合计对应新增缺口约 170 家。是否影响实证处理组，"
        "需要结合其中 A 股公司数量判断。\n")

    report.append("## 五、输出文件\n")
    report.append(f"- 统一处理组快照：`{SNAPSHOT_FILE.relative_to(ROOT)}`")
    report.append(
        "- 明细匹配结果："
        "`data/interim/little_giant_batch6/matched_listed.csv`")
    report.append(
        f"- 人工核验清单：`{MANUAL_CHECK_FILE.relative_to(ROOT)}`")
    report.append(
        "- 本报告只基于本地现有文件生成，"
        "不代表第六批最终全国完整匹配结果。\n")

    report.append("## 六、待处理事项\n")
    report.append("1. 补齐 9 个缺失地区或确认其无 A 股直接入选公司。")
    report.append("2. 将当前“第六批截面”扩展为第一至第六批多年度处理状态。")
    report.append("3. 补北交所上市公司、公司曾用名、统一社会信用代码。")
    report.append(f"4. 人工核验 {len(manual)} 条核心名宽松匹配结果。")
    report.append("5. 后续必须处理复核退出、撤销和三年有效期。")

    REPORT_FILE.write_text("\n".join(report), encoding="utf-8")

    print(
        f"roster={len(roster)} dedup={len(dedup)} "
        f"matched={len(matched)} stocks={len(grouped)} "
        f"manual_check={len(manual)}"
    )


if __name__ == "__main__":
    main()
