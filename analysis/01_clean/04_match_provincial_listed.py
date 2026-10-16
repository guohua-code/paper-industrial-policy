#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将各批次/省份小巨人名单与 A 股上市公司清单匹配。

用法:
  uv run --python 3.12 --with pandas python analysis/01_clean/04_match_provincial_listed.py

输入:
  data/interim/little_giant_batch6/*.csv        各省小巨人（列含 company_name）
  data/interim/listed_companies_szse_sse.csv    A股清单（company_full_name/stock_name）
输出:
  data/interim/little_giant_batch6/matched_listed.csv
"""
import csv, glob, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))


def norm(s: str) -> str:
    if not s:
        return ""
    s = s.strip()
    # 去掉常见空格/全角空格，统一括号写法，去掉“股份有限公司”等后缀做宽松匹配
    s = s.replace("（", "(").replace("）", ")").replace("　", "").replace(" ", "")
    return s


def core(s: str) -> str:
    s = norm(s)
    for suf in ("股份有限公司", "有限责任公司", "有限公司", "集团有限公司", "集团"):
        if s.endswith(suf):
            s = s[: -len(suf)]
    return s


def load_listed():
    path = os.path.join(ROOT, "data", "interim", "listed_companies_szse_sse.csv")
    firms = []
    with open(path, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            firms.append(r)
    return firms


def main():
    firms = load_listed()
    # 构建两种索引：全称精确、核心名宽松
    by_full = {}
    by_core = {}
    for r in firms:
        full = norm(r.get("company_full_name", ""))
        if full:
            by_full.setdefault(full, r)
        c = core(r.get("company_full_name", ""))
        if c and len(c) >= 4:
            by_core.setdefault(c, r)

    roster = []
    for path in sorted(glob.glob(os.path.join(ROOT, "data/interim/little_giant_batch6/*.csv"))):
        if os.path.basename(path) == "matched_listed.csv":
            continue
        with open(path, encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                roster.append(r)

    print(f"名单合计 {len(roster)} 行，A股公司 {len(firms)} 家")

    seen = set()
    out_rows = []
    for r in roster:
        name = norm(r.get("company_name", ""))
        key = (name, r.get("list_type", ""))
        if not name or key in seen:
            continue
        seen.add(key)
        m = by_full.get(name)
        how = "full"
        if not m:
            m = by_core.get(core(name))
            how = "core" if m else ""
        if m:
            out_rows.append({
                "province": r.get("province", ""),
                "batch": r.get("batch", ""),
                "list_type": r.get("list_type", ""),
                "sequence": r.get("sequence_in_source", ""),
                "company_name": r.get("company_name", ""),
                "match": how,
                "stock_code": m.get("stock_code", ""),
                "stock_name": m.get("stock_name", ""),
                "company_full_name": m.get("company_full_name", ""),
                "exchange": m.get("exchange", ""),
                "market_board": m.get("market_board", ""),
                "industry_name": m.get("industry_name", ""),
                "province_listed": m.get("province", ""),
                "source_file": r.get("source_file", ""),
            })

    out_path = os.path.join(ROOT, "data/interim/little_giant_batch6/matched_listed.csv")
    fields = ["province", "batch", "list_type", "sequence", "company_name", "match",
              "stock_code", "stock_name", "company_full_name", "exchange",
              "market_board", "industry_name", "province_listed", "source_file"]
    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(out_rows)

    # 统计
    from collections import Counter
    by_prov = Counter(x["province"] for x in out_rows)
    by_type = Counter(x["list_type"] for x in out_rows)
    uniq_codes = {x["stock_code"] for x in out_rows}
    print(f"匹配到上市公司记录 {len(out_rows)} 条，去重股票 {len(uniq_codes)} 只")
    print("按省份:", dict(by_prov))
    print("按类型:", dict(by_type))
    print(f"-> {out_path}")


if __name__ == "__main__":
    main()
